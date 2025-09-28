"""
Comprehensive test for enhanced scraper across all Microsoft certification assessments.
Tests multiple certification codes to ensure AI-powered question generation works consistently.
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.enhanced_scraper import EnhancedMicrosoftLearnScraper
from app.core.config import settings

# Sample of certification codes to test (representing different categories)
TEST_CERTIFICATIONS = [
    # Azure Fundamentals
    "AZ-900",
    
    # Azure Role-based
    "AZ-104",  # Azure Administrator
    "AZ-204",  # Azure Developer
    "AZ-305",  # Azure Solutions Architect
    
    # Microsoft 365
    "MS-900",  # Microsoft 365 Fundamentals
    "MS-102",  # Microsoft 365 Administrator
    
    # Power Platform
    "PL-900",  # Power Platform Fundamentals
    "PL-300",  # Power BI Data Analyst
    
    # Dynamics 365
    "MB-910",  # Dynamics 365 Fundamentals
    "MB-220",  # Dynamics 365 Marketing
    
    # Security, Compliance, and Identity
    "SC-900",  # Security, Compliance, and Identity Fundamentals
    "SC-300",  # Identity and Access Administrator
    
    # Data & AI
    "DP-900",  # Azure Data Fundamentals
    "AI-900",  # Azure AI Fundamentals
    "DP-100",  # Azure Data Scientist
    
    # DevOps and Development
    "AZ-400",  # DevOps Engineer Expert
    
    # Windows Server and SQL
    "AZ-800",  # Windows Server Hybrid Administrator
    "DP-300",  # Azure Database Administrator
]

async def test_certification_scraping():
    """Test enhanced scraper with multiple certification codes."""
    print("🚀 Testing Enhanced AI-Powered Scraper Across Multiple Certifications")
    print("=" * 80)
    
    # Initialize the enhanced scraper
    scraper = EnhancedMicrosoftLearnScraper()
    
    successful_tests = 0
    failed_tests = 0
    test_results = []
    
    for i, cert_code in enumerate(TEST_CERTIFICATIONS, 1):
        print(f"\n{i}. Testing certification: {cert_code}")
        print("-" * 40)
        
        try:
            # Test scraping for this certification
            assessment = await scraper.scrape_practice_assessment(cert_code)
            
            if assessment:
                successful_tests += 1
                result = {
                    "certification": cert_code,
                    "status": "✅ SUCCESS",
                    "title": assessment.title,
                    "questions": len(assessment.questions),
                    "duration": assessment.estimated_duration_minutes
                }
                
                print(f"✅ Successfully scraped assessment for {cert_code}")
                print(f"   Title: {assessment.title}")
                print(f"   Questions: {len(assessment.questions)}")
                print(f"   Duration: {assessment.estimated_duration_minutes} minutes")
                
                # Show a sample question if available
                if assessment.questions:
                    sample_q = assessment.questions[0]
                    print(f"   Sample Question: {sample_q.text[:80]}...")
                    print(f"   Answers: {len(sample_q.answers)}")
                    print(f"   Difficulty: {sample_q.difficulty}")
                    print(f"   Topics: {sample_q.topics}")
                
            else:
                failed_tests += 1
                result = {
                    "certification": cert_code,
                    "status": "❌ FAILED",
                    "title": "N/A",
                    "questions": 0,
                    "duration": 0
                }
                print(f"❌ Failed to scrape assessment for {cert_code}")
            
            test_results.append(result)
            
        except Exception as e:
            failed_tests += 1
            result = {
                "certification": cert_code,
                "status": f"❌ ERROR: {str(e)[:50]}...",
                "title": "N/A",
                "questions": 0,
                "duration": 0
            }
            test_results.append(result)
            print(f"❌ Error testing {cert_code}: {e}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    print(f"Total Certifications Tested: {len(TEST_CERTIFICATIONS)}")
    print(f"Successful Tests: {successful_tests}")
    print(f"Failed Tests: {failed_tests}")
    print(f"Success Rate: {(successful_tests/len(TEST_CERTIFICATIONS)*100):.1f}%")
    
    # Detailed results table
    print("\n📋 DETAILED RESULTS:")
    print("-" * 80)
    print(f"{'Cert Code':<10} {'Status':<15} {'Questions':<10} {'Duration':<10} {'Title':<30}")
    print("-" * 80)
    
    for result in test_results:
        title_short = result["title"][:28] + "..." if len(result["title"]) > 30 else result["title"]
        print(f"{result['certification']:<10} {result['status'][:13]:<15} {result['questions']:<10} {result['duration']:<10} {title_short:<30}")
    
    print("\n🎉 Comprehensive testing completed!")
    
    return test_results

async def test_specific_areas():
    """Test specific high-priority certification areas."""
    print("\n🎯 Testing High-Priority Certification Areas")
    print("=" * 60)
    
    priority_certs = ["AZ-900", "AZ-104", "MS-900", "PL-900", "SC-900", "DP-900", "AI-900"]
    scraper = EnhancedMicrosoftLearnScraper()
    
    for cert in priority_certs:
        print(f"\n🔍 Deep testing {cert}...")
        try:
            assessment = await scraper.scrape_practice_assessment(cert)
            if assessment and assessment.questions:
                # Test question quality
                q = assessment.questions[0]
                print(f"   ✅ {cert}: {len(assessment.questions)} questions generated")
                print(f"   📝 Question quality check: {len(q.text)} chars, {len(q.answers)} answers")
                print(f"   🎯 Topics: {', '.join(q.topics[:3])}")  # Show first 3 topics
            else:
                print(f"   ❌ {cert}: No questions generated")
        except Exception as e:
            print(f"   ❌ {cert}: Error - {e}")

if __name__ == "__main__":
    # Run comprehensive tests
    asyncio.run(test_certification_scraping())
    
    # Run specific area tests
    asyncio.run(test_specific_areas())