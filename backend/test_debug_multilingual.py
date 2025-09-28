#!/usr/bin/env python3
"""
Test script to debug the multilingual audio generation issue with longer texts.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1/audio"

def test_text_lengths():
    """Test multilingual generation with different text lengths"""
    print("🔍 Testing multilingual audio with different text lengths...")
    
    # Test cases with increasing complexity
    test_cases = [
        {
            "name": "Short text",
            "text": "Hello World",
            "language": "en"
        },
        {
            "name": "Medium text", 
            "text": "What is the capital of Spain? The answer is Madrid.",
            "language": "en"
        },
        {
            "name": "Question format",
            "text": "Question: What is the capital of Spain?\n\nOption 1: Madrid\nOption 2: Barcelona\nOption 3: Valencia\nOption 4: Sevilla",
            "language": "en"
        },
        {
            "name": "Spanish question",
            "text": "Question: ¿Cuál es la capital de España?\n\nOption 1: Madrid\nOption 2: Barcelona\nOption 3: Valencia\nOption 4: Sevilla",
            "language": "es"
        },
        {
            "name": "Very long text",
            "text": "Question: Your company wants to move from maintaining on-premises servers to a solution where Microsoft manages both the hardware and the operating systems. Which cloud service model should you recommend?\n\nOption 1: Infrastructure as a Service (IaaS)\nOption 2: Platform as a Service (PaaS)\nOption 3: Software as a Service (SaaS)\nOption 4: Private Cloud",
            "language": "en"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n  Testing: {test_case['name']}")
        print(f"  Text length: {len(test_case['text'])} characters")
        
        response = requests.post(
            f"{BASE_URL}/generate/multilingual",
            params={
                "text": test_case['text'],
                "language_code": test_case['language'],
                "voice_type": "primary"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Success: {data.get('audio_url')} ({data.get('duration_seconds', 0):.2f}s)")
        else:
            print(f"  ❌ Failed ({response.status_code}): {response.text}")


if __name__ == "__main__":
    print("🔍 Debugging Multilingual Audio Generation Issues...")
    print("=" * 60)
    
    try:
        test_text_lengths()
        print("\n🎯 Text length debugging completed!")
    except Exception as e:
        print(f"\n💥 Error during testing: {e}")