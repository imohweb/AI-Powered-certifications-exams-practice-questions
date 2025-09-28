"""
Test the enhanced AI question generator with 50 questions per assessment.
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_question_generator import ai_question_generator

async def test_50_question_generation():
    """Test generation of 50 questions per assessment."""
    print("🚀 Testing Enhanced 50-Question Generation")
    print("=" * 50)
    
    # Test with AZ-900 first
    cert_code = "AZ-900"
    print(f"Generating assessment for {cert_code}...")
    print("This may take 30-60 seconds for 50 questions...")
    
    try:
        assessment = await ai_question_generator.generate_practice_assessment(cert_code)
        
        if assessment and assessment.questions:
            print(f"\n✅ SUCCESS!")
            print(f"   Certification: {cert_code}")
            print(f"   Title: {assessment.title}")
            print(f"   Total Questions: {len(assessment.questions)}")
            print(f"   Duration: {assessment.estimated_duration_minutes} minutes")
            
            # Analyze question quality
            difficulties = {}
            total_topics = set()
            
            for q in assessment.questions:
                diff = str(q.difficulty).replace('DifficultyLevel.', '')
                difficulties[diff] = difficulties.get(diff, 0) + 1
                total_topics.update(q.topics)
            
            print(f"\n📊 Question Analysis:")
            print(f"   Difficulty Distribution:")
            for diff, count in difficulties.items():
                print(f"     - {diff}: {count} questions")
            print(f"   Total Unique Topics: {len(total_topics)}")
            print(f"   Topics Sample: {list(total_topics)[:10]}")
            
            # Show sample questions
            print(f"\n📝 Sample Questions:")
            for i, q in enumerate(assessment.questions[:3], 1):
                print(f"   {i}. {q.text[:80]}...")
                print(f"      Difficulty: {str(q.difficulty).replace('DifficultyLevel.', '')}")
                print(f"      Topics: {q.topics[:3]}")
                print()
            
            if len(assessment.questions) == 50:
                print("🎉 Perfect! Generated exactly 50 questions as required.")
            else:
                print(f"⚠️  Generated {len(assessment.questions)} questions instead of 50.")
                
        else:
            print("❌ Failed to generate assessment")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_question_authenticity():
    """Test if questions align with Microsoft's official content."""
    print("\n" + "=" * 50)
    print("🔍 Testing Question Authenticity")
    print("=" * 50)
    
    cert_code = "SC-900"  # Test with Security fundamentals
    print(f"Testing {cert_code} for Microsoft Learn alignment...")
    
    try:
        assessment = await ai_question_generator.generate_practice_assessment(cert_code)
        
        if assessment and assessment.questions:
            # Check for Microsoft-specific terms and concepts
            microsoft_terms = ['Azure', 'Microsoft', 'AD', 'Zero Trust', 'Conditional Access', 
                             'MFA', 'Entra', 'Defender', 'Sentinel', 'Purview']
            
            questions_with_ms_terms = 0
            for q in assessment.questions:
                if any(term.lower() in q.text.lower() for term in microsoft_terms):
                    questions_with_ms_terms += 1
            
            authenticity_score = (questions_with_ms_terms / len(assessment.questions)) * 100
            
            print(f"✅ Microsoft authenticity check:")
            print(f"   Questions with MS terms: {questions_with_ms_terms}/{len(assessment.questions)}")
            print(f"   Authenticity Score: {authenticity_score:.1f}%")
            
            if authenticity_score > 80:
                print("🎉 High authenticity - questions align well with Microsoft content!")
            elif authenticity_score > 60:
                print("✅ Good authenticity - questions are reasonably aligned.")
            else:
                print("⚠️  Low authenticity - may need improvement.")
                
        else:
            print("❌ Failed to generate assessment for authenticity test")
            
    except Exception as e:
        print(f"❌ Error in authenticity test: {e}")

if __name__ == "__main__":
    asyncio.run(test_50_question_generation())
    asyncio.run(test_question_authenticity())