"""
Detailed debug to see exactly what's happening
"""

import json
import pandas as pd
from keyword_only_recommender import KeywordRecommendationEngine

# Load engine
engine = KeywordRecommendationEngine()

# Load train data
train_df = pd.read_excel('Gen_AI Dataset.xlsx', sheet_name='Train-Set')

# Take first query as example
first_query = train_df['Query'].iloc[0]
relevant_urls_for_query = train_df[train_df['Query'] == first_query]['Assessment_url'].tolist()

print("="*70)
print("DETAILED DEBUG - FIRST QUERY")
print("="*70)

print(f"\n📝 Query:")
print(f"{first_query}\n")

print(f"📋 Expected URLs (from train data):")
for i, url in enumerate(relevant_urls_for_query, 1):
    print(f"{i}. {url}")

print(f"\n🤖 Getting recommendations...")
predictions = engine.recommend(first_query, num_recommendations=10)

print(f"\n📦 What we predicted:")
for i, pred in enumerate(predictions, 1):
    print(f"{i}. {pred['name']}")
    print(f"   URL: {pred['url']}")
    print(f"   Type: {pred.get('test_type', 'N/A')}\n")

# Check matches
def normalize_url(url):
    url = url.rstrip('/')
    if '/product-catalog/view/' in url:
        return url.split('/product-catalog/view/')[-1]
    return url

predicted_urls_normalized = [normalize_url(p['url']) for p in predictions]
relevant_urls_normalized = [normalize_url(url) for url in relevant_urls_for_query]

print("="*70)
print("URL MATCHING")
print("="*70)

matches = 0
for pred_url in predicted_urls_normalized:
    if pred_url in relevant_urls_normalized:
        matches += 1
        print(f"✓ MATCH: {pred_url}")
    else:
        print(f"✗ NO MATCH: {pred_url}")

print(f"\n📊 Results:")
print(f"Total predicted: {len(predictions)}")
print(f"Total relevant: {len(relevant_urls_for_query)}")
print(f"Matches: {matches}")
print(f"Recall@10: {matches/len(relevant_urls_for_query):.2%}")

# Show what we missed
print("\n⚠️  Relevant URLs we MISSED:")
for url in relevant_urls_normalized:
    if url not in predicted_urls_normalized:
        # Find the assessment name
        full_url = [u for u in relevant_urls_for_query if normalize_url(u) == url][0]
        print(f"  - {url}")
        print(f"    Full: {full_url}")
        
        # Check if we have this assessment
        found = False
        for assessment in engine.assessments:
            if normalize_url(assessment['url']) == url:
                print(f"    ✓ WE HAVE IT: {assessment['name']} (Type: {assessment.get('test_type', 'N/A')})")
                found = True
                break
        
        if not found:
            print(f"    ✗ NOT IN OUR DATABASE")

print("\n" + "="*70)
print("DIAGNOSIS")
print("="*70)

if matches == 0:
    print("❌ ZERO matches means:")
    print("   1. Keywords not matching properly")
    print("   2. Scoring logic is wrong")
    print("   3. URLs not in database")
elif matches < len(relevant_urls_for_query) * 0.3:
    print("⚠️  Very few matches means:")
    print("   1. Keyword extraction needs improvement")
    print("   2. Need better scoring weights")
else:
    print("✓ Some matches - system is working but needs tuning")