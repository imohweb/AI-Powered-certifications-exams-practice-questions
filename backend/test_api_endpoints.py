"""
Test the backend API endpoints to verify 50-question generation is working.
"""

import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:6000"

async def test_certification_api():
    """Test the certification API endpoints."""
    print("🚀 Testing Backend API with 50-Question Generation")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Get available certifications
        print("1. Testing /api/v1/assessments/certifications...")
        try:
            async with session.get(f"{BASE_URL}/api/v1/assessments/certifications") as response:
                if response.status == 200:
                    certifications = await response.json()
                    print(f"   ✅ Found {len(certifications)} certifications")
                    print(f"   Sample: {certifications[0]['code']} - {certifications[0]['title'][:50]}...")
                else:
                    print(f"   ❌ Failed with status {response.status}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: Get a practice assessment (this should generate 50 questions)
        print("\n2. Testing /api/v1/assessments/AZ-900 (50 question generation)...")
        print("   This may take 30-60 seconds for AI generation...")
        try:
            async with session.get(f"{BASE_URL}/api/v1/assessments/AZ-900") as response:
                if response.status == 200:
                    assessment = await response.json()
                    print(f"   ✅ Assessment generated successfully!")
                    print(f"   Title: {assessment['title']}")
                    print(f"   Questions: {len(assessment['questions'])}")
                    print(f"   Duration: {assessment['estimated_duration_minutes']} minutes")
                    
                    # Analyze first question
                    if assessment['questions']:
                        q = assessment['questions'][0]
                        print(f"   Sample Question: {q['text'][:80]}...")
                        print(f"   Answers: {len(q['answers'])}")
                        print(f"   Difficulty: {q['difficulty']}")
                        
                    if len(assessment['questions']) == 50:
                        print("   🎉 Perfect! Generated exactly 50 questions.")
                    else:
                        print(f"   ⚠️  Generated {len(assessment['questions'])} questions instead of 50.")
                        
                else:
                    print(f"   ❌ Failed with status {response.status}")
                    error_text = await response.text()
                    print(f"   Error details: {error_text[:200]}...")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Test speech synthesis endpoint
        print("\n3. Testing /api/v1/audio/synthesize...")
        try:
            audio_request = {
                "text": "Welcome to the Microsoft Azure Fundamentals practice assessment. This is a test of the speech synthesis functionality."
            }
            async with session.post(
                f"{BASE_URL}/api/v1/audio/synthesize", 
                json=audio_request
            ) as response:
                if response.status == 200:
                    audio_response = await response.json()
                    print(f"   ✅ Audio generated successfully!")
                    print(f"   Audio URL: {audio_response['audio_url']}")
                    if 'duration_seconds' in audio_response:
                        print(f"   Duration: {audio_response['duration_seconds']} seconds")
                else:
                    print(f"   ❌ Audio synthesis failed with status {response.status}")
        except Exception as e:
            print(f"   ❌ Audio synthesis error: {e}")

async def test_different_certifications():
    """Test with different certification types."""
    print("\n" + "=" * 60)
    print("🔍 Testing Different Certification Types")
    print("=" * 60)
    
    test_certs = ["MS-900", "PL-900", "SC-900"]
    
    async with aiohttp.ClientSession() as session:
        for cert in test_certs:
            print(f"\nTesting {cert}...")
            try:
                async with session.get(f"{BASE_URL}/api/v1/assessments/{cert}") as response:
                    if response.status == 200:
                        assessment = await response.json()
                        print(f"   ✅ {cert}: {len(assessment['questions'])} questions generated")
                    else:
                        print(f"   ❌ {cert}: Failed with status {response.status}")
            except Exception as e:
                print(f"   ❌ {cert}: Error - {e}")

if __name__ == "__main__":
    asyncio.run(test_certification_api())
    asyncio.run(test_different_certifications())