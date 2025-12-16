"""
SIMPLER VERSION - No FAISS required
Uses pure Gemini for recommendations
Faster to set up, good enough for the assignment
"""

import json
import google.generativeai as genai
from typing import List, Dict

# Get your FREE API key from: https://ai.google.dev/
GEMINI_API_KEY = "AIzaSyDpDT9KstdRvDL7wPD6GgcoYqNrSaFW03A"
genai.configure(api_key=GEMINI_API_KEY)

class SimpleRecommendationEngine:
    def __init__(self, assessments_file='shl_assessments.json'):
        """Load assessments"""
        print("Loading assessments...")
        with open(assessments_file, 'r', encoding='utf-8') as f:
            self.assessments = json.load(f)
        print(f"✓ Loaded {len(self.assessments)} assessments")
        
        self.model = genai.GenerativeModel('gemini-pro')
    
    def create_catalog_summary(self, max_items=200) -> str:
        """Create a summary of assessments for the LLM"""
        # Use first 200 assessments to fit in context
        items = []
        for i, assessment in enumerate(self.assessments[:max_items]):
            items.append(
                f"{i+1}. {assessment['name']} | "
                f"Type: {assessment.get('test_type', 'N/A')} | "
                f"URL: {assessment['url']}"
            )
        return "\n".join(items)
    
    def recommend(self, query: str, num_recommendations=10) -> List[Dict]:
        """Get recommendations using Gemini"""
        print(f"\nProcessing: {query}")
        
        # Create catalog for LLM
        catalog = self.create_catalog_summary()
        
        # Create smart prompt
        prompt = f"""You are an expert HR assessment recommendation system.

USER QUERY: {query}

ASSESSMENT CATALOG (first 200 items):
{catalog}

TASK:
1. Analyze the query to understand required skills (technical AND behavioral)
2. Select the {num_recommendations} MOST RELEVANT assessments
3. IMPORTANT: Balance technical skills (Type K) with behavioral skills (Type P) when query mentions both
4. Return EXACTLY {num_recommendations} recommendations

TEST TYPE GUIDE:
- K = Knowledge & Skills (Java, Python, SQL, coding, technical)
- P = Personality & Behavior (teamwork, leadership, communication)
- B = Biodata & Situational Judgement
- A = Ability & Aptitude
- S = Simulations

EXAMPLE BALANCING:
Query: "Java developer who collaborates well"
Should return: Mix of Java/coding tests (Type K) + teamwork/collaboration tests (Type P)

Return ONLY a JSON array with assessment numbers from the catalog above.
Format: [1, 45, 12, 78, 23, 56, 89, 34, 67, 90]

Your response (JSON array only):"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Extract JSON
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
                print("⚠️ Could not parse LLM response")
                return self.assessments[:num_recommendations]
        
        except Exception as e:
            print(f"Error: {e}")
            return self.assessments[:num_recommendations]
    
    def format_for_api(self, results: List[Dict]) -> Dict:
        """Format results for API response"""
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


# QUICK TEST
def test_engine():
    """Test the engine"""
    engine = SimpleRecommendationEngine()
    
    # Test queries from assignment
    queries = [
        "I am hiring for Java developers who can also collaborate effectively with my business teams.",
        "Looking to hire mid-level professionals who are proficient in Python, SQL and Java Script.",
        "Need cognitive and personality tests for analyst role"
    ]
    
    for query in queries:
        print("\n" + "="*70)
        results = engine.recommend(query, num_recommendations=10)
        
        print(f"\nQuery: {query}")
        print(f"\nRecommendations:")
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['name']} (Type: {r.get('test_type', 'N/A')})")
            print(f"   {r['url']}")
        print()


if __name__ == "__main__":
    # Make sure to set your API key above!
    test_engine()