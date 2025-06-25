#!/usr/bin/env python3
"""
Custom LLM wrapper for LangChain that works with local OpenAI-compatible APIs.
"""

from typing import Any, List, Optional, Dict
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
import requests
import json
import toml
from pathlib import Path

# Load configuration
CONFIG = toml.load(Path(__file__).parent.parent.parent / "config.toml")

class CustomOpenAILLM(LLM):
    """
    Custom LLM wrapper for local OpenAI-compatible API endpoints.
    """
    
    api_base: str = ""
    api_key: str = ""
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096
    
    def __init__(self, **kwargs):
        # Load configuration values
        config_values = {
            "api_base": CONFIG["llm"]["base_url"],
            "api_key": CONFIG["llm"]["api_key"],
            "model": CONFIG["llm"]["chat_model"],
            "temperature": CONFIG.get("llm", {}).get("temperature", 0.7),
            "max_tokens": CONFIG.get("llm", {}).get("max_tokens", 4096)
        }
        
        # Merge with any provided kwargs
        config_values.update(kwargs)
        
        # Initialize the parent with all required fields
        super().__init__(**config_values)
    
    @property
    def _llm_type(self) -> str:
        return "custom_openai"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the local OpenAI-compatible API."""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **kwargs
        }
        
        if stop:
            data["stop"] = stop
        
        try:
            print(f"🔧 LLM API Call: {self.model} at {self.api_base}")
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=30  # Reduced timeout to 30 seconds
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "choices" not in result or not result["choices"]:
                raise ValueError("No choices returned from LLM API")
            
            if "message" not in result["choices"][0] or "content" not in result["choices"][0]["message"]:
                raise ValueError("Invalid response format from LLM API")
            
            content = result["choices"][0]["message"]["content"]
            if content is None:
                raise ValueError("LLM returned None content")
            
            return content.strip()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ LLM API Request Error: {e}")
            print(f"   API Base: {self.api_base}")
            print(f"   Model: {self.model}")
            raise RuntimeError(f"LLM API request failed: {e}")
        except Exception as e:
            print(f"❌ LLM Processing Error: {e}")
            print(f"   API Base: {self.api_base}")
            print(f"   Model: {self.model}")
            raise RuntimeError(f"LLM processing failed: {e}")
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {
            "api_base": self.api_base,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
