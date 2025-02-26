# GPT4ALL Speech Module

This module provides an interface to a locally running GPT4ALL server, enabling text generation and speech capabilities in your projects.

## Features

- **Connect to local GPT4ALL server**: Uses the specified GPT4ALL API URL (defaults to http://localhost:4891/v1)
- **Text generation**: Generate text using the GPT4ALL language models
- **Text-to-Speech**: Convert generated text to speech using either:
  - The GPT4ALL API's TTS capabilities (if available)
  - Local text-to-speech fallback mechanisms for macOS, Windows, and Linux

## Requirements

- A locally running [GPT4ALL server](https://docs.gpt4all.io/gpt4all_server.html)
- Python 3.6+
- Required packages: `requests`, `playsound` (for Windows audio playback)
- For Windows TTS fallback: `pywin32`

## Installation

1. Install the required packages:

```bash
pip install requests
# For Windows audio playback
pip install playsound
# For Windows TTS fallback
pip install pywin32
```

2. Copy the `gpt4all_speech.py` file to your project directory.

## Usage

### Basic Usage

```python
from gpt4all_speech import GPT4AllSpeechModule

# Initialize the module (defaults to http://localhost:4891/v1)
speech_module = GPT4AllSpeechModule()

# Generate text from a prompt
response = speech_module.generate_text(
    "Explain quantum computing in simple terms."
)
print(response)

# Convert text to speech and play it
speech_module.speak(response)
```

### Advanced Usage

#### Custom API URL

```python
# Use a custom API URL
speech_module = GPT4AllSpeechModule(api_url="http://192.168.1.100:4891/v1")
```

#### Text Generation with Custom Parameters

```python
response = speech_module.generate_text(
    "Write a haiku about programming.",
    model="gpt4all-j-v1.3-groovy",  # Specify model
    max_tokens=50,                   # Maximum tokens to generate
    temperature=0.9,                 # Higher values make output more random
    top_p=0.95,                      # Nucleus sampling parameter
)
```

#### Save Speech to File

```python
# Convert text to speech and save to a specific file
audio_file = speech_module.text_to_speech(
    "This is a test of the text-to-speech capabilities.", 
    output_file="output.mp3"
)
```

## Environment Variables

- `GPT4ALL_API_URL`: Set this environment variable to override the default API URL

## Notes

- The module attempts to use the GPT4ALL server's API for text-to-speech first
- If the API does not support TTS or fails, it falls back to using local OS capabilities
- On Windows, generated audio files are not automatically saved when using the fallback mechanism

## Troubleshooting

### Connection Issues

If you see a connection error, ensure:
1. The GPT4ALL server is running
2. The API URL is correct
3. No firewalls are blocking the connection

### Audio Playback Issues

- **macOS**: Ensure `afplay` is available (built into macOS)
- **Windows**: Install `playsound` package
- **Linux**: Ensure `aplay` is available (install via `sudo apt-get install alsa-utils` on Debian/Ubuntu)