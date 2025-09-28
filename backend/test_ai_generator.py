"""
Test the simplified AI question generator across multiple certifications.
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_question_generator import ai_question_generator

# Test a few different certification types
TEST_CERTIFICATIONS = [
    "AZ-900",  # Azure Fundamentals
    "MS-900",  # Microsoft 365 Fundamentals
    "PL-900",  # Power Platform Fundamentals
    "SC-900",  # Security Fundamentals
    "DP-900",  # Data Fundamentals
]

async def test_ai_question_generation():
    """Test AI question generation for multiple certifications."""
    print("🚀 Testing Simplified AI Question Generator")
    print("=" * 60)
    
    successful_tests = 0
    total_tests = len(TEST_CERTIFICATIONS)
    
    for i, cert_code in enumerate(TEST_CERTIFICATIONS, 1):
        print(f"\n{i}. Testing {cert_code}...")
        print("-" * 30)
        
        try:
            # Generate assessment
            assessment = await ai_question_generator.generate_practice_assessment(cert_code)
            
            if assessment and assessment.questions:
                successful_tests += 1
                print(f"✅ SUCCESS: Generated {len(assessment.questions)} questions")
                print(f"   Title: {assessment.title}")
                print(f"   Duration: {assessment.estimated_duration_minutes} minutes")
                
                # Show sample question
                if assessment.questions:
                    q = assessment.questions[0]
                    print(f"   Sample Question: {q.text[:100]}...")
                    print(f"   Answers: {len(q.answers)}")
                    print(f"   Difficulty: {q.difficulty}")
                    print(f"   Topics: {q.topics[:3]}")  # First 3 topics
            else:
                print(f"❌ FAILED: No questions generated")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {(successful_tests/total_tests*100):.1f}%")
    
    if successful_tests == total_tests:
        print("\n🎉 All tests passed! AI question generator is working correctly.")
    else:
        print(f"\n⚠️  {total_tests - successful_tests} tests failed. Check the logs above.")

if __name__ == "__main__":
    asyncio.run(test_ai_question_generation())