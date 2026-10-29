"""AWS Bedrock provider via the Converse API. Supports forced tool use for Anthropic/Nova/Mistral models
and automatic JSON-schema prompt fallback for models that do not support toolChoice (DeepSeek, Qwen, MiniMax, Kimi, NVIDIA)."""
from __future__ import annotations
import json, re, time
from .base import ModelSpec, ProviderError, StructuredResult


def _extract_json_object(text: str) -> dict:
    s = text.strip()
    s = re.sub(r"^```(?:json)?\s*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s*```$", "", s)
    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(s[start : end + 1])
    return json.loads(s)


class BedrockProvider:
    name = "bedrock"

    def __init__(self, region: str = ""):
        import boto3
        from botocore.config import Config
        self._region = region or boto3.Session().region_name
        if not self._region:
            raise ProviderError("No AWS region configured. Set AWS_REGION in .env or run `aws configure`.")
        self._client = boto3.client("bedrock-runtime", region_name=self._region,
                                    config=Config(read_timeout=300, connect_timeout=15, retries={"max_attempts": 3, "mode": "standard"}))

    def _call(self, **kw):
        from botocore.exceptions import BotoCoreError, ClientError
        model = str(kw.get("modelId") or "")
        inf = dict(kw.get("inferenceConfig") or {})
        if any(k in model.lower() for k in ("kimi-k3", "kimi-k2-thinking", "deepseek.r1")):
            inf.pop("temperature", None)
            inf["maxTokens"] = max(int(inf.get("maxTokens", 4000)), 8192)
            kw["inferenceConfig"] = inf
        try:
            return self._client.converse(**kw)
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code", "")
            msg = e.response.get("Error", {}).get("Message", "")[:240]
            if code == "ValidationException" and "temperature" in msg.lower() and "temperature" in inf:
                inf.pop("temperature", None)
                kw["inferenceConfig"] = inf
                return self._client.converse(**kw)
            if code == "AccessDeniedException":
                raise ProviderError(f"Bedrock denied access to model '{model}': {msg} Enable model access in the AWS Bedrock console, or select a different model in Settings.")
            if code == "ValidationException" and "on-demand throughput" in msg:
                raise ProviderError(f"Model '{model}' needs an inference profile ID (e.g. 'au.', 'apac.', or 'global.' prefix). See Settings -> AI Providers.")
            if code in ("ThrottlingException", "ServiceUnavailableException", "ModelTimeoutException", "ModelNotReadyException"):
                raise ProviderError(f"Bedrock temporarily unavailable ({code}). Retry shortly.", retryable=True)
            raise ProviderError(f"Bedrock error {code}: {msg}")
        except BotoCoreError as e:
            raise ProviderError(f"Cannot reach Bedrock ({type(e).__name__}). Check network and AWS credentials.", retryable=True)

    def generate_structured(self, spec, system, messages, schema, tool_name, tool_description) -> StructuredResult:
        t = time.time()
        m_low = (spec.model_id or "").lower()
        no_forced_tool = any(k in m_low for k in ("kimi", "glm", "deepseek", "qwen", "minimax", "nemotron"))
        if spec.structured_mode == "tool" and not no_forced_tool:
            try:
                r = self._call(
                    modelId=spec.model_id,
                    system=[{"text": system}],
                    messages=messages,
                    inferenceConfig={"maxTokens": spec.max_tokens, "temperature": spec.temperature},
                    toolConfig={"tools": [{"toolSpec": {"name": tool_name, "description": tool_description, "inputSchema": {"json": schema}}}],
                                "toolChoice": {"tool": {"name": tool_name}}},
                )
                stop = r.get("stopReason", "")
                if stop == "max_tokens":
                    raise ProviderError(f"Model output was cut off at {spec.max_tokens} tokens. Use a shorter script or raise max_tokens for this task in config/models.json.")
                for block in r["output"]["message"]["content"]:
                    if "toolUse" in block and block["toolUse"]["name"] == tool_name:
                        u = r.get("usage", {})
                        return StructuredResult(data=block["toolUse"]["input"], model_id=spec.model_id, input_tokens=u.get("inputTokens", 0),
                                                output_tokens=u.get("outputTokens", 0), latency_s=round(time.time() - t, 2), raw_stop_reason=stop)
            except ProviderError as e:
                if "toolchoice" not in str(e).lower() and "toolconfig" not in str(e).lower() and "tool" not in str(e).lower():
                    raise

        # Fallback to JSON-schema prompt mode for models that do not support forced toolChoice
        json_sys = (
            f"{system}\n\n"
            f"IMPORTANT: Return ONLY a single valid JSON object matching this JSON Schema (no markdown fences, no commentary):\n"
            f"{json.dumps(schema)}"
        )
        flat_msgs = []
        for m in messages:
            texts = [b["text"] for b in m.get("content", []) if "text" in b]
            if texts:
                flat_msgs.append({"role": m["role"], "content": [{"text": "\n".join(texts)}]})
        r = self._call(
            modelId=spec.model_id,
            system=[{"text": json_sys}],
            messages=flat_msgs or messages,
            inferenceConfig={"maxTokens": spec.max_tokens, "temperature": spec.temperature},
        )
        stop = r.get("stopReason", "")
        text = "".join(b.get("text", "") for b in r["output"]["message"]["content"] if "text" in b)
        u = r.get("usage", {})
        try:
            parsed = _extract_json_object(text)
        except Exception as e:
            raise ProviderError(f"Model '{spec.model_id}' did not return valid JSON ({e}).", retryable=True)
        return StructuredResult(
            data=parsed,
            model_id=spec.model_id,
            input_tokens=u.get("inputTokens", 0),
            output_tokens=u.get("outputTokens", 0),
            latency_s=round(time.time() - t, 2),
            raw_stop_reason=stop,
        )

    def generate_text(self, spec, system, prompt):
        t = time.time()
        r = self._call(modelId=spec.model_id, system=[{"text": system}], messages=[{"role": "user", "content": [{"text": prompt}]}],
                       inferenceConfig={"maxTokens": spec.max_tokens, "temperature": spec.temperature})
        text = "".join(b["text"] for b in r["output"]["message"]["content"] if "text" in b)
        u = r.get("usage", {})
        return text, StructuredResult(data={}, model_id=spec.model_id, input_tokens=u.get("inputTokens", 0),
                                      output_tokens=u.get("outputTokens", 0), latency_s=round(time.time() - t, 2),
                                      raw_stop_reason=r.get("stopReason", ""))
