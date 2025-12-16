"""
Verify your assessment data
"""

import json
import pandas as pd

# Check assessments
with open('shl_assessments.json', 'r') as f:
    assessments = json.load(f)

print("="*70)
print("DATA VERIFICATION")
print("="*70)

print(f"\n📦 Your Assessment Database:")
print(f"   Total assessments: {len(assessments)}")

# Check train data
train_df = pd.read_excel('Gen_AI Dataset.xlsx', sheet_name='Train-Set')
train_urls = set(train_df['Assessment_url'].str.rstrip('/'))

print(f"\n📋 Train Data:")
print(f"   Total URLs needed: {len(train_urls)}")

# Check coverage
assessment_urls = set(a['url'].rstrip('/') for a in assessments)
coverage = len(train_urls.intersection(assessment_urls))
missing = len(train_urls - assessment_urls)

print(f"\n📊 Coverage:")
print(f"   URLs you have: {coverage}/{len(train_urls)}")
print(f"   Missing: {missing}")
print(f"   Coverage: {coverage/len(train_urls)*100:.1f}%")

if len(assessments) < 100:
    print("\n" + "="*70)
    print("⚠️  CRITICAL PROBLEM!")
    print("="*70)
    print(f"You only have {len(assessments)} assessments!")
    print("You need at least 377 (requirement) to cover all train data.")
    print("\n🔧 SOLUTION: Run the full scraper to get all assessments")
    print("   Run: python shl_scraper.py")
    print("   This will take 5-10 minutes but is necessary!")

elif missing > 0:
    print(f"\n⚠️  Missing {missing} URLs from train data")
    print("First 5 missing:")
    for url in list(train_urls - assessment_urls)[:5]:
        print(f"  - {url}")

else:
    print("\n✅ Good! You have all needed assessments")
    print("   Issue might be with recommendation logic")

# Show sample
print(f"\n📝 Sample assessments you have:")
for i, a in enumerate(assessments[:5], 1):
    print(f"{i}. {a['name']} - Type: {a.get('test_type', 'N/A')}")