"""AWS Bedrock provider via the Converse API. Structured output uses forced tool use, which the Anthropic models
accept. Other model families may not support toolChoice; those fail with a clear message rather than silently degrading."""
from __future__ import annotations
import time
from .base import ModelSpec, ProviderError, StructuredResult


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
        try:
            return self._client.converse(**kw)
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code", "")
            msg = e.response.get("Error", {}).get("Message", "")[:200]
            model = kw.get("modelId")
            if code == "AccessDeniedException":
                raise ProviderError(f"Bedrock denied access to model '{model}': {msg} Enable model access in the AWS Bedrock console, or set a different model in config/models.json.")
            if code == "ValidationException" and "on-demand throughput" in msg:
                raise ProviderError(f"Model '{model}' needs an inference profile ID (e.g. 'au.' or 'global.' prefix). See config/models.json.")
            if code in ("ThrottlingException", "ServiceUnavailableException", "ModelTimeoutException", "ModelNotReadyException"):
                raise ProviderError(f"Bedrock temporarily unavailable ({code}). Retry shortly.", retryable=True)
            raise ProviderError(f"Bedrock error {code}: {msg}")
        except BotoCoreError as e:
            raise ProviderError(f"Cannot reach Bedrock ({type(e).__name__}). Check network and AWS credentials.", retryable=True)

    def generate_structured(self, spec, system, messages, schema, tool_name, tool_description) -> StructuredResult:
        if spec.structured_mode != "tool":
            raise ProviderError(f"Unsupported structured_mode '{spec.structured_mode}' for Bedrock.")
        t = time.time()
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
        raise ProviderError("Model did not return structured output (no tool call).", retryable=True)

    def generate_text(self, spec, system, prompt):
        t = time.time()
        r = self._call(modelId=spec.model_id, system=[{"text": system}], messages=[{"role": "user", "content": [{"text": prompt}]}],
                       inferenceConfig={"maxTokens": spec.max_tokens, "temperature": spec.temperature})
        text = "".join(b["text"] for b in r["output"]["message"]["content"] if "text" in b)
        u = r.get("usage", {})
        return text, StructuredResult(data={}, model_id=spec.model_id, input_tokens=u.get("inputTokens", 0),
                                      output_tokens=u.get("outputTokens", 0), latency_s=round(time.time() - t, 2),
                                      raw_stop_reason=r.get("stopReason", ""))
