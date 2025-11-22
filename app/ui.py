import streamlit as st
import sys
import os
import time
import base64

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.search_client import SearchClient

# Page Config
st.set_page_config(
    page_title="Food Intelligence Platform",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if 'search_limit' not in st.session_state:
    st.session_state.search_limit = 50
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""

# Custom CSS for Professional UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Background - Light warm gray */
    .stApp {
        background: linear-gradient(180deg, #fafafa 0%, #f5f5f5 100%);
    }

    /* Hero Section */
    .hero-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.95);
        font-weight: 400;
    }

    /* Search Input Styling */
    .stTextInput > div > div > input {
        border-radius: 12px;
        padding: 18px 24px;
        font-size: 1.05rem;
        border: 2px solid #d1d5db;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        transition: all 0.2s ease;
        background-color: #ffffff;
        color: #111827;
        font-weight: 500;
    }
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
        outline: none;
    }
    .stTextInput > div > div > input::placeholder {
        color: #9ca3af;
    }

    /* Suggestions Section */
    .suggestions-header {
        font-size: 0.95rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 12px;
        margin-top: 16px;
    }

    /* Recipe Card - High Contrast */
    .recipe-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        border: 2px solid #e5e7eb;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .recipe-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(102, 126, 234, 0.15);
        border-color: #667eea;
    }
    .recipe-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 14px;
        line-height: 1.3;
    }
    .recipe-desc {
        color: #4b5563;
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 16px;
    }
    
    /* Badges - High Contrast */
    .badges {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-bottom: 16px;
    }
    .badge {
        padding: 7px 14px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-cuisine { background: #dbeafe; color: #1e40af; }
    .badge-diet { background: #dcfce7; color: #166534; }
    .badge-time { background: #fed7aa; color: #9a3412; }

    /* Streamlit Button Styling - High Contrast */
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        border: 2px solid #667eea;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff !important;
        font-weight: 600;
        padding: 0.7rem 1.2rem;
        transition: all 0.2s;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        font-size: 0.95rem;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #5568d3 0%, #6a4193 100%);
    }
    div.stButton > button:active {
        transform: translateY(0);
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        font-weight: 600;
        color: #374151;
    }

    /* Sidebar - High Contrast */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 2px solid #e5e7eb;
    }
    
    /* Results Count */
    .results-info {
        font-size: 1rem;
        color: #374151;
        font-weight: 500;
        padding: 12px 0;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize client
@st.cache_resource
def get_client():
    return SearchClient()

client = get_client()

# --- Sidebar ---
with st.sidebar:
    st.markdown("# 🍳 Kitchen Tools")
    st.markdown("---")
    
    st.markdown("### 🎯 Filters")
    st.markdown("Refine your search results:")
    f_cuisine = st.selectbox("**Cuisine**", ["All", "Indian", "Continental", "Mexican", "Italian", "Chinese", "Thai"], key="cuisine_filter")
    f_diet = st.selectbox("**Diet Type**", ["All", "Vegetarian", "Non Vegeterian", "High Protein Vegetarian", "Diabetic Friendly", "Vegan", "Gluten Free"], key="diet_filter")
    f_course = st.selectbox("**Course**", ["All", "Lunch", "Dinner", "Snack", "Breakfast", "Dessert"], key="course_filter")
    
    st.markdown("---")
    
    st.markdown("### 🥕 Ingredient Helper")
    st.markdown("Look up ingredient info & substitutes:")
    ing_query = st.text_input("Search ingredient", placeholder="e.g. 'galangal', 'paneer'", key="ing_search")
    
    if ing_query:
        with st.spinner("🔍 Searching..."):
            ing_results = client.autocomplete_ingredient(ing_query)
            if not ing_results:
                st.warning("❌ No ingredients found.")
            else:
                for hit in ing_results[:3]:  # Show max 3 results
                    doc = hit['document']
                    with st.container():
                        st.markdown(f"**✓ {doc['ingredient'].title()}**")
                        if doc.get('synonym'):
                            st.caption(f"**Also known as:** {', '.join(doc['synonym'][:3])}")
                        if doc.get('replacements'):
                            st.success(f"**Substitute:** {', '.join(doc['replacements'][:3])}")
                        st.divider()
    
    st.markdown("---")
    st.markdown("**📊 Platform Stats**")
    st.caption(f"✓ Version 1.0.0")
    st.caption(f"✓ 9,600+ Recipes")
    st.caption(f"✓ Semantic Search Enabled")

# --- Main Content ---

# Header
st.markdown("""
<div class="hero-box">
    <div class="hero-title">Food Intelligence Platform</div>
    <div class="hero-subtitle">Discover delicious recipes with semantic search</div>
</div>
""", unsafe_allow_html=True)

# Search Area
query = st.text_input("Search", placeholder="Search for 'spicy chicken dinner' or 'vegan dessert'...", key="main_search", label_visibility="collapsed")

# Auto-suggestions as you type (shown even with partial query)
if query and len(query) >= 2:
    with st.spinner(""):
        suggestions = client.autocomplete_query(query, limit=5)
        if suggestions:
            st.markdown('<div class="suggestions-header">💡 Related Searches</div>', unsafe_allow_html=True)
            # Display suggestions as clickable buttons
            sugg_cols = st.columns(min(len(suggestions), 5))
            for i, hit in enumerate(suggestions):
                sugg_text = hit['document']['query']
                with sugg_cols[i]:
                    if st.button(f"🔍 {sugg_text}", key=f"sugg_{i}", use_container_width=True):
                        query = sugg_text
                        st.session_state.last_query = ""
                        st.rerun()
            st.markdown("---")

# Update session state
if query and query != st.session_state.last_query:
    st.session_state.search_limit = 50
    st.session_state.last_query = query

# Results
if query:
    start_time = time.time()
    try:
        filters = {
            'cuisine': f_cuisine,
            'diet': f_diet,
            'course': f_course
        }
        
        search_result = client.search(query, limit=st.session_state.search_limit, filters=filters)
        results = search_result['hits']
        duration = time.time() - start_time
        
        st.markdown(f'<div class="results-info">📊 Found <strong>{search_result["found"]}</strong> recipes in {duration:.3f} seconds</div>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Display results in a single column for better visibility
        for i, hit in enumerate(results):
            doc = hit['document']
            
            # Render Card
            st.markdown(f"""
            <div class="recipe-card">
                <div class="recipe-title">{i+1}. {doc['name']}</div>
                <div class="badges">
                    <span class="badge badge-cuisine">🌍 {doc['cuisine']}</span>
                    <span class="badge badge-diet">🥗 {doc['diet']}</span>
                    <span class="badge badge-time">⏱️ {doc['total_time']}m</span>
                </div>
                <div class="recipe-desc">{doc['description']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Native Streamlit Expander for details
            with st.expander("📖 View Full Recipe Details", expanded=False):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("#### 🛒 Ingredients")
                    for ing in doc['ingredients']:
                        st.markdown(f"• {ing}")
                
                with col2:
                    st.markdown("#### 📝 Instructions")
                    if 'instructions' in doc and doc['instructions']:
                        try:
                            import ast
                            instr = doc['instructions']
                            if isinstance(instr, str) and instr.startswith('['):
                                instr_list = ast.literal_eval(instr)
                                for idx, step in enumerate(instr_list, 1):
                                    if isinstance(step, dict):
                                        st.markdown(f"**{idx}.** {step.get('instructions', '')}")
                                    else:
                                        st.markdown(f"**{idx}.** {step}")
                            else:
                                st.write(instr)
                        except:
                            st.write(instr)
                    else:
                        st.info("Instructions not available for this recipe.")
                
                if doc.get('url'):
                    st.markdown("---")
                    st.link_button("🔗 View Original Recipe", doc['url'], use_container_width=True)
            
            st.markdown("")

        # Load More Button
        if len(results) < search_result['found']:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(f"⬇️ Load More Results ({len(results)}/{search_result['found']})", use_container_width=True):
                    st.session_state.search_limit += 50
                    st.rerun()
            
    except Exception as e:
        st.error(f"Search failed: {e}")

else:
    # Empty State - Show example searches
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #374151; font-weight: 600;'>🔍 Try searching for...</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    example_queries = [
        "🥞 High protein vegetarian breakfast",
        "🍰 Gluten-free desserts with chocolate",
        "🐟 Traditional Kerala fish curry",
        "⚡ Quick 15-minute snacks",
        "🌶️ Spicy Indian dinner recipes",
        "🥗 Low calorie vegan meals"
    ]
    
    c1, c2 = st.columns(2)
    for i, example in enumerate(example_queries):
        with (c1 if i % 2 == 0 else c2):
            if st.button(example, key=f"ex_{i}", use_container_width=True):
                # Strip emoji for actual search
                clean_query = ' '.join([word for word in example.split() if not any(char in word for char in '🥞🍰🐟⚡🌶️🥗')])
                st.session_state.main_search = clean_query.strip()
                st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Show some stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 Total Recipes", "9,600+")
    with col2:
        st.metric("🌍 Cuisines", "15+")
    with col3:
        st.metric("🥗 Diet Types", "7+")


