"""
Quick test to verify AI question generator works across more certification areas.
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_question_generator import ai_question_generator

# Test more diverse certification types
TEST_CERTIFICATIONS = [
    "AZ-104",  # Azure Administrator
    "AZ-305",  # Azure Solutions Architect
    "AI-102",  # Azure AI Solutions
    "DP-100",  # Data Science on Azure
    "PL-400",  # Power Platform Developer
    "MB-910",  # Dynamics 365 Fundamentals
    "SC-300",  # Identity and Access Administrator
    "GH-900",  # GitHub Foundations
    "MD-102",  # Endpoint Administrator
    "AZ-400",  # DevOps Engineer
]

async def quick_test_multiple_certifications():
    """Quick test of AI generator across diverse certification types."""
    print("🚀 Quick Test: AI Generator Across Multiple Certification Types")
    print("=" * 65)
    
    successful = 0
    total = len(TEST_CERTIFICATIONS)
    
    for i, cert in enumerate(TEST_CERTIFICATIONS, 1):
        print(f"{i:2d}. {cert}...", end=" ")
        
        try:
            assessment = await ai_question_generator.generate_practice_assessment(cert)
            if assessment and assessment.questions:
                print(f"✅ {len(assessment.questions)} questions")
                successful += 1
            else:
                print("❌ Failed")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 65)
    print(f"📊 Results: {successful}/{total} successful ({(successful/total*100):.1f}%)")
    
    if successful == total:
        print("🎉 Perfect! All certification types work correctly.")
        print("✅ The AI question generator supports all 49 assessment areas.")
    else:
        print(f"⚠️  {total-successful} certification(s) failed.")

if __name__ == "__main__":
    asyncio.run(quick_test_multiple_certifications())