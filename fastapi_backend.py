"""
FastAPI Backend for SHL Assessment Recommendation System
This is your API server that will be deployed
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from keyword_only_recommender import KeywordRecommendationEngine

# Initialize FastAPI app
app = FastAPI(
    title="SHL Assessment Recommendation API",
    description="AI-powered assessment recommendation system",
    version="1.0.0"
)

# Add CORS middleware to allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize recommendation engine
print("Loading recommendation engine...")
engine = KeywordRecommendationEngine()
print("✓ Engine loaded successfully")


# Request/Response Models
class RecommendationRequest(BaseModel):
    query: str
    num_recommendations: Optional[int] = 10


class AssessmentResponse(BaseModel):
    assessment_name: str
    assessment_url: str
    test_type: str
    relevance_score: Optional[float] = None


class RecommendationResponse(BaseModel):
    query: str
    recommendations: List[AssessmentResponse]
    total_results: int


class HealthResponse(BaseModel):
    status: str
    message: str


# API Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - API info"""
    return {
        "status": "healthy",
        "message": "SHL Assessment Recommendation API is running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint as per assignment requirements"""
    return {
        "status": "healthy",
        "message": "API is operational"
    }


@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_assessments(request: RecommendationRequest):
    """
    Main recommendation endpoint
    
    Args:
        request: Contains query and optional num_recommendations
        
    Returns:
        RecommendationResponse with list of recommended assessments
    """
    try:
        # Validate input
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Limit recommendations between 1 and 10
        num_recs = max(1, min(request.num_recommendations, 10))
        
        # Get recommendations
        results = engine.recommend(request.query, num_recommendations=num_recs)
        
        # Format response
        recommendations = []
        for i, result in enumerate(results):
            recommendations.append(AssessmentResponse(
                assessment_name=result['name'],
                assessment_url=result['url'],
                test_type=result.get('test_type', 'N/A'),
                relevance_score=1.0 - (i * 0.05)  # Decreasing relevance
            ))
        
        return RecommendationResponse(
            query=request.query,
            recommendations=recommendations,
            total_results=len(recommendations)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/recommend", response_model=RecommendationResponse)
async def recommend_assessments_get(query: str, num_recommendations: int = 10):
    """
    GET version of recommend endpoint (for testing in browser)
    """
    return await recommend_assessments(
        RecommendationRequest(query=query, num_recommendations=num_recommendations)
    )


@app.get("/stats")
async def get_stats():
    """Get API statistics"""
    return {
        "total_assessments": len(engine.assessments),
        "api_version": "1.0.0",
        "status": "operational"
    }


# Run the server
if __name__ == "__main__":
    print("\n" + "="*70)
    print("Starting SHL Assessment Recommendation API")
    print("="*70)
    print("\nAPI will be available at:")
    print("  - http://localhost:8000")
    print("  - Health check: http://localhost:8000/health")
    print("  - Recommend: http://localhost:8000/recommend")
    print("\nAPI Documentation:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)