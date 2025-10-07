#!/usr/bin/env python3
"""
Test script to verify the API endpoints that the frontend uses are working correctly.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1/audio"

def test_frontend_multilingual_question():
    """Test the multilingual question audio endpoint that the frontend now uses"""
    print("Testing frontend multilingual question audio...")
    
    # Simulate what the frontend will send
    question_text = "What is the capital of Spain?"
    answers = ["Madrid", "Barcelona", "Valencia", "Sevilla"]
    
    # Format like the frontend does
    answer_options = []
    for i, answer in enumerate(answers, 1):
        answer_options.append(f"Option {i}: {answer}")
    
    full_question_text = f"Question: {question_text}\n\n" + "\n".join(answer_options)
    
    # Test different languages
    languages = ["en", "es", "fr", "de"]
    
    for lang in languages:
        print(f"\n  Testing {lang.upper()}...")
        
        response = requests.post(
            f"{BASE_URL}/generate/multilingual",
            params={
                "text": full_question_text,
                "language_code": lang,
                "voice_type": "primary"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ {lang.upper()}: Success - {data.get('audio_url')}")
            print(f"     Duration: {data.get('duration_seconds', 0):.2f} seconds")
        else:
            print(f"  ❌ {lang.upper()}: Failed - {response.text}")


def test_frontend_feedback_audio():
    """Test the feedback audio endpoint that the frontend uses"""
    print("\nTesting frontend feedback audio...")
    
    # Test different languages and feedback types
    test_cases = [
        ("Correct! Well done.", True, "en"),
        ("¡Correcto! Bien hecho.", True, "es"),
        ("Incorrect. The correct answer is Madrid.", False, "en"),
        ("Incorrecto. La respuesta correcta es Madrid.", False, "es")
    ]
    
    for feedback_text, is_correct, lang in test_cases:
        response = requests.post(
            f"{BASE_URL}/generate/feedback",
            params={
                "feedback_text": feedback_text,
                "is_correct": is_correct,
                "language_code": lang
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            result_type = "Correct" if is_correct else "Incorrect"
            print(f"  ✅ {lang.upper()} {result_type}: Success - {data.get('audio_url')}")
        else:
            print(f"  ❌ {lang.upper()} {result_type}: Failed - {response.text}")


if __name__ == "__main__":
    print("🧪 Testing Frontend API Endpoints...")
    print("=" * 50)
    
    try:
        test_frontend_multilingual_question()
        test_frontend_feedback_audio()
        print("\n🎉 All frontend API tests completed!")
    except Exception as e:
        print(f"\n💥 Error during testing: {e}")