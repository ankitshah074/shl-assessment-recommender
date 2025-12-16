"""
Streamlit Frontend for SHL Assessment Recommendation System
Simple, beautiful web interface
"""

import streamlit as st
import requests
import pandas as pd
from keyword_only_recommender import KeywordRecommendationEngine

# Page config
st.set_page_config(
    page_title="SHL Assessment Recommender",
    page_icon="🎯",
    layout="wide"
)

# Initialize engine (for local mode)
@st.cache_resource
def load_engine():
    return KeywordRecommendationEngine()

engine = load_engine()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .assessment-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🎯 SHL Assessment Recommender</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Find the perfect assessments for your hiring needs</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.write("""
    This AI-powered system helps you find the most relevant SHL assessments 
    for your job requirements.
    
    **How to use:**
    1. Enter your job description or requirements
    2. Click "Get Recommendations"
    3. Review the suggested assessments
    """)
    
    st.divider()
    
    st.header("📊 Statistics")
    st.metric("Total Assessments", f"{len(engine.assessments)}")
    st.metric("Test Types", "7")
    
    st.divider()
    
    st.header("🏷️ Test Types")
    st.write("""
    - **K**: Knowledge & Skills
    - **P**: Personality & Behavior
    - **B**: Biodata & SJT
    - **A**: Ability & Aptitude
    - **S**: Simulations
    """)

# Main area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Enter Your Requirements")
    
    # Query input
    query = st.text_area(
        "Job Description or Requirements",
        height=150,
        placeholder="Example: I am hiring for Java developers who can also collaborate effectively with my business teams. Looking for an assessment that can be completed in 40 minutes.",
        help="Describe the role, skills needed, and any other requirements"
    )
    
    # Number of recommendations
    num_recs = st.slider(
        "Number of Recommendations",
        min_value=5,
        max_value=10,
        value=10,
        help="How many assessment recommendations do you want?"
    )

with col2:
    st.header("Quick Examples")
    
    if st.button("🔧 Java Developer"):
        query = "I am hiring for Java developers who can also collaborate effectively with my business teams."
        st.rerun()
    
    if st.button("📊 Data Analyst"):
        query = "Looking to hire mid-level professionals who are proficient in Python, SQL and JavaScript."
        st.rerun()
    
    if st.button("💼 Sales Representative"):
        query = "I want to hire new graduates for a sales role in my company, the budget is for about an hour for each test."
        st.rerun()

# Get recommendations button
if st.button("🚀 Get Recommendations", type="primary", use_container_width=True):
    if not query:
        st.error("⚠️ Please enter a job description or requirements")
    else:
        with st.spinner("🔍 Finding the best assessments for you..."):
            # Get recommendations
            results = engine.recommend(query, num_recommendations=num_recs)
            
            # Display results
            st.success(f"✅ Found {len(results)} recommended assessments!")
            
            st.divider()
            st.header("📋 Recommended Assessments")
            
            # Create tabs
            tab1, tab2 = st.tabs(["📊 Table View", "📄 Detailed View"])
            
            with tab1:
                # Table view
                df = pd.DataFrame([
                    {
                        "Rank": i+1,
                        "Assessment Name": r['name'],
                        "Test Type": r.get('test_type', 'N/A'),
                        "URL": r['url']
                    }
                    for i, r in enumerate(results)
                ])
                
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "URL": st.column_config.LinkColumn("Assessment Link")
                    }
                )
                
                # Download button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name="shl_recommendations.csv",
                    mime="text/csv"
                )
            
            with tab2:
                # Detailed view
                for i, result in enumerate(results, 1):
                    with st.container():
                        st.markdown(f"""
                        <div class="assessment-card">
                            <h3>{i}. {result['name']}</h3>
                            <p><strong>Test Type:</strong> {result.get('test_type', 'N/A')}</p>
                            <p><strong>URL:</strong> <a href="{result['url']}" target="_blank">{result['url']}</a></p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Show type distribution
            st.divider()
            st.header("📊 Test Type Distribution")
            
            type_counts = {}
            for r in results:
                types = r.get('test_type', 'N/A').split()
                for t in types:
                    type_counts[t] = type_counts.get(t, 0) + 1
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Knowledge (K)", type_counts.get('K', 0))
            with col2:
                st.metric("Personality (P)", type_counts.get('P', 0))
            with col3:
                st.metric("Simulations (S)", type_counts.get('S', 0))
            with col4:
                st.metric("Other", sum(v for k, v in type_counts.items() if k not in ['K', 'P', 'S']))

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>SHL Assessment Recommendation System | Built by Ankit Shah using Streamlit</p>
    <p>Data Source: SHL Assessments Catalog</p>
</div>
""", unsafe_allow_html=True)