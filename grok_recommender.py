
import json
import requests
from typing import List, Dict
import time
from dotenv import load_dotenv
import os

load_dotenv()
GROK_API_KEY = os.getenv("GROK_API_KEY")

class GrokRecommendationEngine:
    def __init__(self, assessments_file='shl_assessments.json'):
        """Load assessments"""
        print("Loading assessments...")
        with open(assessments_file, 'r', encoding='utf-8') as f:
            self.assessments = json.load(f)
        print(f"✓ Loaded {len(self.assessments)} assessments")
        
        self.api_url = "https://api.x.ai/v1/chat/completions"
        self.api_key = GROK_API_KEY
    
    def create_catalog_text(self, max_items=300) -> str:
        """Create catalog for Grok"""
        items = []
        for i, assessment in enumerate(self.assessments[:max_items]):
            desc = f"{i+1}. {assessment['name']}"
            desc += f" | Type: {assessment.get('test_type', 'N/A')}"
            desc += f" | URL: {assessment['url']}"
            items.append(desc)
        return "\n".join(items)
    
    def call_grok(self, prompt: str) -> str:
        """Call Grok API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert HR assessment recommendation system."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": "grok-beta",
            "temperature": 0.3
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"Grok API Error: {e}")
            return None
    
    def recommend(self, query: str, num_recommendations=10) -> List[Dict]:
        """Get recommendations using Grok"""
        print(f"\n🔍 Processing: {query[:80]}...")
        
        # Create catalog
        catalog = self.create_catalog_text(max_items=300)
        
        # Create prompt
        prompt = f"""You are an expert HR assessment selector for SHL assessments.

USER QUERY: {query}

ASSESSMENT CATALOG (first 300 items):
{catalog}

TEST TYPE GUIDE:
- K = Knowledge & Skills (Java, Python, SQL, coding, technical)
- P = Personality & Behavior (teamwork, leadership, communication)
- B = Biodata & Situational Judgement
- A = Ability & Aptitude
- S = Simulations

CRITICAL INSTRUCTIONS:
1. For technical roles: Prioritize Type K assessments that match the EXACT technologies mentioned
2. For soft skills: Include Type P assessments
3. When BOTH technical AND soft skills mentioned: 60-70% technical, 30-40% behavioral
4. Return EXACTLY {num_recommendations} assessments
5. Match the specific technologies (e.g., "Python" in query → Python assessments)

EXAMPLES:
- Query: "Java developer who collaborates" → 6-7 Java tests (Type K) + 3-4 collaboration tests (Type P)
- Query: "Python, SQL, JavaScript" → Mix of Python, SQL, and JavaScript tests
- Query: "Sales role" → Sales and communication tests

Return ONLY a JSON array with assessment numbers from the catalog.
Format: [12, 45, 67, 89, 23, 156, 234, 78, 190, 145]

Your response (JSON array only):"""

        # Call Grok
        response = self.call_grok(prompt)
        
        if not response:
            print("⚠️ Grok API failed, using fallback")
            return self._fallback_recommend(query, num_recommendations)
        
        try:
            # Extract JSON
            text = response.strip()
            if '[' in text and ']' in text:
                start = text.index('[')
                end = text.rindex(']') + 1
                json_str = text[start:end]
                indices = json.loads(json_str)
                
                # Get assessments
                results = []
                for idx in indices[:num_recommendations]:
                    idx = idx - 1  # Convert to 0-based
                    if 0 <= idx < len(self.assessments):
                        results.append(self.assessments[idx])
                
                print(f"✓ Found {len(results)} recommendations")
                return results
            else:
                print("⚠️ Could not parse response")
                return self._fallback_recommend(query, num_recommendations)
        
        except Exception as e:
            print(f"❌ Error parsing: {e}")
            return self._fallback_recommend(query, num_recommendations)
    
    def _fallback_recommend(self, query: str, num: int) -> List[Dict]:
        """Fallback: Keyword matching"""
        from keyword_only_recommender import KeywordRecommendationEngine
        fallback = KeywordRecommendationEngine()
        return fallback.recommend(query, num)
    
    def format_for_api(self, results: List[Dict]) -> Dict:
        """Format for API"""
        return {
            'recommendations': [
                {
                    'assessment_name': r['name'],
                    'assessment_url': r['url'],
                    'test_type': r.get('test_type', ''),
                }
                for r in results
            ]
        }


# TEST FUNCTION
def test_grok():
    """Test Grok engine"""
    engine = GrokRecommendationEngine()
    
    queries = [
        "I am hiring for Java developers who can also collaborate effectively",
        "Looking to hire mid-level professionals who are proficient in Python, SQL and Java Script"
    ]
    
    for query in queries:
        print("\n" + "="*70)
        results = engine.recommend(query, num_recommendations=10)
        
        print(f"\nQuery: {query}")
        print(f"\nTop 10 Recommendations:")
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['name']} (Type: {r.get('test_type', 'N/A')})")
        
        time.sleep(2)


if __name__ == "__main__":
    if GROK_API_KEY is None or GROK_API_KEY.strip() == "":
        print("❌ ERROR: Set Grok API key first!")
        
    else:
        test_grok()