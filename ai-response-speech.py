import os
import requests
import json
import speech_recognition as sr
import pyttsx3
from typing import Optional

class GPT4AllVoiceAssistant:
    def __init__(self, api_url: str = None):
        # Initialize GPT4ALL API
        self.api_url = api_url or os.environ.get("GPT4ALL_API_URL", "http://localhost:4891/v1")
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.setup_voice()
        
        # Test connection
        self._check_server_connection()

    def setup_voice(self):
        """Configure voice settings"""
        self.tts_engine.setProperty('rate', 150)     # Speed of speech
        self.tts_engine.setProperty('volume', 0.9)   # Volume (0-1)
        
        # Get available voices and set a default one
        voices = self.tts_engine.getProperty('voices')
        if voices:
            self.tts_engine.setProperty('voice', voices[0].id)

    def _check_server_connection(self) -> bool:
        """Check GPT4ALL server connection"""
        try:
            response = requests.get(f"{self.api_url}/models")
            if response.status_code == 200:
                print(f"Successfully connected to GPT4ALL server at {self.api_url}")
                return True
            else:
                raise ConnectionError(f"Failed to connect to GPT4ALL server. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Could not connect to GPT4ALL server at {self.api_url}: {str(e)}")

    def list_all_audio_sources(self):
        """List all audio sources with detailed information"""
        print("\nAvailable Audio Sources:")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            try:
                mic = sr.Microphone(device_index=index)
                with mic as source:
                    # Try to initialize the source
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.1)
                    status = "✓ (Working)"
            except Exception as e:
                status = f"✗ (Error: {str(e)})"
            
            print(f"Index {index}: {name}")
            print(f"   Status: {status}")
            print("   " + "-" * 50)

    def find_stereo_mix(self):
        """Try to find Stereo Mix or similar sources"""
        names = sr.Microphone.list_microphone_names()
        potential_sources = [
            "Stereo Mix", "Stereo", "Mixed", "Mix",
            "What U Hear", "What You Hear",
            "Speakers", "Output"
        ]
        
        found_sources = []
        for index, name in enumerate(names):
            if any(source.lower() in name.lower() for source in potential_sources):
                found_sources.append((index, name))
        
        if found_sources:
            print("\nPotential system audio sources found:")
            for index, name in found_sources:
                print(f"Index {index}: {name}")
        else:
            print("\nNo Stereo Mix or similar sources found.")
        
        return found_sources

    def get_valid_audio_sources(self):
        """Get a list of valid audio sources with proper testing"""
        valid_sources = []
        print("\nChecking available audio sources...")
        
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            try:
                # Try to initialize the microphone
                microphone = sr.Microphone(device_index=index)
                
                # Test if we can actually use it
                with microphone as source:
                    # Quick ambient noise adjustment to test if the source is responsive
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.1)
                    valid_sources.append((index, name))
                    print(f"Index {index}: {name} (✓)")
            except Exception as e:
                print(f"Index {index}: {name} (✗) - {str(e)}")
                continue
        
        return valid_sources

    def test_audio_source(self, device_index: int, duration: int = 5):
        """Test a specific audio source with proper resource handling"""
        if device_index >= len(sr.Microphone.list_microphone_names()):
            print(f"Error: Device index {device_index} is out of range.")
            return False

        source_name = sr.Microphone.list_microphone_names()[device_index]
        print(f"\nTesting source: {source_name}")
        print(f"Listening for {duration} seconds...")

        # Create a new recognizer instance for this test
        test_recognizer = sr.Recognizer()

        try:
            # Explicitly create and manage the microphone resource
            microphone = sr.Microphone(device_index=device_index)
            
            # Use context manager to properly handle the audio source
            with microphone as source:
                print("Adjusting for ambient noise...")
                test_recognizer.adjust_for_ambient_noise(source, duration=1)
                
                print("Listening... (speak now)")
                try:
                    audio = test_recognizer.listen(source, timeout=duration)
                    print("Processing audio...")
                    
                    try:
                        text = test_recognizer.recognize_google(audio)
                        print(f"Recognized: '{text}'")
                        return True
                    except sr.UnknownValueError:
                        print("Audio detected but couldn't be recognized.")
                        return False
                    
                except sr.WaitTimeoutError:
                    print("No audio detected during test.")
                    return False
                    
        except OSError as e:
            print(f"Error: Cannot access audio device (index {device_index})")
            print(f"Details: {str(e)}")
            return False
        except Exception as e:
            print(f"Error testing source: {str(e)}")
            return False

    def setup_audio_source(self):
        """Interactive setup for audio source selection"""
        while True:
            print("\nAudio Source Setup:")
            print("1. List all audio sources")
            print("2. Find Stereo Mix / System audio sources")
            print("3. Test specific source")
            print("4. Select source and continue")
            print("5. Exit")
            
            choice = input("Choose an option (1-5): ")
            
            if choice == "1":
                valid_sources = self.get_valid_audio_sources()
            
            elif choice == "2":
                self.find_stereo_mix()
            
            elif choice == "3":
                try:
                    # Show valid sources first
                    valid_sources = self.get_valid_audio_sources()
                    if not valid_sources:
                        print("No valid audio sources found!")
                        continue
                    
                    index = int(input("Enter source index to test: "))
                    # Validate index
                    if index not in [idx for idx, _ in valid_sources]:
                        print("Invalid source index. Please choose from the list above.")
                        continue
                        
                    self.test_audio_source(index)
                except ValueError:
                    print("Please enter a valid number.")
            
            elif choice == "4":
                try:
                    # Show valid sources first
                    valid_sources = self.get_valid_audio_sources()
                    if not valid_sources:
                        print("No valid audio sources found!")
                        continue
                    
                    index = int(input("Enter source index to use: "))
                    # Validate index
                    if index not in [idx for idx, _ in valid_sources]:
                        print("Invalid source index. Please choose from the list above.")
                        continue
                    
                    self.microphone = sr.Microphone(device_index=index)
                    source_name = sr.Microphone.list_microphone_names()[index]
                    print(f"Selected source: {source_name}")
                    
                    # Test the selected source
                    if self.test_audio_source(index):
                        return True
                    else:
                        print("Source test failed. Please try another source.")
                except ValueError:
                    print("Please enter a valid number.")
                except Exception as e:
                    print(f"Error setting source: {str(e)}")
            
            elif choice == "5":
                return False

    def listen(self) -> str:
        """Listen for voice input and convert to text with proper resource handling"""
        if not hasattr(self, 'microphone'):
            print("No microphone selected. Using default...")
            self.microphone = sr.Microphone()
        
        try:
            with self.microphone as source:
                print("Listening...")
                # Adjust for ambient noise before each listen
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                try:
                    audio = self.recognizer.listen(source, timeout=5)
                    print("Processing speech...")
                    
                    try:
                        text = self.recognizer.recognize_google(audio)
                        print(f"You said: {text}")
                        return text
                    except sr.UnknownValueError:
                        print("Could not understand audio")
                        return ""
                    except sr.RequestError as e:
                        print(f"Could not request results; {e}")
                        return ""
                        
                except sr.WaitTimeoutError:
                    print("No speech detected")
                    return ""
                    
        except Exception as e:
            print(f"Error during listening: {str(e)}")
            return ""

    def speak(self, text: str) -> None:
        """Convert text to speech"""
        try:
            print(f"AI: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Failed to speak: {str(e)}")

    def generate_response(self, prompt: str) -> str:
        """Generate response using GPT4ALL"""
        endpoint = f"{self.api_url}/chat/completions"
        
        params = {
            "model": "gpt4all-j",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 150,
            "stream": False
        }
        
        try:
            response = requests.post(endpoint, json=params)
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                print(f"Error response: {response.text}")
                raise ConnectionError(f"Failed to generate text. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to generate text: {str(e)}")

    def run_interactive(self, voice_input: bool = True):
        """Run interactive session"""
        print("Starting interactive session...")
        print("Speak or type 'quit' to exit")
        
        while True:
            try:
                if voice_input:
                    user_input = self.listen()
                    if not user_input:
                        continue
                else:
                    user_input = input("You: ")
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    self.speak("Goodbye!")
                    break
                
                # Generate and speak response
                response = self.generate_response(user_input)
                self.speak(response)
                
            except Exception as e:
                print(f"Error: {str(e)}")
                continue

def main():
    # Initialize the assistant
    assistant = GPT4AllVoiceAssistant()
    
    # Setup audio source
    if assistant.setup_audio_source():
        # Run the interactive session
        assistant.run_interactive(voice_input=True)
    else:
        print("Audio setup cancelled.")

if __name__ == "__main__":
    main()
