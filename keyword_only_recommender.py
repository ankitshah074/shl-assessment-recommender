"""
Keyword-Only Recommendation Engine
NO API KEY NEEDED - Works immediately!
Uses smart keyword matching only
"""

import json
from typing import List, Dict
import re

class KeywordRecommendationEngine:
    def __init__(self, assessments_file='shl_assessments.json'):
        """Load assessments"""
        print("Loading assessments...")
        with open(assessments_file, 'r', encoding='utf-8') as f:
            self.assessments = json.load(f)
        print(f"✓ Loaded {len(self.assessments)} assessments")
    
    def extract_keywords(self, query: str) -> Dict:
        """Extract important keywords from query"""
        query_lower = query.lower()
        
        keywords = {
            'languages': [],
            'soft_skills': [],
            'level': [],
            'roles': [],
            'other_tech': []
        }
        
        # Programming languages & tech
        tech_keywords = {
            'java': ['java', 'jdk', 'spring', 'java8', 'java 8'],
            'python': ['python', 'django', 'flask'],
            'javascript': ['javascript', 'js ', ' js', 'node', 'react', 'angular', 'vue'],
            'sql': ['sql', 'database', 'mysql', 'postgresql', 'oracle sql'],
            'c++': ['c++', 'cpp'],
            'c#': ['c#', 'csharp', '.net', 'dot net'],
            'php': ['php'],
            'ruby': ['ruby'],
            'go': ['golang', ' go '],
            'html': ['html'],
            'css': ['css'],
            'excel': ['excel', 'spreadsheet'],
            'office': ['office', 'word', 'powerpoint'],
            'sap': ['sap'],
            'r': [' r ', 'r programming'],
            'scala': ['scala'],
            'swift': ['swift'],
            'kotlin': ['kotlin']
        }
        
        for tech, variations in tech_keywords.items():
            if any(var in query_lower for var in variations):
                keywords['languages'].append(tech)
        
        # Soft skills
        soft_skill_keywords = {
            'collaborate': ['collaborate', 'collaboration', 'collaborative'],
            'communication': ['communication', 'communicate'],
            'teamwork': ['teamwork', 'team work', 'team player'],
            'leadership': ['leadership', 'lead', 'leader'],
            'interpersonal': ['interpersonal'],
            'problem solving': ['problem solving', 'analytical'],
            'customer service': ['customer service', 'customer']
        }
        
        for skill, variations in soft_skill_keywords.items():
            if any(var in query_lower for var in variations):
                keywords['soft_skills'].append(skill)
        
        # Level
        if any(word in query_lower for word in ['entry', 'graduate', 'junior', 'fresh']):
            keywords['level'] = 'entry'
        elif any(word in query_lower for word in ['mid', 'intermediate', 'professional']):
            keywords['level'] = 'mid'
        elif any(word in query_lower for word in ['senior', 'lead', 'principal']):
            keywords['level'] = 'senior'
        
        # Roles
        role_keywords = {
            'sales': ['sales', 'selling'],
            'developer': ['developer', 'engineer', 'programmer', 'coding'],
            'analyst': ['analyst', 'analysis'],
            'manager': ['manager', 'management'],
            'accountant': ['accountant', 'accounting'],
            'customer service': ['customer service', 'support']
        }
        
        for role, variations in role_keywords.items():
            if any(var in query_lower for var in variations):
                keywords['roles'].append(role)
        
        return keywords
    
    def score_assessment(self, assessment: Dict, keywords: Dict) -> float:
        """Score assessment based on keyword matching"""
        score = 0.0
        name_lower = assessment['name'].lower()
        test_type = assessment.get('test_type', '')
        
        # CRITICAL: Match programming languages FIRST (HIGHEST priority)
        for lang in keywords['languages']:
            # Exact match in name
            if lang in name_lower:
                score += 100.0  # MASSIVE boost for exact tech match
                
                # Extra boost for specific variations
                if 'advanced' in name_lower:
                    score += 20.0
                if 'entry' in name_lower and keywords['level'] == 'entry':
                    score += 15.0
                if 'new' in name_lower:
                    score += 10.0  # Newer tests
        
        # Match soft skills (SECONDARY)
        for skill in keywords['soft_skills']:
            if any(word in name_lower for word in skill.split()):
                score += 50.0  # Direct skill name match
            elif 'P' in test_type:  # Personality type for soft skills
                score += 20.0
            
            # Specific soft skill matches
            if 'collaborat' in skill and ('team' in name_lower or 'interpersonal' in name_lower):
                score += 30.0
            if 'communication' in skill and 'communication' in name_lower:
                score += 40.0
        
        # Match roles
        for role in keywords['roles']:
            if role in name_lower:
                score += 60.0
        
        # Match level
        if keywords['level']:
            if keywords['level'] in name_lower:
                score += 25.0
        
        # BOOST test types based on query intent
        if keywords['languages'] and 'K' in test_type:
            score += 30.0  # Knowledge & Skills for technical
        if keywords['soft_skills'] and 'P' in test_type:
            score += 25.0  # Personality for soft skills
        if keywords['roles']:
            if 'B' in test_type:  # Biodata/SJT
                score += 15.0
        
        # Special boost for specific combinations
        if 'S' in test_type and keywords['languages']:
            score += 20.0  # Simulations for technical roles
        
        # Penalize if completely irrelevant
        has_any_match = (
            any(lang in name_lower for lang in keywords['languages']) or
            any(skill.split()[0] in name_lower for skill in keywords['soft_skills']) or
            any(role in name_lower for role in keywords['roles'])
        )
        
        if not has_any_match and (keywords['languages'] or keywords['soft_skills']):
            score -= 50.0  # Heavy penalty for irrelevant
        
        return score
    
    def recommend(self, query: str, num_recommendations=10) -> List[Dict]:
        """Get recommendations using keyword matching"""
        print(f"\n🔍 Processing: {query[:80]}...")
        
        # Extract keywords
        keywords = self.extract_keywords(query)
        print(f"   Keywords: {keywords}")
        
        # Score all assessments
        scored_assessments = []
        for assessment in self.assessments:
            score = self.score_assessment(assessment, keywords)
            scored_assessments.append((score, assessment))
        
        # Sort by score
        scored_assessments.sort(reverse=True, key=lambda x: x[0])
        
        # Get top candidates
        top_candidates = [a for s, a in scored_assessments if s > 0][:50]
        
        if not top_candidates:
            # Fallback to first assessments
            print("⚠️ No keyword matches, using general assessments")
            return self.assessments[:num_recommendations]
        
        print(f"✓ Found {len(top_candidates)} candidates")
        
        # Balance recommendations
        results = self._balance_recommendations(top_candidates, keywords, num_recommendations)
        
        # Show what we're returning
        print(f"   Returning {len(results)} recommendations")
        return results
    
    def _balance_recommendations(self, candidates: List[Dict], keywords: Dict, num: int) -> List[Dict]:
        """Balance between technical (K) and soft skills (P)"""
        # Determine ratio based on query
        has_tech = bool(keywords['languages'] or 'developer' in keywords['roles'])
        has_soft = bool(keywords['soft_skills'])
        
        if has_tech and has_soft:
            # Both mentioned - 70% tech, 30% soft (prioritize tech more)
            tech_count = int(num * 0.7)
            soft_count = num - tech_count
        elif has_tech:
            # Only tech - 90% tech, 10% soft
            tech_count = int(num * 0.9)
            soft_count = num - tech_count
        elif has_soft:
            # Only soft - 20% tech, 80% soft
            tech_count = int(num * 0.2)
            soft_count = num - tech_count
        else:
            # Neither - slightly favor diverse types
            tech_count = int(num * 0.6)
            soft_count = num - tech_count
        
        # Separate by test type
        tech_assessments = [a for a in candidates if 'K' in a.get('test_type', '') or 'S' in a.get('test_type', '')]
        soft_assessments = [a for a in candidates if 'P' in a.get('test_type', '')]
        other_assessments = [a for a in candidates if 'K' not in a.get('test_type', '') and 'P' not in a.get('test_type', '') and 'S' not in a.get('test_type', '')]
        
        # Build results ensuring diversity of tech skills when multiple mentioned
        results = []
        
        # If multiple languages mentioned, try to get variety
        if len(keywords['languages']) > 1:
            # Try to get assessments for each language
            for lang in keywords['languages']:
                lang_assessments = [a for a in tech_assessments if lang in a['name'].lower() and a not in results]
                results.extend(lang_assessments[:2])  # Get 2 per language
        
        # Fill remaining tech slots
        remaining_tech = [a for a in tech_assessments if a not in results]
        while len([r for r in results if 'K' in r.get('test_type', '') or 'S' in r.get('test_type', '')]) < tech_count and remaining_tech:
            results.append(remaining_tech.pop(0))
        
        # Add soft skills
        results.extend(soft_assessments[:soft_count])
        
        # Fill remaining with others
        while len(results) < num and other_assessments:
            results.append(other_assessments.pop(0))
        
        # Fill remaining with any candidates
        remaining = [a for a in candidates if a not in results]
        while len(results) < num and remaining:
            results.append(remaining.pop(0))
        
        return results[:num]
    
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
    engine = KeywordRecommendationEngine()
    
    queries = [
        "I am hiring for Java developers who can also collaborate effectively with my business teams.",
        "Looking to hire mid-level professionals who are proficient in Python, SQL and Java Script.",
        "I want to hire new graduates for a sales role in my company"
    ]
    
    for query in queries:
        print("\n" + "="*70)
        results = engine.recommend(query, num_recommendations=10)
        
        print(f"\nQuery: {query[:60]}...")
        print(f"\nTop 10 Recommendations:")
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['name']} (Type: {r.get('test_type', 'N/A')})")
        
        # Show type distribution
        type_counts = {}
        for r in results:
            types = r.get('test_type', 'N/A').split()
            for t in types:
                type_counts[t] = type_counts.get(t, 0) + 1
        print(f"\n📊 Distribution: {type_counts}")


if __name__ == "__main__":
    print("="*70)
    print("KEYWORD-ONLY RECOMMENDATION ENGINE")
    print("NO API KEY NEEDED!")
    print("="*70)
    test_engine()