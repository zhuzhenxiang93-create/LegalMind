from __future__ import annotations

import os
from typing import Any


class OpenAICompatibleGenerator:
    """Client for a separately deployed Qwen3.5 or compatible generation service."""

    def __init__(self, config: dict[str, Any]):
        base_url = config.get("base_url") or os.getenv(
            config.get("base_url_env", "GENERATION_BASE_URL")
        )
        api_key = os.getenv(config.get("api_key_env", "GENERATION_API_KEY"), "EMPTY")
        if not base_url:
            raise ValueError(
                "Generation base URL is missing from the configured environment variable"
            )
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        try:
            from openai import OpenAI

            self.client = OpenAI(
                base_url=self.base_url,
                api_key=api_key,
                timeout=float(config.get("timeout_seconds", 120)),
                max_retries=1,
            )
        except ImportError:
            self.client = None
        self.model = config["model"]
        self.max_tokens = int(config.get("max_tokens", 4096))
        self.temperature = float(config.get("temperature", 0.7))
        self.top_p = float(config.get("top_p", 0.8))
        self.top_k = config.get("top_k")
        self.extra_body = {}
        if "enable_thinking" in config:
            self.extra_body["enable_thinking"] = bool(config["enable_thinking"])
        self.response_format = config.get("response_format")
        self.presence_penalty = float(config.get("presence_penalty", 1.5))
        self.timeout_seconds = float(config.get("timeout_seconds", 120))

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "presence_penalty": self.presence_penalty,
        }
        if self.top_k is not None:
            payload["top_k"] = int(self.top_k)
        payload.update(self.extra_body)
        if self.response_format:
            payload["response_format"] = self.response_format
        if self.client is not None:
            options = {"response_format": self.response_format} if self.response_format else {}
            response = self.client.chat.completions.create(
                model=self.model,
                messages=payload["messages"],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                presence_penalty=self.presence_penalty,
                extra_body={
                    **self.extra_body,
                    **({"top_k": int(self.top_k)} if self.top_k is not None else {}),
                },
                **options,
            )
            content = response.choices[0].message.content
        else:
            import requests

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            body = response.json()
            content = body["choices"][0]["message"]["content"]
        if not content:
            raise RuntimeError("Generation service returned an empty response")
        return content
