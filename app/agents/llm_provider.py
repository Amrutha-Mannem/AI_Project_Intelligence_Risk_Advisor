import os
import json
import re
from typing import Dict, Any, Optional
from app.config import settings


class LLMProvider:
    """
    Unified LLM Provider — Gemini (primary) → OpenAI → Local heuristic fallback.
    """

    def __init__(self):
        self.gemini_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
        self.openai_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY", "")
        self.gemini_client = None
        self._init_clients()

    def _init_clients(self):
        self.gemini_client = None
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                # Use gemini-1.5-flash (stable name)
                self.gemini_client = genai.GenerativeModel("gemini-1.5-flash")
                print(f"[LLMProvider] Gemini client ready (gemini-1.5-flash).")
            except Exception as e:
                print(f"[LLMProvider] Gemini init error: {e}")
                self.gemini_client = None

    def update_keys(self, gemini_key: Optional[str] = None, openai_key: Optional[str] = None):
        if gemini_key and gemini_key.strip():
            self.gemini_key = gemini_key.strip()
        if openai_key and openai_key.strip():
            self.openai_key = openai_key.strip()
        self._init_clients()

    def get_active_provider_name(self) -> str:
        if self.gemini_client:
            return "Gemini (gemini-1.5-flash)"
        if self.openai_key:
            return "OpenAI (gpt-4o-mini)"
        return "Local Heuristic Engine"

    def is_llm_available(self) -> bool:
        return self.gemini_client is not None or bool(self.openai_key)

    def generate_text(self, prompt: str, system_instruction: str = "") -> str:
        # 1. Gemini
        if self.gemini_client:
            try:
                full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
                response = self.gemini_client.generate_content(full_prompt, request_options={"timeout": 12})
                return response.text.strip()
            except Exception as e:
                print(f"[LLMProvider] Gemini error: {e}")

        # 2. OpenAI
        if self.openai_key:
            try:
                import httpx
                headers = {
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json",
                }
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})
                payload = {"model": "gpt-4o-mini", "messages": messages, "temperature": 0.3}
                res = httpx.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers, json=payload, timeout=45.0,
                )
                if res.status_code == 200:
                    return res.json()["choices"][0]["message"]["content"].strip()
                else:
                    print(f"[LLMProvider] OpenAI HTTP {res.status_code}: {res.text[:200]}")
            except Exception as e:
                print(f"[LLMProvider] OpenAI error: {e}")

        return ""

    def generate_json(self, prompt: str, system_instruction: str = "") -> Optional[Dict[str, Any]]:
        raw = self.generate_text(
            prompt + "\n\nIMPORTANT: Reply ONLY with valid raw JSON. No markdown fences, no explanation.",
            system_instruction=system_instruction,
        )
        if not raw:
            return None
        # Strip ```json ... ``` fences
        cleaned = re.sub(r"^```(?:json)?", "", raw.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            start, end = cleaned.find("{"), cleaned.rfind("}")
            if start != -1 and end != -1:
                try:
                    return json.loads(cleaned[start: end + 1])
                except Exception:
                    pass
        return None
