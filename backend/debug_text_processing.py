#!/usr/bin/env python3
"""
Detailed debugging script for text processing in multilingual audio generation.
"""

import requests
import json

def debug_text_processing():
    """Debug text processing to identify what's causing failures."""
    
    print("🔍 Debugging Text Processing for Multilingual Audio...")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api/v1/audio"
    
    # Test cases with different characteristics
    test_cases = [
        {
            "name": "Simple text",
            "text": "Hello world",
            "language": "en"
        },
        {
            "name": "Text with newline",
            "text": "Hello\nworld",
            "language": "en"
        },
        {
            "name": "Question with options (formatted)",
            "text": "What is Azure?\nA) Cloud platform\nB) Database\nC) Operating system",
            "language": "en"
        },
        {
            "name": "Question without newlines",
            "text": "What is Azure? A) Cloud platform B) Database C) Operating system",
            "language": "en"
        },
        {
            "name": "Spanish with newline",
            "text": "¿Qué es Azure?\nA) Plataforma en la nube\nB) Base de datos",
            "language": "es"
        },
        {
            "name": "Spanish without newlines", 
            "text": "¿Qué es Azure? A) Plataforma en la nube B) Base de datos",
            "language": "es"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        print(f"   Text: '{test_case['text']}'")
        print(f"   Length: {len(test_case['text'])} characters")
        print(f"   Language: {test_case['language']}")
        
        # Show escaped version
        escaped_text = repr(test_case['text'])
        print(f"   Escaped: {escaped_text}")
        
        try:
            response = requests.post(
                f"{base_url}/generate/multilingual",
                params={
                    "text": test_case['text'],
                    "language_code": test_case['language'],
                    "voice_type": "primary"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success: {result.get('audio_url', 'No URL')}")
            else:
                print(f"   ❌ Failed ({response.status_code}): {response.text}")
                
        except Exception as e:
            print(f"   💥 Exception: {e}")
    
    print(f"\n🎯 Text processing debugging completed!")

if __name__ == "__main__":
    debug_text_processing()