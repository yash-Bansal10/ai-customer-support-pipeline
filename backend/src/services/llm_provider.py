import os
import time
from typing import Dict, Any, Optional
import json
from dotenv import load_dotenv
from pydantic import ValidationError

# Using google-genai package
from google import genai
from google.genai import types

try:
    from groq import Groq
except ImportError:
    pass # Will be installed by requirements.txt

load_dotenv()

class LLMProvider:
    """I built this abstract interface so I can easily swap out LLM providers later."""
    def generate_json(self, prompt: str, schema: Any) -> Dict[str, Any]:
        raise NotImplementedError

class GeminiProvider(LLMProvider):
    def __init__(self):
        api_keys_str = os.getenv("GEMINI_API_KEY", "")
        self.api_keys = [k.strip() for k in api_keys_str.split(",") if k.strip()]
        if not self.api_keys:
            print("WARNING: GEMINI_API_KEY is not set.")
            self.client = None
        else:
            self.current_key_idx = 0
            self.client = genai.Client(api_key=self.api_keys[self.current_key_idx])
            
        # I default to gemini-1.5-flash because it has a better free-tier rate limit (15 RPM)
        self.model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")
        
    def generate_json(self, prompt: str, schema: Optional[Any] = None) -> Dict[str, Any]:
        """
        I call Gemini here and strictly enforce a JSON response.
        I also added retry logic to handle free-tier rate limits gracefully.
        """
        full_prompt = prompt + "\n\nReturn strictly valid JSON without markdown wrapping."
        retries = 5
        
        for attempt in range(retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                
                text = response.text
                if text.startswith("```json"):
                    text = text[7:]
                if text.endswith("```"):
                    text = text[:-3]
                    
                parsed_dict = json.loads(text.strip())
                if schema:
                    parsed_dict = schema.model_validate(parsed_dict).model_dump()
                return parsed_dict
                
            except Exception as e:
                # If I hit a rate limit (429) or suspension (403), I catch it and handle it gracefully
                err_str = str(e).lower()
                if any(x in err_str for x in ["429", "resource_exhausted", "quota", "403", "permission"]):
                    if len(self.api_keys) > 1:
                        # API Key Pooling: Rotate to the next available key
                        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
                        print(f"Gemini key blocked/exhausted. Rotating to API Key #{self.current_key_idx + 1}...")
                        self.client = genai.Client(api_key=self.api_keys[self.current_key_idx])
                        time.sleep(2) # Tiny backoff to avoid instant block
                    else:
                        wait_time = 65 # Wait 65 seconds to absolutely guarantee the per-minute quota resets
                        print(f"Rate limit hit. I am sleeping for {wait_time}s before retrying (Attempt {attempt+1}/{retries})...")
                        time.sleep(wait_time)
                elif isinstance(e, (json.JSONDecodeError, ValidationError)):
                    print(f"Schema validation failed (Attempt {attempt+1}/{retries}): {e}")
                    time.sleep(1)
                else:
                    print(f"Error calling Gemini API: {e}")
                    raise e
                    
        raise Exception("I hit the maximum retries for the LLM API due to rate limits.")

class GroqProvider(LLMProvider):
    def __init__(self):
        api_keys_str = os.getenv("GROQ_API_KEY", "")
        self.api_keys = [k.strip() for k in api_keys_str.split(",") if k.strip()]
        if not self.api_keys:
            print("WARNING: GROQ_API_KEY is not set.")
            self.client = None
        else:
            self.current_key_idx = 0
            self.client = Groq(api_key=self.api_keys[self.current_key_idx])
            
        # Using Qwen 3.8 27B because it is the only capable free LLM available on your specific API keys
        self.model_name = os.getenv("GROQ_MODEL_NAME", "qwen/qwen3.8-27b")
        
    def generate_json(self, prompt: str, schema: Optional[Any] = None) -> Dict[str, Any]:
        """
        I call Groq here for extremely fast generation during testing.
        """
        full_prompt = prompt + "\n\nReturn strictly valid JSON without markdown wrapping."
        retries = 5
        
        for attempt in range(retries):
            try:
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": full_prompt}],
                    model=self.model_name,
                    response_format={"type": "json_object"}
                )
                
                text = response.choices[0].message.content
                parsed_dict = json.loads(text.strip())
                if schema:
                    parsed_dict = schema.model_validate(parsed_dict).model_dump()
                return parsed_dict
                
            except Exception as e:
                if "429" in str(e):
                    if len(self.api_keys) > 1:
                        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
                        print(f"Groq rate limit hit. Rotating to API Key #{self.current_key_idx + 1}...")
                        self.client = Groq(api_key=self.api_keys[self.current_key_idx])
                        time.sleep(2)
                    else:
                        print(f"Groq rate limit hit. Sleeping for 10s (Attempt {attempt+1}/{retries})...")
                        time.sleep(10)
                elif isinstance(e, (json.JSONDecodeError, ValidationError)):
                    print(f"Schema validation failed (Attempt {attempt+1}/{retries}): {e}")
                    time.sleep(1)
                else:
                    print(f"Error calling Groq API: {e}")
                    raise e
                    
        raise Exception("I hit the maximum retries for the Groq API due to rate limits.")

class FallbackProvider(LLMProvider):
    def __init__(self, primary: LLMProvider, secondary: LLMProvider):
        self.primary = primary
        self.secondary = secondary
        
    def generate_json(self, prompt: str, schema: Optional[Any] = None) -> Dict[str, Any]:
        try:
            return self.primary.generate_json(prompt, schema)
        except Exception as e:
            err_str = str(e).lower()
            if any(x in err_str for x in ["maximum retries", "quota", "rate limit", "429", "403", "permission"]):
                print(f"Primary provider exhausted or blocked ({e}). Falling back to Secondary provider (Groq)...")
                try:
                    return self.secondary.generate_json(prompt, schema)
                except Exception as secondary_e:
                    raise Exception(f"ALL_PROVIDERS_EXHAUSTED: Secondary provider also failed with error: {secondary_e}")
            raise e

def get_llm_provider() -> LLMProvider:
    # I used a factory pattern here so I can easily inject a different provider in the future
    provider = os.getenv("LLM_PROVIDER", "auto").lower()
    
    if provider == "auto":
        # Strategy Pattern: Try Gemini first, fallback to Groq if keys are burned out
        return FallbackProvider(primary=GeminiProvider(), secondary=GroqProvider())
    elif provider == "groq":
        return GroqProvider()
    elif provider == "gemini":
        return GeminiProvider()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
