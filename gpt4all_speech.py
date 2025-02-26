import os
import requests
import json
import subprocess
import platform
from typing import Optional

class GPT4AllSpeechModule:
    def __init__(self, api_url: str = None):
        self.api_url = api_url or os.environ.get("GPT4ALL_API_URL", "http://localhost:4891/v1")
        self._check_server_connection()
    
    def _check_server_connection(self) -> bool:
        try:
            response = requests.get(f"{self.api_url}/models")
            if response.status_code == 200:
                print(f"Successfully connected to GPT4ALL server at {self.api_url}")
                return True
            else:
                raise ConnectionError(f"Failed to connect to GPT4ALL server. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Could not connect to GPT4ALL server at {self.api_url}: {str(e)}")
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        endpoint = f"{self.api_url}/chat/completions"
        
        # Updated parameters for chat completion format
        params = {
            "model": kwargs.get("model", "gpt4all-j"),  # Added default model
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 100),
            "stream": False
        }
        
        try:
            response = requests.post(endpoint, json=params)
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                print(f"Error response: {response.text}")  # Debug information
                raise ConnectionError(f"Failed to generate text. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to generate text: {str(e)}")


    def text_to_speech(self, text: str, output_file: Optional[str] = None) -> str:
        """
        Convert text to speech using local text-to-speech capabilities.
        """
        if output_file is None:
            import tempfile
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
        
        return self._fallback_tts(text, output_file)
    
    def _fallback_tts(self, text: str, output_file: Optional[str] = None) -> str:
        system = platform.system()
        
        if output_file is None:
            import tempfile
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
        
        if system == "Darwin":  # macOS
            try:
                subprocess.call(["say", "-o", output_file, text])
                return output_file
            except Exception as e:
                print(f"Failed to use local TTS: {str(e)}")
                return ""
                
        elif system == "Windows":
            try:
                import win32com.client
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                speaker.Speak(text)
                return ""  # Windows doesn't easily support saving to file without additional libraries
            except Exception as e:
                print(f"Failed to use local TTS: {str(e)}")
                return ""
                
        elif system == "Linux":
            try:
                subprocess.call(["espeak", text, "-w", output_file])
                return output_file
            except Exception as e:
                print(f"Failed to use local TTS: {str(e)}")
                return ""
        
        return ""
    
    def speak(self, text: str) -> None:
        output_file = self.text_to_speech(text)
        
        if output_file:
            self._play_audio(output_file)
            # Clean up the file after playing
            try:
                os.remove(output_file)
            except Exception:
                pass
    
    def _play_audio(self, audio_file: str) -> None:
        system = platform.system()
        
        try:
            if system == "Darwin":  # macOS
                subprocess.call(["afplay", audio_file])
            elif system == "Windows":
                from playsound import playsound
                playsound(audio_file)
            elif system == "Linux":
                subprocess.call(["aplay", audio_file])
        except Exception as e:
            print(f"Failed to play audio: {str(e)}")

# Usage example
if __name__ == "__main__":
    # Initialize the speech module
    speech_module = GPT4AllSpeechModule()
    
    while True:
        try:
            # Get user input
            user_input = input("You: ")
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye!")
                break
            
            # Generate text and speak it
            text = speech_module.generate_text(user_input)
            print(f"AI: {text}")
            speech_module.speak(text)
            
        except Exception as e:
            print(f"Error: {str(e)}")
            continue
