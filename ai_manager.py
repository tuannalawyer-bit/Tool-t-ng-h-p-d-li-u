import os
import sys
import traceback

class AIManager:
    """
    Unified AI Manager Gateway for corporate multi-model orchestration.
    Supports Google Gemini (Cloud), Groq API (Speed Cloud), and Ollama (Offline Local).
    Uses dynamic lazy imports to prevent crashes if dependencies are missing.
    """
    def __init__(self, default_engine="gemini", fallback_enabled=True):
        self.engine = default_engine.lower()
        self.fallback_enabled = fallback_enabled
        self.api_keys = {
            "gemini": os.environ.get("GEMINI_API_KEY", ""),
            "groq": os.environ.get("GROQ_API_KEY", "")
        }
        
    def set_engine(self, engine_name):
        self.engine = engine_name.lower()
        
    def set_api_key(self, service, key):
        self.api_keys[service.lower()] = key

    def ask(self, prompt, model_override=None):
        """
        Executes prompt generations against the currently configured engine.
        If failure occurs and fallback is enabled, automatically shifts to offline Ollama.
        """
        try:
            if self.engine == "gemini":
                return self._call_gemini(prompt, model_override)
            elif self.engine == "groq":
                return self._call_groq(prompt, model_override)
            elif self.engine == "ollama":
                return self._call_ollama(prompt, model_override)
            else:
                raise ValueError(f"Unknown AI Engine: {self.engine}")
        except Exception as e:
            print(f"[AI MANAGER ERROR] Failure in engine '{self.engine}': {e}", file=sys.stderr)
            if self.fallback_enabled and self.engine != "ollama":
                print("Attempting fallback to OFFLINE Ollama model...", file=sys.stderr)
                return self._call_ollama(prompt, model_override)
            raise

    def _call_gemini(self, prompt, model):
        from google import genai
        
        # Use default fast multimodal model if not specified
        selected_model = model if model else "gemini-2.5-flash"
        api_key = self.api_keys["gemini"]
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or keys dict.")
            
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=selected_model,
            contents=prompt,
        )
        return response.text

    def _call_groq(self, prompt, model):
        # Groq uses standard OpenAI compatible endpoints and python library
        from openai import OpenAI
        
        selected_model = model if model else "llama3-8b-8192"
        api_key = self.api_keys["groq"]
        
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment.")
            
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key
        )
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=selected_model,
        )
        return chat_completion.choices[0].message.content

    def _call_ollama(self, prompt, model):
        try:
            import ollama
        except ImportError:
            raise ImportError("The 'ollama' python library is not installed. Run 'pip install ollama'.")
            
        selected_model = model if model else "llama3" # Default standard model
        
        try:
            response = ollama.chat(model=selected_model, messages=[
                {'role': 'user', 'content': prompt}
            ])
            return response['message']['content']
        except Exception as e:
            raise RuntimeError(f"Ollama connection failed. Ensure Ollama desktop app is running. Detail: {e}")

# Quick Test Sandbox Usage
if __name__ == "__main__":
    print("Initializing AI Manager Gateway...")
    ai = AIManager(default_engine="gemini", fallback_enabled=True)
    print("Gateway loaded successfully with robust dynamic imports.")
