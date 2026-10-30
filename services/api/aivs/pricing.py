"""AI Model Catalog (AWS Bedrock, excluding OpenAI; Anthropic <= 4.5 + Nova, DeepSeek, MiniMax, Qwen, Mistral, Kimi, Nemotron)
and Official Token Pricing / Cost-Per-Video Calculator.

Official Pricing Sources:
  - AWS Bedrock Pricing: https://aws.amazon.com/bedrock/pricing/
  - Anthropic Claude Pricing: https://docs.anthropic.com/en/docs/about-claude/pricing
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

OFFICIAL_PRICING_LINKS = [
    {"name": "AWS Bedrock Official Pricing", "url": "https://aws.amazon.com/bedrock/pricing/", "note": "Official AWS Bedrock On-Demand & Cross-Region Inference Token Pricing"},
    {"name": "Anthropic Claude Official Pricing", "url": "https://docs.anthropic.com/en/docs/about-claude/pricing", "note": "Official Anthropic Claude 4.5 / 3.5 Model Pricing"},
]

# Catalog of verified AWS Bedrock models in ap-southeast-2 (No OpenAI; Anthropic <= 4.5 + other leading AI models)
# Prices are in USD per 1,000,000 (1M) input and output tokens.
_RAW_CATALOG: list[dict] = [
    # --- Anthropic Claude Suite (Verified HTTP 200 OK on User Account) ---
    {
        "model_id": "au.anthropic.claude-sonnet-4-6",
        "label": "Anthropic Claude Sonnet 4.6 (AU Profile — Latest Flagship)",
        "vendor": "Anthropic",
        "family": "Anthropic Claude (4.6 & 4.5)",
        "region_scope": "AU Cross-Region",
        "input_per_1m_usd": 3.00,
        "output_per_1m_usd": 15.00,
        "recommended_for": ["planning", "script", "repair"],
        "supports_tool_use": True,
        "is_best": True,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "global.anthropic.claude-sonnet-4-6",
        "label": "Anthropic Claude Sonnet 4.6 (Global Profile)",
        "vendor": "Anthropic",
        "family": "Anthropic Claude (4.6 & 4.5)",
        "region_scope": "Global Cross-Region",
        "input_per_1m_usd": 3.00,
        "output_per_1m_usd": 15.00,
        "recommended_for": ["planning", "script"],
        "supports_tool_use": True,
        "is_best": True,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "au.anthropic.claude-opus-4-6-v1",
        "label": "Anthropic Claude Opus 4.6 (AU Profile — Maximum Reasoning)",
        "vendor": "Anthropic",
        "family": "Anthropic Claude (4.6 & 4.5)",
        "region_scope": "AU Cross-Region",
        "input_per_1m_usd": 5.00,
        "output_per_1m_usd": 25.00,
        "recommended_for": ["planning", "script"],
        "supports_tool_use": True,
        "is_best": True,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "global.anthropic.claude-opus-4-6-v1",
        "label": "Anthropic Claude Opus 4.6 (Global Profile)",
        "vendor": "Anthropic",
        "family": "Anthropic Claude (4.6 & 4.5)",
        "region_scope": "Global Cross-Region",
        "input_per_1m_usd": 5.00,
        "output_per_1m_usd": 25.00,
        "recommended_for": ["planning"],
        "supports_tool_use": True,
        "is_best": True,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "au.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "label": "Anthropic Claude Sonnet 4.5 (AU Profile)",
        "vendor": "Anthropic",
        "family": "Anthropic Claude (4.6 & 4.5)",
        "region_scope": "AU Cross-Region",
        "input_per_1m_usd": 3.00,
        "output_per_1m_usd": 15.00,
        "recommended_for": ["planning", "script"],
        "supports_tool_use": True,
        "is_best": True,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "label": "Anthropic Claude Sonnet 4.5 (Global Profile)",
        "vendor": "Anthropic",
        "family": "Anthropic Claude (4.6 & 4.5)",
        "region_scope": "Global Cross-Region",
        "input_per_1m_usd": 3.00,
        "output_per_1m_usd": 15.00,
        "recommended_for": ["planning", "script"],
        "supports_tool_use": True,
        "is_best": True,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "au.anthropic.claude-haiku-4-5-20251001-v1:0",
        "label": "Anthropic Claude Haiku 4.5 (AU Profile — Fast & Low Cost)",
        "vendor": "Anthropic",
        "family": "Anthropic Claude (4.6 & 4.5)",
        "region_scope": "AU Cross-Region",
        "input_per_1m_usd": 1.00,
        "output_per_1m_usd": 5.00,
        "recommended_for": ["analysis", "script", "planning"],
        "supports_tool_use": True,
        "is_best": True,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "global.anthropic.claude-haiku-4-5-20251001-v1:0",
        "label": "Anthropic Claude Haiku 4.5 (Global Profile)",
        "vendor": "Anthropic",
        "family": "Anthropic Claude (4.6 & 4.5)",
        "region_scope": "Global Cross-Region",
        "input_per_1m_usd": 1.00,
        "output_per_1m_usd": 5.00,
        "recommended_for": ["analysis", "script"],
        "supports_tool_use": True,
        "is_best": True,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "global.anthropic.claude-opus-4-5-20251101-v1:0",
        "label": "Anthropic Claude Opus 4.5 (Global Profile — Flagship)",
        "vendor": "Anthropic",
        "family": "Anthropic Claude (4.6 & 4.5)",
        "region_scope": "Global Cross-Region",
        "input_per_1m_usd": 5.00,
        "output_per_1m_usd": 25.00,
        "recommended_for": ["planning"],
        "supports_tool_use": True,
        "is_best": True,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },

    # --- Amazon Nova Suite (Verified HTTP 200 OK on User Account) ---
    {
        "model_id": "apac.amazon.nova-pro-v1:0",
        "label": "Amazon Nova Pro v1 (APAC Multimodal Reasoning)",
        "vendor": "Amazon",
        "family": "Amazon Nova",
        "region_scope": "APAC Cross-Region",
        "input_per_1m_usd": 0.80,
        "output_per_1m_usd": 3.20,
        "recommended_for": ["planning", "script"],
        "supports_tool_use": True,
        "is_best": True,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "apac.amazon.nova-lite-v1:0",
        "label": "Amazon Nova Lite v1 (APAC Ultra-Fast)",
        "vendor": "Amazon",
        "family": "Amazon Nova",
        "region_scope": "APAC Cross-Region",
        "input_per_1m_usd": 0.06,
        "output_per_1m_usd": 0.24,
        "recommended_for": ["analysis", "script"],
        "supports_tool_use": True,
        "is_best": False,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "global.amazon.nova-2-lite-v1:0",
        "label": "Amazon Nova 2 Lite (Global)",
        "vendor": "Amazon",
        "family": "Amazon Nova",
        "region_scope": "Global Cross-Region",
        "input_per_1m_usd": 0.06,
        "output_per_1m_usd": 0.24,
        "recommended_for": ["analysis", "script"],
        "supports_tool_use": True,
        "is_best": False,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "apac.amazon.nova-micro-v1:0",
        "label": "Amazon Nova Micro v1 (APAC Lowest Cost)",
        "vendor": "Amazon",
        "family": "Amazon Nova",
        "region_scope": "APAC Cross-Region",
        "input_per_1m_usd": 0.035,
        "output_per_1m_usd": 0.14,
        "recommended_for": ["analysis"],
        "supports_tool_use": True,
        "is_best": False,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },

    # --- DeepSeek Suite (Verified HTTP 200 OK on User Account) ---
    {
        "model_id": "deepseek.v3.2",
        "label": "DeepSeek V3.2 (Bedrock On-Demand)",
        "vendor": "DeepSeek",
        "family": "DeepSeek",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 0.58,
        "output_per_1m_usd": 1.68,
        "recommended_for": ["planning", "script"],
        "supports_tool_use": False,
        "is_best": True,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "deepseek.v3-v1:0",
        "label": "DeepSeek V3.1 (Bedrock On-Demand)",
        "vendor": "DeepSeek",
        "family": "DeepSeek",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 0.58,
        "output_per_1m_usd": 1.68,
        "recommended_for": ["planning", "script"],
        "supports_tool_use": False,
        "is_best": False,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },

    # --- Z.AI GLM Suite (Verified HTTP 200 OK on User Account) ---
    {
        "model_id": "zai.glm-5",
        "label": "Z.AI GLM 5 (1M Context Director — Low Output Cost)",
        "vendor": "Z.AI (GLM)",
        "family": "Z.AI (GLM)",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 0.50,
        "output_per_1m_usd": 1.50,
        "recommended_for": ["planning", "script", "repair"],
        "supports_tool_use": False,
        "is_best": True,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "zai.glm-4.7",
        "label": "Z.AI GLM 4.7 (Balanced Director)",
        "vendor": "Z.AI (GLM)",
        "family": "Z.AI (GLM)",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 0.35,
        "output_per_1m_usd": 1.10,
        "recommended_for": ["planning", "script"],
        "supports_tool_use": False,
        "is_best": False,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "zai.glm-4.7-flash",
        "label": "Z.AI GLM 4.7 Flash (Ultra-Low Cost Fast Planner)",
        "vendor": "Z.AI (GLM)",
        "family": "Z.AI (GLM)",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 0.07,
        "output_per_1m_usd": 0.25,
        "recommended_for": ["analysis", "script", "planning"],
        "supports_tool_use": False,
        "is_best": False,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },

    # --- NVIDIA Nemotron Suite (Verified HTTP 200 OK on User Account) ---
    {
        "model_id": "nvidia.nemotron-super-3-120b",
        "label": "NVIDIA Nemotron 3 Super 120B (High-Reasoning Director)",
        "vendor": "NVIDIA",
        "family": "NVIDIA",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 0.40,
        "output_per_1m_usd": 1.20,
        "recommended_for": ["planning", "script", "analysis"],
        "supports_tool_use": False,
        "is_best": True,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "nvidia.nemotron-nano-3-30b",
        "label": "NVIDIA Nemotron Nano 3 30B (Fast & Light)",
        "vendor": "NVIDIA",
        "family": "NVIDIA",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 0.12,
        "output_per_1m_usd": 0.36,
        "recommended_for": ["analysis", "script"],
        "supports_tool_use": False,
        "is_best": False,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "nvidia.nemotron-nano-12b-v2",
        "label": "NVIDIA Nemotron Nano 12B v2 (Ultra Fast)",
        "vendor": "NVIDIA",
        "family": "NVIDIA",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 0.10,
        "output_per_1m_usd": 0.30,
        "recommended_for": ["analysis", "script"],
        "supports_tool_use": False,
        "is_best": False,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },

    # --- Moonshot AI Suite (Verified HTTP 200 OK on User Account) ---
    {
        "model_id": "moonshotai.kimi-k2.5",
        "label": "Moonshot AI Kimi K2.5 (Fast Director — Low Cost)",
        "vendor": "Moonshot AI",
        "family": "Moonshot AI",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 0.60,
        "output_per_1m_usd": 2.40,
        "recommended_for": ["planning", "script"],
        "supports_tool_use": False,
        "is_best": True,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "moonshot.kimi-k2-thinking",
        "label": "Moonshot AI Kimi K2 Thinking (Deep Reasoning)",
        "vendor": "Moonshot AI",
        "family": "Moonshot AI",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 0.60,
        "output_per_1m_usd": 2.40,
        "recommended_for": ["planning"],
        "supports_tool_use": False,
        "is_best": False,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },

    # --- Qwen Suite (Verified HTTP 200 OK on User Account) ---
    {
        "model_id": "qwen.qwen3-235b-a22b-2507-v1:0",
        "label": "Qwen3 235B A22B (Bedrock On-Demand)",
        "vendor": "Qwen",
        "family": "Qwen",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 0.45,
        "output_per_1m_usd": 1.80,
        "recommended_for": ["planning", "script"],
        "supports_tool_use": False,
        "is_best": True,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "qwen.qwen3-32b-v1:0",
        "label": "Qwen3 32B Dense (Bedrock On-Demand)",
        "vendor": "Qwen",
        "family": "Qwen",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 0.15,
        "output_per_1m_usd": 0.60,
        "recommended_for": ["script", "analysis"],
        "supports_tool_use": False,
        "is_best": False,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "qwen.qwen3-coder-next",
        "label": "Qwen3 Coder Next (Bedrock On-Demand)",
        "vendor": "Qwen",
        "family": "Qwen",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 0.40,
        "output_per_1m_usd": 1.60,
        "recommended_for": ["planning", "script"],
        "supports_tool_use": False,
        "is_best": False,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },

    # --- MiniMax Suite (Verified HTTP 200 OK on User Account) ---
    {
        "model_id": "minimax.minimax-m2.5",
        "label": "MiniMax M2.5 (Bedrock On-Demand)",
        "vendor": "MiniMax",
        "family": "MiniMax",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 0.30,
        "output_per_1m_usd": 1.20,
        "recommended_for": ["planning", "script"],
        "supports_tool_use": False,
        "is_best": True,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "minimax.minimax-m2.1",
        "label": "MiniMax M2.1 (Bedrock On-Demand)",
        "vendor": "MiniMax",
        "family": "MiniMax",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 0.25,
        "output_per_1m_usd": 1.00,
        "recommended_for": ["script"],
        "supports_tool_use": False,
        "is_best": False,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },

    # --- Mistral AI Suite (Verified HTTP 200 OK on User Account) ---
    {
        "model_id": "mistral.mistral-large-3-675b-instruct",
        "label": "Mistral Large 3 675B Instruct",
        "vendor": "Mistral AI",
        "family": "Mistral AI",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 2.00,
        "output_per_1m_usd": 6.00,
        "recommended_for": ["planning", "script"],
        "supports_tool_use": True,
        "is_best": True,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "mistral.mistral-large-2402-v1:0",
        "label": "Mistral Large 24.02 Instruct",
        "vendor": "Mistral AI",
        "family": "Mistral AI",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 2.00,
        "output_per_1m_usd": 6.00,
        "recommended_for": ["planning", "script"],
        "supports_tool_use": True,
        "is_best": False,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "mistral.ministral-3-14b-instruct",
        "label": "Ministral 14B 3.0",
        "vendor": "Mistral AI",
        "family": "Mistral AI",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 0.10,
        "output_per_1m_usd": 0.30,
        "recommended_for": ["script"],
        "supports_tool_use": False,
        "is_best": False,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },

    # --- OpenAI on Bedrock (Verified HTTP 200 OK on User Account) ---
    {
        "model_id": "openai.gpt-oss-120b-1:0",
        "label": "OpenAI GPT OSS 120B (Bedrock On-Demand)",
        "vendor": "OpenAI",
        "family": "OpenAI",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 0.50,
        "output_per_1m_usd": 1.50,
        "recommended_for": ["planning", "script"],
        "supports_tool_use": True,
        "is_best": True,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
    {
        "model_id": "openai.gpt-oss-20b-1:0",
        "label": "OpenAI GPT OSS 20B (Bedrock On-Demand)",
        "vendor": "OpenAI",
        "family": "OpenAI",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 0.15,
        "output_per_1m_usd": 0.60,
        "recommended_for": ["script", "analysis"],
        "supports_tool_use": True,
        "is_best": False,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },

    # --- Google Gemma on Bedrock (Verified HTTP 200 OK on User Account) ---
    {
        "model_id": "google.gemma-3-27b-it",
        "label": "Google Gemma 3 27B IT",
        "vendor": "Google",
        "family": "Google",
        "region_scope": "On-Demand",
        "input_per_1m_usd": 0.20,
        "output_per_1m_usd": 0.60,
        "recommended_for": ["script"],
        "supports_tool_use": False,
        "is_best": False,
        "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    },
]

BEDROCK_MODEL_CATALOG: list[dict] = [
    {**m, "name": m["label"], "provider": "bedrock", "official_url": m["official_pricing_url"]}
    for m in _RAW_CATALOG
]

MODEL_BY_ID = {m["model_id"]: m for m in BEDROCK_MODEL_CATALOG}


ARCHITECTURE_LAYERS: list[dict] = [
    {
        "layer": 1,
        "title": "Layer 1 — The Director (Orchestrator)",
        "description": "Plans execution order, delegates scene layouts, selects category visual assets, and validates timing.",
        "options": [
            {"id": "global.moonshotai.kimi-k3", "name": "Kimi K3 (1M Context, Always-On Reasoning)", "cost": "$0.60 / $2.50 per 1M", "mode": "bedrock"},
            {"id": "zai.glm-5", "name": "GLM 5 / GLM 5.3 (1M Context, Low Output Cost)", "cost": "$0.50 / $1.50 per 1M", "mode": "bedrock"},
            {"id": "zai.glm-4.7-flash", "name": "GLM 4.7 Flash (Ultra-Low Cost Planner)", "cost": "$0.07 / $0.25 per 1M", "mode": "bedrock"},
            {"id": "nvidia.nemotron-super-3-120b", "name": "NVIDIA Nemotron 3 Super 120B", "cost": "$0.40 / $1.20 per 1M", "mode": "bedrock"},
            {"id": "apac.amazon.nova-pro-v1:0", "name": "Amazon Nova Pro v1", "cost": "$0.80 / $3.20 per 1M", "mode": "bedrock"},
            {"id": "au.anthropic.claude-sonnet-4-5-20250929-v1:0", "name": "Anthropic Claude Sonnet 4.5 (<= 4.5)", "cost": "$3.00 / $15.00 per 1M", "mode": "bedrock"},
            {"id": "au.anthropic.claude-haiku-4-5-20251001-v1:0", "name": "Anthropic Claude Haiku 4.5 (<= 4.5)", "cost": "$1.00 / $5.00 per 1M", "mode": "bedrock"},
            {"id": "deepseek.v3.2", "name": "DeepSeek V3.2", "cost": "$0.58 / $1.68 per 1M", "mode": "bedrock"},
        ],
    },
    {
        "layer": 2,
        "title": "Layer 2 — Visual Scene Generation",
        "description": "Generates cartographic maps, GeoJSON country borders, 2D cartoon characters, SVG icons, stock cutouts, or optional AI scene images.",
        "options": [
            {"id": "local:carto-svg-stock", "name": "Local GeoJSON Map + 2D Cartoon/SVG + Pexels/Wikimedia Stock (Default)", "cost": "$0.00 (Free Local + Stock API)", "mode": "local"},
            {"id": "amazon.nova-canvas-v1:0", "name": "Amazon Nova Canvas (Bedrock Text-to-Image)", "cost": "$0.04 / image", "mode": "bedrock_opt_in"},
            {"id": "stability.sd3-5-large-v1:0", "name": "Stability AI Stable Diffusion 3.5 Large", "cost": "$0.065 / image", "mode": "bedrock_opt_in"},
            {"id": "stability.stable-image-ultra-v1:1", "name": "Stable Image Ultra 1.0 (Photorealistic)", "cost": "$0.08 / image", "mode": "bedrock_opt_in"},
        ],
    },
    {
        "layer": 3,
        "title": "Layer 3 — Motion / Video Generation",
        "description": "Multi-layer keyframe animation, camera pan/zoom rigs, drop shadows, and optional AI video motion.",
        "options": [
            {"id": "local:effectcraft-mcp", "name": "EffectCraft v0.17.0 Headless MCP Multi-Layer Compositor (Default)", "cost": "$0.00 (Local Engine)", "mode": "local"},
            {"id": "amazon.nova-reel-v1:0", "name": "Amazon Nova Reel (Bedrock Text/Image-to-Video)", "cost": "$0.08 / sec", "mode": "bedrock_opt_in"},
            {"id": "luma.ray-v2:0", "name": "Luma AI Ray 2 (Cinematic Video Generation)", "cost": "$0.15 / sec", "mode": "bedrock_opt_in"},
        ],
    },
    {
        "layer": 4,
        "title": "Layer 4 — Narration Script → Audio (Local Default)",
        "description": "Synthesizes broadcast narration with exact word-level timing for scene pacing and captions.",
        "options": [
            {"id": "kokoro:am_michael", "name": "Local Kokoro-82M Neural TTS (Offline Default)", "cost": "$0.00 (Local Offline)", "mode": "local"},
            {"id": "en-US-GuyNeural", "name": "Microsoft Edge Neural TTS", "cost": "$0.00 (Free)", "mode": "local"},
            {"id": "polly:Matthew", "name": "Amazon Polly Neural TTS (SSML)", "cost": "$16.00 / 1M chars (~$0.01/video)", "mode": "bedrock_opt_in"},
            {"id": "mistral.voxtral-small-24b-2507", "name": "Mistral Voxtral Small 24B (Bedrock Audio)", "cost": "$0.20 / $0.60 per 1M", "mode": "bedrock_opt_in"},
        ],
    },
    {
        "layer": 5,
        "title": "Layer 5 — Captions & Final Assembly (Local)",
        "description": "Generates active spoken-word gold highlighted ASS/SRT captions and assembles final MP4 via FilmCraft MCP.",
        "options": [
            {"id": "local:kokoro-ass-filmcraft", "name": "Local Phoneme Word-Timestamps + Active Word-Highlighted .ASS + FilmCraft MCP", "cost": "$0.00 (Local Offline)", "mode": "local"},
        ],
    },
]


def get_model_pricing(model_id: str) -> dict:
    if model_id in MODEL_BY_ID:
        return MODEL_BY_ID[model_id]
    low = (model_id or "").lower()
    if "kimi-k3" in low:
        return {"model_id": model_id, "label": model_id, "vendor": "Moonshot AI", "family": "Kimi K3", "input_per_1m_usd": 0.60, "output_per_1m_usd": 2.50, "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/"}
    if "kimi" in low:
        return {"model_id": model_id, "label": model_id, "vendor": "Moonshot AI", "family": "Kimi K2", "input_per_1m_usd": 0.60, "output_per_1m_usd": 2.40, "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/"}
    if "glm-4.7-flash" in low:
        return {"model_id": model_id, "label": model_id, "vendor": "Z.AI (GLM)", "family": "GLM 4.7", "input_per_1m_usd": 0.07, "output_per_1m_usd": 0.25, "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/"}
    if "glm" in low:
        return {"model_id": model_id, "label": model_id, "vendor": "Z.AI (GLM)", "family": "GLM 5", "input_per_1m_usd": 0.50, "output_per_1m_usd": 1.50, "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/"}
    if "nemotron" in low:
        return {"model_id": model_id, "label": model_id, "vendor": "NVIDIA", "family": "Nemotron 3", "input_per_1m_usd": 0.40, "output_per_1m_usd": 1.20, "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/"}
    if "haiku-4-5" in low:
        return {"model_id": model_id, "label": model_id, "vendor": "Anthropic", "family": "Anthropic Claude", "input_per_1m_usd": 1.00, "output_per_1m_usd": 5.00, "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/"}
    if "haiku" in low:
        return {"model_id": model_id, "label": model_id, "vendor": "Anthropic", "family": "Anthropic Claude", "input_per_1m_usd": 0.25, "output_per_1m_usd": 1.25, "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/"}
    if "opus" in low:
        return {"model_id": model_id, "label": model_id, "vendor": "Anthropic", "family": "Anthropic Claude", "input_per_1m_usd": 5.00, "output_per_1m_usd": 25.00, "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/"}
    if "sonnet" in low:
        return {"model_id": model_id, "label": model_id, "vendor": "Anthropic", "family": "Anthropic Claude", "input_per_1m_usd": 3.00, "output_per_1m_usd": 15.00, "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/"}
    if "nova-pro" in low:
        return {"model_id": model_id, "label": model_id, "vendor": "Amazon", "family": "Amazon Nova", "input_per_1m_usd": 0.80, "output_per_1m_usd": 3.20, "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/"}
    if "nova" in low:
        return {"model_id": model_id, "label": model_id, "vendor": "Amazon", "family": "Amazon Nova", "input_per_1m_usd": 0.06, "output_per_1m_usd": 0.24, "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/"}
    if "minimax" in low:
        return {"model_id": model_id, "label": model_id, "vendor": "MiniMax", "family": "MiniMax", "input_per_1m_usd": 0.30, "output_per_1m_usd": 1.20, "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/"}
    if "deepseek" in low:
        return {"model_id": model_id, "label": model_id, "vendor": "DeepSeek", "family": "DeepSeek", "input_per_1m_usd": 0.58, "output_per_1m_usd": 1.68, "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/"}
    if "fake" in low or "local" in low:
        return {"model_id": model_id, "label": model_id, "vendor": "Local", "family": "Local / Test", "input_per_1m_usd": 0.0, "output_per_1m_usd": 0.0, "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/"}
    return {"model_id": model_id, "label": model_id, "vendor": "AWS Bedrock", "family": "AWS Bedrock", "input_per_1m_usd": 1.00, "output_per_1m_usd": 5.00, "official_pricing_url": "https://aws.amazon.com/bedrock/pricing/"}


def calculate_call_cost(model_id: str, input_tokens: int, output_tokens: int) -> dict:
    info = get_model_pricing(model_id)
    in_rate = float(info["input_per_1m_usd"])
    out_rate = float(info["output_per_1m_usd"])
    in_cost = (max(0, int(input_tokens)) / 1_000_000.0) * in_rate
    out_cost = (max(0, int(output_tokens)) / 1_000_000.0) * out_rate
    label = info.get("label") or info.get("name") or model_id
    return {
        "provider": "AWS Bedrock",
        "model_id": model_id,
        "model_label": label,
        "model_name": label,
        "vendor": info.get("vendor", "AWS Bedrock"),
        "family": info.get("family", "AWS Bedrock"),
        "input_tokens": int(input_tokens),
        "output_tokens": int(output_tokens),
        "total_tokens": int(input_tokens) + int(output_tokens),
        "input_rate_per_1m_usd": in_rate,
        "output_rate_per_1m_usd": out_rate,
        "input_cost_usd": round(in_cost, 6),
        "output_cost_usd": round(out_cost, 6),
        "total_cost_usd": round(in_cost + out_cost, 6),
        "official_pricing_url": info.get("official_pricing_url", "https://aws.amazon.com/bedrock/pricing/"),
        "bedrock_pricing_url": "https://aws.amazon.com/bedrock/pricing/",
    }


def record_token_usage(
    ws_root: Path, stage: str, model_id: str, input_tokens: int, output_tokens: int, latency_s: float = 0.0, attempts: int = 1
) -> dict:
    rep_dir = ws_root / "reports"
    rep_dir.mkdir(parents=True, exist_ok=True)
    path = rep_dir / "token_usage.json"
    existing_calls: list[dict] = []
    if path.is_file():
        try:
            existing_calls = json.loads(path.read_text(encoding="utf-8")).get("calls", [])
        except Exception:
            existing_calls = []

    call = calculate_call_cost(model_id, input_tokens, output_tokens)
    call["stage"] = stage
    call["attempts"] = int(attempts)
    call["latency_s"] = round(float(latency_s), 2)
    call["ts"] = datetime.now(timezone.utc).isoformat()
    existing_calls.append(call)

    report = _summarize_calls(existing_calls)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def _summarize_calls(calls: list[dict]) -> dict:
    tot_in = sum(int(c.get("input_tokens", 0)) for c in calls)
    tot_out = sum(int(c.get("output_tokens", 0)) for c in calls)
    tot_in_cost = sum(float(c.get("input_cost_usd", 0.0)) for c in calls)
    tot_out_cost = sum(float(c.get("output_cost_usd", 0.0)) for c in calls)
    tot_cost = round(tot_in_cost + tot_out_cost, 6)
    models = sorted({c.get("model_id", "") for c in calls if c.get("model_id")})
    real_api = any("fake" not in c.get("model_id", "").lower() for c in calls)
    primary_id = calls[-1].get("model_id") if calls else None
    primary_label = (calls[-1].get("model_label") or calls[-1].get("model_name")) if calls else None
    return {
        "used_api_tokens": bool(calls and real_api),
        "provider": "AWS Bedrock" if real_api else ("Local / Test" if calls else "None"),
        "primary_model_id": primary_id,
        "primary_model_label": primary_label,
        "models_used": models,
        "total_input_tokens": tot_in,
        "total_output_tokens": tot_out,
        "total_tokens": tot_in + tot_out,
        "input_cost_usd": round(tot_in_cost, 6),
        "output_cost_usd": round(tot_out_cost, 6),
        "total_cost_usd": tot_cost,
        "tts_cost_usd": 0.0,
        "rendering_cost_usd": 0.0,
        "calls": calls,
        "official_pricing_links": OFFICIAL_PRICING_LINKS,
    }


def get_project_token_report(ws_root: Path) -> dict:
    """Returns the project's token & cost report, auto-backfilling from director_usage.json / script_generation.json if needed."""
    rep_dir = ws_root / "reports"
    path = rep_dir / "token_usage.json"
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if "primary_model_id" in data:
                return data
            return _summarize_calls(data.get("calls", []))
        except Exception:
            pass

    calls: list[dict] = []
    sg_file = rep_dir / "script_generation.json"
    if sg_file.is_file():
        try:
            sg = json.loads(sg_file.read_text(encoding="utf-8"))
            c = calculate_call_cost(sg.get("model_id", "au.anthropic.claude-haiku-4-5-20251001-v1:0"), sg.get("input_tokens", 0), sg.get("output_tokens", 0))
            c["stage"] = "script_generation"
            c["attempts"] = 1
            c["latency_s"] = sg.get("latency_s", 0.0)
            calls.append(c)
        except Exception:
            pass

    du_file = rep_dir / "director_usage.json"
    if du_file.is_file():
        try:
            du = json.loads(du_file.read_text(encoding="utf-8"))
            c = calculate_call_cost(du.get("model_id", "au.anthropic.claude-sonnet-4-5-20250929-v1:0"), du.get("input_tokens", 0), du.get("output_tokens", 0))
            c["stage"] = "storyboard_planning"
            c["attempts"] = int(du.get("attempts", 1))
            c["latency_s"] = du.get("latency_s", 0.0)
            calls.append(c)
        except Exception:
            pass

    report = _summarize_calls(calls)
    if calls:
        rep_dir.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
