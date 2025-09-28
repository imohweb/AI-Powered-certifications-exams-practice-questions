#!/usr/bin/env python3
"""
Test script to verify multilingual functionality is working correctly.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1/audio"

def test_multilingual_audio():
    """Test basic multilingual audio generation"""
    print("Testing basic multilingual audio generation...")
    
    # Test Spanish
    response = requests.post(
        f"{BASE_URL}/generate/multilingual",
        params={
            "text": "Hola, bienvenido al examen de certificación",
            "language_code": "es", 
            "voice_type": "primary"
        }
    )
    print(f"Spanish audio: {response.status_code} - {response.json()}")
    
    # Test French
    response = requests.post(
        f"{BASE_URL}/generate/multilingual",
        params={
            "text": "Bonjour, bienvenue à l'examen de certification", 
            "language_code": "fr",
            "voice_type": "primary"
        }
    )
    print(f"French audio: {response.status_code} - {response.json()}")
    
    # Test German
    response = requests.post(
        f"{BASE_URL}/generate/multilingual",
        params={
            "text": "Hallo, willkommen zur Zertifizierungsprüfung",
            "language_code": "de",
            "voice_type": "primary" 
        }
    )
    print(f"German audio: {response.status_code} - {response.json()}")


def test_multilingual_question_audio():
    """Test multilingual question audio generation"""
    print("\nTesting multilingual question audio generation...")
    
    # Test Spanish question
    data = {
        "question_text": "¿Cuál es la capital de España?",
        "answers": ["Madrid", "Barcelona", "Valencia", "Sevilla"],
        "language_code": "es"
    }
    response = requests.post(
        f"{BASE_URL}/generate/question/multilingual",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print(f"Spanish question: {response.status_code} - {response.json()}")
    
    # Test French question
    data = {
        "question_text": "Quelle est la capitale de la France?",
        "answers": ["Paris", "Lyon", "Marseille", "Toulouse"], 
        "language_code": "fr"
    }
    response = requests.post(
        f"{BASE_URL}/generate/question/multilingual",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print(f"French question: {response.status_code} - {response.json()}")


def test_multilingual_voices():
    """Test getting multilingual voice information"""
    print("\nTesting multilingual voice information...")
    
    response = requests.get(f"{BASE_URL}/voices/multilingual")
    print(f"Multilingual voices: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Supported languages: {data.get('supported_languages')}")
        print(f"Available voices: {list(data.get('multilingual_voices', {}).keys())}")


if __name__ == "__main__":
    print("Testing multilingual functionality...")
    
    try:
        test_multilingual_audio()
        test_multilingual_question_audio()
        test_multilingual_voices()
        print("\n✅ All multilingual tests completed!")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")