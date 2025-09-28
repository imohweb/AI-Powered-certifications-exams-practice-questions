#!/usr/bin/env python3
"""Test double newlines specifically"""

import requests

# Test the exact text from the failing test case
test_text = "Question: What is the capital of Spain?\n\nOption 1: Madrid\nOption 2: Barcelona\nOption 3: Valencia\nOption 4: Sevilla"

print("Testing text with double newlines:")
print(f"Text: {repr(test_text)}")
print(f"Length: {len(test_text)}")

response = requests.post(
    "http://localhost:8000/api/v1/audio/generate/multilingual",
    params={
        "text": test_text,
        "language_code": "en",
        "voice_type": "primary"
    },
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")