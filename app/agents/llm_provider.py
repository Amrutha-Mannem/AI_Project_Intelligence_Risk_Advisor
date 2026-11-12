import os
import json
import re
from typing import Dict, Any, Optional
from app.config import settings


class LLMProvider:
    """
    Unified LLM Provider abstraction supporting:
    1. Google Gemini API (gemini-1.5-flash / gemini-1.5-pro)
    2. OpenAI API (gpt-4o-mini / gpt-4o / compatible local LLM endpoints)
    3. Deterministic Local Heuristic Engine when no external API key is configured.
    """

    def __init__(self):
        self.gemini_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
        self.openai_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY", "")
        self._init_clients()

    def _init_clients(self):
        self.gemini_client = None
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                self.gemini_client = genai.GenerativeModel(settings.gemini_model)
                print("[LLMProvider] Configured Gemini client successfully.")
            except Exception as e:
                print(f"[LLMProvider] Gemini configuration notice: {e}")

    def update_keys(self, gemini_key: Optional[str] = None, openai_key: Optional[str] = None):
        if gemini_key:
            self.gemini_key = gemini_key
            settings.gemini_api_key = gemini_key
        if openai_key:
            self.openai_key = openai_key
            settings.openai_api_key = openai_key
        self._init_clients()

    def get_active_provider_name(self) -> str:
        if self.gemini_client:
            return f"Gemini ({settings.gemini_model})"
        if self.openai_key:
            return f"OpenAI ({settings.openai_model})"
        return "Built-in Local Project Intelligence Engine"

    def generate_text(self, prompt: str, system_instruction: str = "") -> str:
        # 1. Gemini
        if self.gemini_client:
            try:
                full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
                response = self.gemini_client.generate_content(full_prompt)
                return response.text
            except Exception as e:
                print(f"[LLMProvider] Gemini generation error: {e}. Falling back to OpenAI or local.")

        # 2. OpenAI
        if self.openai_key:
            try:
                import httpx
                headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})

                payload = {
                    "model": settings.openai_model,
                    "messages": messages,
                    "temperature": 0.2,
                }
                res = httpx.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30.0)
                if res.status_code == 200:
                    return res.json()["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"[LLMProvider] OpenAI error: {e}. Falling back to local.")

        return ""

    def generate_json(self, prompt: str, system_instruction: str = "") -> Optional[Dict[str, Any]]:
        raw_text = self.generate_text(
            prompt + "\n\nCRITICAL: Respond ONLY with valid, raw JSON (no markdown fences, no explanation).",
            system_instruction=system_instruction,
        )
        if not raw_text:
            return None

        # Clean JSON markdown if wrapped
        cleaned = re.sub(r"^```(?:json)?", "", raw_text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE).strip()

        try:
            return json.loads(cleaned)
        except Exception:
            # Try finding first { and last }
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1:
                try:
                    return json.loads(cleaned[start : end + 1])
                except Exception:
                    pass
        return None
