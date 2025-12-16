"""
UPDATED: Evaluation Script for Your Excel Data Format
Works with: Query, Assessment_url columns
"""

import json
import pandas as pd
from typing import List, Dict
import time

from grok_recommender import GrokRecommendationEngine

def load_train_data_from_excel(excel_file='Gen_AI Dataset.xlsx', sheet_name='Train-Set'):
    """
    Load training data from Excel
    Expected columns: Query, Assessment_url
    """
    print(f"Loading train data from {excel_file}...")
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    # Normalize column names (handle spaces, case)
    df.columns = df.columns.str.strip()
    
    print(f"✓ Loaded {len(df)} rows")
    print(f"  Columns: {list(df.columns)}")
    
    # Group by query to get all relevant assessments per query
    train_data = {}
    query_col = 'Query' if 'Query' in df.columns else 'query'
    url_col = 'Assessment_url' if 'Assessment_url' in df.columns else 'assessment_url'
    
    for query in df[query_col].unique():
        relevant_urls = df[df[query_col] == query][url_col].tolist()
        # Normalize URLs (remove trailing slashes)
        relevant_urls = [url.rstrip('/') for url in relevant_urls]
        train_data[query] = relevant_urls
    
    print(f"✓ Found {len(train_data)} unique queries")
    for query, urls in train_data.items():
        print(f"  - {len(urls)} assessments for: {query[:60]}...")
    
    return train_data


def calculate_recall_at_k(predicted_urls: List[str], 
                          relevant_urls: List[str], 
                          k: int = 10) -> float:
    """
    Calculate Recall@K for a single query
    Recall@K = (Number of relevant items in top K) / (Total relevant items)
    """
    # Normalize URLs to handle /products/ vs /solutions/products/ differences
    def normalize_url(url):
        url = url.rstrip('/')
        if '/product-catalog/view/' in url:
            return url.split('/product-catalog/view/')[-1]
        return url
    
    predicted_urls = [normalize_url(url) for url in predicted_urls]
    relevant_urls = [normalize_url(url) for url in relevant_urls]
    
    # Take only top K predictions
    top_k_predictions = predicted_urls[:k]
    
    # Count matches
    relevant_in_top_k = sum(1 for url in top_k_predictions if url in relevant_urls)
    
    # Calculate recall
    total_relevant = len(relevant_urls)
    if total_relevant == 0:
        return 0.0
    
    recall = relevant_in_top_k / total_relevant
    return recall


def evaluate_system(engine, train_data: Dict, k: int = 10):
    """
    Evaluate the recommendation system on train data
    Returns: Mean Recall@K
    """
    print("\n" + "="*70)
    print("EVALUATING SYSTEM ON TRAIN DATA")
    print("="*70)
    
    recalls = []
    query_details = []
    
    for i, (query, relevant_urls) in enumerate(train_data.items(), 1):
        print(f"\n📝 Query {i}/{len(train_data)}:")
        print(f"   {query[:80]}...")
        
        # Get predictions
        predictions = engine.recommend(query, num_recommendations=10)
        predicted_urls = [p['url'].rstrip('/') for p in predictions]
        
        # Calculate recall
        recall = calculate_recall_at_k(predicted_urls, relevant_urls, k=k)
        recalls.append(recall)
        
        # Count matches
        matches = sum(1 for url in predicted_urls[:k] if url.rstrip('/') in relevant_urls)
        
        print(f"   Relevant assessments: {len(relevant_urls)}")
        print(f"   Found in top {k}: {matches}")
        print(f"   Recall@{k}: {recall:.3f} ({recall*100:.1f}%)")
        
        # Show what was found
        if matches > 0:
            print(f"   ✓ Matched assessments:")
            for pred in predictions[:k]:
                if pred['url'].rstrip('/') in relevant_urls:
                    print(f"      - {pred['name']}")
        
        # Track details
        query_details.append({
            'query': query,
            'recall': recall,
            'matches': matches,
            'total_relevant': len(relevant_urls)
        })
        
        time.sleep(1)  # Be nice to API
    
    # Calculate mean recall
    mean_recall = sum(recalls) / len(recalls) if recalls else 0.0
    
    print("\n" + "="*70)
    print("EVALUATION RESULTS")
    print("="*70)
    print(f"Mean Recall@{k}: {mean_recall:.3f} ({mean_recall*100:.1f}%)")
    print(f"Min Recall: {min(recalls):.3f}")
    print(f"Max Recall: {max(recalls):.3f}")
    print(f"Total Queries: {len(recalls)}")
    
    # Show performance breakdown
    print(f"\nPerformance Breakdown:")
    excellent = sum(1 for r in recalls if r >= 0.8)
    good = sum(1 for r in recalls if 0.6 <= r < 0.8)
    okay = sum(1 for r in recalls if 0.4 <= r < 0.6)
    poor = sum(1 for r in recalls if r < 0.4)
    
    print(f"  Excellent (≥80%): {excellent}")
    print(f"  Good (60-79%): {good}")
    print(f"  Okay (40-59%): {okay}")
    print(f"  Needs work (<40%): {poor}")
    
    # Show worst performing queries
    if recalls:
        print(f"\n⚠️  Queries needing improvement:")
        sorted_details = sorted(query_details, key=lambda x: x['recall'])
        for detail in sorted_details[:3]:
            print(f"  - Recall {detail['recall']:.2f}: {detail['query'][:60]}...")
    
    return mean_recall, recalls, query_details


def generate_test_predictions(engine, excel_file='Gen_AI Dataset.xlsx', 
                              test_sheet='Test-Set',
                              output_file='predictions.csv'):
    """
    Generate predictions for test set and save to CSV
    Required format: query, assessment_url
    """
    print("\n" + "="*70)
    print("GENERATING TEST PREDICTIONS")
    print("="*70)
    
    # Load test queries
    test_df = pd.read_excel(excel_file, sheet_name=test_sheet)
    
    # Handle column names
    test_df.columns = test_df.columns.str.strip()
    query_col = 'Query' if 'Query' in test_df.columns else 'query'
    
    queries = test_df[query_col].unique()
    
    print(f"Found {len(queries)} test queries")
    
    results = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Processing...")
        print(f"Query: {query[:80]}...")
        
        # Get recommendations
        predictions = engine.recommend(query, num_recommendations=10)
        
        # Add to results (each recommendation = one row)
        for pred in predictions:
            results.append({
                'query': query,
                'assessment_url': pred['url']
            })
        
        print(f"✓ Generated {len(predictions)} recommendations")
        time.sleep(2)  # Rate limiting
    
    # Save to CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)
    
    print("\n" + "="*70)
    print(f"✓ PREDICTIONS SAVED to {output_file}")
    print("="*70)
    print(f"Total rows: {len(results_df)}")
    print(f"Format: query, assessment_url")
    print("Ready for submission!")
    
    return results_df


def show_sample_predictions(predictions_df, n=5):
    """Show sample predictions"""
    print("\n" + "="*70)
    print(f"SAMPLE PREDICTIONS (first {n} rows):")
    print("="*70)
    print(predictions_df.head(n).to_string())


# MAIN EVALUATION FUNCTION
def run_full_evaluation(excel_file='Gen_AI Dataset.xlsx'):
    """Complete evaluation workflow"""
    from keyword_only_recommender import KeywordRecommendationEngine
    from grok_recommender import GrokRecommendationEngine
    engine = GrokRecommendationEngine()
    print("="*70)
    print("SHL ASSESSMENT RECOMMENDATION - FULL EVALUATION")
    print("="*70)
    
    # Load engine
    print("\n1️⃣ Loading recommendation engine...")
    engine = KeywordRecommendationEngine()  # USE KEYWORD ENGINE!
    
    # Load train data
    print("\n2️⃣ Loading train data...")
    train_data = load_train_data_from_excel(excel_file, sheet_name='Train-Set')
    
    # Evaluate
    print("\n3️⃣ Evaluating on train data...")
    mean_recall, recalls, query_details = evaluate_system(engine, train_data, k=10)
    
    # Generate test predictions
    print("\n4️⃣ Generating test predictions...")
    predictions_df = generate_test_predictions(
        engine, 
        excel_file=excel_file,
        test_sheet='Test-Set',
        output_file='predictions.csv'
    )
    
    # Show samples
    show_sample_predictions(predictions_df)
    
    # Final summary
    print("\n" + "="*70)
    print("✅ EVALUATION COMPLETE!")
    print("="*70)
    print(f"Performance Score: {mean_recall:.3f} ({mean_recall*100:.1f}%)")
    print(f"Predictions saved: predictions.csv")
    print(f"Total predictions: {len(predictions_df)} rows")
    print("\n✓ Ready for submission!")
    
    return mean_recall, predictions_df


if __name__ == "__main__":
    import sys
    import os
    
    # Check if Excel file exists
    excel_file = 'Gen_AI Dataset.xlsx'
    
    if not os.path.exists(excel_file):
        print(f"❌ Error: {excel_file} not found!")
        print("Please make sure Gen_AI Dataset.xlsx is in the same folder.")
        print(f"Current folder: {os.getcwd()}")
        print(f"Files in folder: {os.listdir('.')}")
        sys.exit(1)
    
    # Make sure you have:
    # 1. shl_assessments_basic.json
    # 2. Gen_AI Dataset.xlsx
    # 3. GEMINI_API_KEY set in simple_recommendation_engine.py
    
    run_full_evaluation(excel_file)