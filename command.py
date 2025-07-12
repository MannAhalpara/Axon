import requests
import json
import re
import base64
import os

# Gemini AI API configuration
GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
GEMINI_API_KEY = "your valid Gemini API key" 

GEMINI_PROMPT = """
You are an AI assistant tasked with parsing natural language commands for a Jarvis-like voice assistant. Your job is to take a user's spoken input, normalize it, and map it to a predefined command from a command map, even if the input contains typos, misspellings, or speech recognition errors. Use semantic understanding to infer the intended command. The command map is:

{0}

### Instructions:
1. **Input**: The user's spoken or typed command (e.g., "open spotify" or "whooo am i").
2. **Normalization**:
   - Convert the input to lowercase.
   - Remove filler words like "please," "could you," "can you," "would you," "kindly," "a," "the."
   - Remove extra spaces and punctuation.
3. **Command Matching**:
   - Identify the closest matching command from the command map by checking if any phrase in the command map (or its aliases) appears in the normalized input.
   - Handle typos or misspellings (e.g., "whooo am i," "hu am i," "who m i" should map to "who am i") using semantic understanding and context.
   - If no exact match is found, infer the most likely command based on similarity and intent.
4. **Argument Extraction**:
   - Extract any arguments (e.g., app name, search query) that follow the command phrase.
   - For commands like "who am i" or "who are you," no arguments are expected.
5. **Output**:
   - Return a JSON object with:
     - `command`: The matched command (e.g., "open app").
     - `args`: The extracted arguments (e.g., "spotify" for "open spotify").
     - `confidence`: A float (0.0 to 1.0) indicating your confidence in the command match.
   - If no command is recognized, return `command: null` and `args: ""`.

### Examples:
- Input: "open spotify"
  Output: {{"command": "open app", "args": "spotify", "confidence": 0.95}}
- Input: "search YouTube for Python tutorials"
  Output: {{"command": "youtube search", "args": "Python tutorials", "confidence": 0.90}}
- Input: "tell me a joke now"
  Output: {{"command": "joke", "args": "", "confidence": 0.98}}
- Input: "whooo am i"
  Output: {{"command": "who am i", "args": "", "confidence": 0.92}}
- Input: "hu am i"
  Output: {{"command": "who am i", "args": "", "confidence": 0.90}}
- Input: "who m i"
  Output: {{"command": "who am i", "args": "", "confidence": 0.91}}
- Input: "who are you please"
  Output: {{"command": "who are you", "args": "", "confidence": 0.98}}
- Input: "what's the weather"
  Output: {{"command": null, "args": "", "confidence": 0.0}}
- Input: "hey axon ask ai about python"
  Output: {{"command": "ask ai", "args": "about python", "confidence": 0.95}}
- Input: "axon open whatsapp"
  Output: {{"command": "open app", "args": "whatsapp", "confidence": 0.95}}

### Current Input:
{1}

### Command Map (for reference):
{0}

Return the JSON output based on the current input.
"""

def process_command_with_gemini(query, command_map):
    """
    Send the query to Gemini AI to parse and normalize the command.
    Returns (command, args) tuple.
    """
    # Strip "hey axon" or "axon" from the beginning of the query
    normalized_query = normalize_text(query)
    prompt = GEMINI_PROMPT.format(
        json.dumps(command_map, indent=2),
        normalized_query
    )
    try:
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "maxOutputTokens": 200,
                "temperature": 0.7
            }
        }
        response = requests.post(
            f"{GEMINI_API_ENDPOINT}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        if not result.get("candidates"):
            print("Gemini response missing 'candidates'")
            return None, query
        candidate = result["candidates"][0]
        if not candidate.get("content") or not candidate["content"].get("parts"):
            print("Gemini response missing 'content' or 'parts'")
            return None, query
        gemini_output_text = candidate["content"]["parts"][0].get("text", "{}")
        try:
            gemini_output = json.loads(gemini_output_text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', gemini_output_text, re.DOTALL)
            if json_match:
                gemini_output = json.loads(json_match.group(0))
            else:
                print("Failed to parse Gemini response as JSON")
                return None, query
        command = gemini_output.get("command")
        args = gemini_output.get("args", "")
        confidence = gemini_output.get("confidence", 0.0)
        if command and confidence > 0.5:
            return command, args
        else:
            print(f"Gemini failed to recognize command: {gemini_output}")
            return None, query
    except requests.exceptions.RequestException as e:
        print(f"Gemini API request failed: {e}")
        return None, query
    except Exception as e:
        print(f"Error processing command with Gemini: {e}")
        return None, query

def normalize_text(text):
    """
    Normalize the input text by removing prefixes like 'hey axon' or 'axon',
    filler words, punctuation, and extra spaces.
    """
    text = text.lower()
    # Remove "hey axon" or "axon" from the start
    text = re.sub(r'^\s*(hey\s+axon|axon)\s+', '', text)
    # Remove filler words
    text = re.sub(r'\b(a|the|please|could you|can you|would you|kindly|now|for)\b', '', text)
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Remove extra spaces
    return re.sub(r'\s+', ' ', text).strip()

def describe_image_with_gemini(image_path):
    """
    Send an image to Gemini AI to describe its contents.
    Returns a natural language description or None if the request fails.
    """
    try:
        # Read and encode the image as base64
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        # Prompt for image description
        prompt = """
        You are Axon, a voice assistant. Describe the contents of the provided image in a concise, natural, and conversational manner, as if explaining it to a user in real-time. Focus on key elements visible on the screen, such as open applications, text, icons, or general layout. Avoid technical jargon and keep the tone helpful and slightly witty, like Axon from Iron Man. If the image is unclear or empty, say so politely.
        """

        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inlineData": {
                            "mimeType": "image/png",
                            "data": image_data
                        }
                    }
                ]
            }],
            "generationConfig": {
                "maxOutputTokens": 300,
                "temperature": 0.7
            }
        }
        response = requests.post(
            f"{GEMINI_API_ENDPOINT}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        if not result.get("candidates"):
            print("Gemini image response missing 'candidates'")
            return None
        candidate = result["candidates"][0]
        if not candidate.get("content") or not candidate["content"].get("parts"):
            print("Gemini image response missing 'content' or 'parts'")
            return None
        description = candidate["content"]["parts"][0].get("text", "")
        if description:
            return description
        else:
            print("No description returned by Gemini")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Gemini image API request failed: {e}")
        return None
    except Exception as e:
        print(f"Error processing image with Gemini: {e}")
        return None
