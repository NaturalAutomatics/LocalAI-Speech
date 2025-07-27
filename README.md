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

## Developing New AI Features

### Architecture Overview

The AI assistant uses a modular approach where new capabilities can be added as "features" or "tools" that the AI can invoke based on user requests.

### Adding New Features - Step by Step

#### 1. Create Feature Classes

Create feature classes that inherit from a base `AIFeature` class:

```python
class AIFeature:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def can_handle(self, user_input: str) -> bool:
        """Check if this feature can handle the user input"""
        raise NotImplementedError
    
    def execute(self, user_input: str, **kwargs) -> str:
        """Execute the feature and return result"""
        raise NotImplementedError
```

#### 2. Implement Feature Detection

Use keyword matching or AI-based intent recognition to determine which feature to use:

```python
def detect_intent(self, user_input: str) -> str:
    """Detect user intent from input"""
    # Use GPT4ALL to analyze intent
    intent_prompt = f"Analyze this request and identify the main action: '{user_input}'. Respond with one word: create_file, usb_operation, web_search, etc."
    return self.generate_response(intent_prompt).strip().lower()
```

#### 3. Register and Execute Features

Register features in the main assistant class and route requests:

```python
def __init__(self):
    # ... existing code ...
    self.features = {
        'file_operations': FileOperationsFeature(),
        'usb_operations': USBOperationsFeature(),
        # Add more features here
    }

def process_with_features(self, user_input: str) -> str:
    """Process user input with available features"""
    intent = self.detect_intent(user_input)
    
    for feature in self.features.values():
        if feature.can_handle(user_input):
            return feature.execute(user_input)
    
    # Fallback to regular GPT4ALL response
    return self.generate_response(user_input)
```

#### 4. Feature Development Guidelines

- **Safety First**: Always validate user inputs and file paths
- **Error Handling**: Provide clear error messages and graceful failures
- **Permissions**: Check system permissions before executing operations
- **Logging**: Log all feature executions for debugging
- **User Feedback**: Provide clear status updates during operations

### Example Features to Implement

1. **File Operations**: Create, read, modify, delete files
2. **USB Device Management**: List, mount, unmount USB devices
3. **System Information**: Get CPU, memory, disk usage
4. **Network Operations**: Check connectivity, download files
5. **Process Management**: List, start, stop processes
6. **Calendar Integration**: Schedule events, reminders
7. **Email Operations**: Send emails, check inbox
8. **Web Scraping**: Extract information from websites

### Security Considerations

- **Sandboxing**: Limit file system access to specific directories
- **Input Validation**: Sanitize all user inputs
- **Permission Checks**: Verify user has necessary permissions
- **Audit Trail**: Log all system operations
- **Rate Limiting**: Prevent abuse of system resources

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

### Feature Development Issues

- **Import Errors**: Ensure all required packages are installed
- **Permission Denied**: Run with appropriate system permissions
- **Feature Not Detected**: Check keyword matching in `can_handle()` method