"""
Test script for the enhanced AI-powered scraper.
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.enhanced_scraper import EnhancedMicrosoftLearnScraper


async def test_enhanced_scraper():
    """Test the enhanced AI-powered scraper."""
    
    print("🚀 Testing Enhanced AI-Powered Scraper")
    print("=" * 50)
    
    try:
        # Test with a popular certification
        certification_code = "AZ-900"
        
        print(f"\n1. Testing scraping for {certification_code}...")
        
        async with EnhancedMicrosoftLearnScraper() as scraper:
            assessment = await scraper.scrape_practice_assessment(certification_code)
            
            if assessment:
                print(f"✅ Successfully scraped assessment for {certification_code}")
                print(f"   Title: {assessment.title}")
                print(f"   Questions: {len(assessment.questions)}")
                print(f"   Duration: {assessment.estimated_duration_minutes} minutes")
                
                # Show first question as sample
                if assessment.questions:
                    first_q = assessment.questions[0]
                    print(f"\n📝 Sample Question:")
                    print(f"   Question: {first_q.text[:100]}...")
                    print(f"   Answers: {len(first_q.answers)}")
                    print(f"   Difficulty: {first_q.difficulty.value}")
                    print(f"   Topics: {first_q.topics}")
                
                return True
            else:
                print(f"❌ Failed to scrape assessment for {certification_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing enhanced scraper: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_enhanced_scraper())
    if success:
        print("\n🎉 Enhanced scraper test completed successfully!")
    else:
        print("\n⚠️ Enhanced scraper test failed!")