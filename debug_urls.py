"""
Debug script to find why URLs aren't matching
"""

import json
import pandas as pd

# Load your assessments
with open('shl_assessments.json', 'r', encoding='utf-8') as f:
    assessments = json.load(f)

# Load train data
train_df = pd.read_excel('Gen_AI Dataset.xlsx', sheet_name='Train-Set')

print("="*70)
print("URL MATCHING DEBUG")
print("="*70)

# Get sample URLs from train data
train_urls = train_df['Assessment_url'].unique()[:5]
print("\n📋 Sample URLs from Train Data:")
for i, url in enumerate(train_urls, 1):
    print(f"{i}. {url}")

# Get sample URLs from your scraped data
assessment_urls = [a['url'] for a in assessments[:5]]
print("\n📦 Sample URLs from Your Scraped Data:")
for i, url in enumerate(assessment_urls, 1):
    print(f"{i}. {url}")

# Check for matches
print("\n" + "="*70)
print("CHECKING FOR MATCHES")
print("="*70)

matches = 0
for train_url in train_urls:
    train_url_clean = train_url.rstrip('/')
    found = False
    for assessment in assessments:
        assess_url_clean = assessment['url'].rstrip('/')
        if train_url_clean == assess_url_clean:
            found = True
            matches += 1
            break
    
    status = "✓ FOUND" if found else "✗ NOT FOUND"
    print(f"{status}: {train_url[:70]}...")

print(f"\nMatches: {matches}/{len(train_urls)}")

# Check all train URLs
print("\n" + "="*70)
print("FULL TRAIN DATA CHECK")
print("="*70)

all_train_urls = set(train_df['Assessment_url'].str.rstrip('/'))
all_assessment_urls = set(a['url'].rstrip('/') for a in assessments)

total_train = len(all_train_urls)
found_in_scraped = len(all_train_urls.intersection(all_assessment_urls))

print(f"Total unique URLs in train data: {total_train}")
print(f"Found in your scraped data: {found_in_scraped}")
print(f"Missing: {total_train - found_in_scraped}")

if found_in_scraped < total_train:
    print("\n⚠️  PROBLEM: Some train URLs are missing from your scraped data!")
    missing = all_train_urls - all_assessment_urls
    print(f"\nFirst 5 missing URLs:")
    for url in list(missing)[:5]:
        print(f"  - {url}")
    
    print("\n🔧 SOLUTION: You need to re-scrape with ALL assessments!")
    print("   Your scraped data might be incomplete.")

else:
    print("\n✓ All train URLs found in scraped data!")
    print("   The problem might be in the recommendation logic.")

# Check if URLs have different formats
print("\n" + "="*70)
print("URL FORMAT COMPARISON")
print("="*70)

sample_train = list(all_train_urls)[0]
sample_scraped = list(all_assessment_urls)[0]

print(f"Train URL format:   {sample_train}")
print(f"Scraped URL format: {sample_scraped}")

# Check for common differences
if '/solutions/' in sample_train and '/solutions/' not in sample_scraped:
    print("\n⚠️  Format difference: Train has /solutions/ but scraped doesn't!")
elif '/products/' in sample_train and '/products/' not in sample_scraped:
    print("\n⚠️  Format difference: Train has /products/ but scraped doesn't!")

print("\n" + "="*70)