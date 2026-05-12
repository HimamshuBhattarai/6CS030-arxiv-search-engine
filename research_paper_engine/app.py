import streamlit as st
from query.search_engine import search

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ArXiv Research Search Engine",
    page_icon="🔬",
    layout="wide"
)

# ── Startup Checks ────────────────────────────────────────────────────────────
@st.cache_resource
def check_elasticsearch():
    """Verify Elasticsearch connection on startup"""
    try:
        from indexing.es_client import es
        from indexing.index_mapping import INDEX_NAME
        
        if not es.ping():
            st.error("❌ Elasticsearch Connection Failed")
            st.info("Please ensure Elasticsearch is running on http://localhost:9200")
            st.stop()
            
        if not es.indices.exists(index=INDEX_NAME):
            st.error("❌ Index Not Found")
            st.info("Please run: python indexing/indexer.py")
            st.stop()
            
        return True
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("Please ensure all dependencies are installed and Elasticsearch is running")
        st.stop()

# Run startup checks
check_elasticsearch()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🔬 ArXiv Research Paper Search Engine")
st.caption("6CS030 Big Data — University of Wolverhampton")
st.divider()

# ── Search Bar ────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([4, 1, 1])

with col1:
    query = st.text_input("", placeholder="Search papers e.g. transformer attention mechanism...")

with col2:
    category = st.selectbox("Category", [
        "All", "cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.IR", "cs.NE"
    ])

with col3:
    top_n = st.selectbox("Results", [10, 20, 50])

search_btn = st.button("🔍 Search", use_container_width=True)

# ── Results ───────────────────────────────────────────────────────────────────
if search_btn and query:
    category_filter = None if category == "All" else category

    try:
        with st.spinner("Searching..."):
            results = search(query, category_filter=category_filter, top_n=top_n)

        if not results:
            st.warning("No results found. Try a different query.")
        else:
            st.success(f"Found results for **{query}**")
            st.info(f"📊 Results ranked by BM25 relevance score")
            st.divider()

            for i, r in enumerate(results, 1):
                with st.container():
                    # Title + Score
                    col_title, col_score = st.columns([5, 1])
                    with col_title:
                        st.markdown(f"### {i}. [{r['title']}]({r['url']})")
                    with col_score:
                        st.metric("Score", r['score'])

                    # Authors + Categories
                    col_a, col_b = st.columns(2)
                    with col_a:
                        authors_str = ", ".join(r['authors']) if r['authors'] else "Unknown"
                        st.markdown(f"👤 **Authors:** {authors_str}")
                    with col_b:
                        categories_str = ", ".join(r['categories']) if r['categories'] else "Unknown"
                        st.markdown(f"📂 **Categories:** {categories_str}")

                    # Keywords
                    if r['keywords']:
                        keywords_str = ", ".join(r['keywords'])
                        st.markdown(f"🏷️ **Keywords:** {keywords_str}")

                    # Abstract
                    with st.expander("📄 Abstract"):
                        st.write(r['abstract'] if r['abstract'] else "No abstract available")

                    # Buttons
                    col_url, col_pdf, _ = st.columns([1, 1, 4])
                    with col_url:
                        st.link_button("🔗 View on arXiv", r['url'])
                    with col_pdf:
                        st.link_button("📥 Download PDF", r['pdf_url'])

                    st.divider()
    
    except ValueError as e:
        st.error(f"❌ Invalid query: {str(e)}")
    except Exception as e:
        st.error(f"❌ Search failed: {str(e)}")
        st.info("Please ensure Elasticsearch is running and accessible")

elif search_btn and not query:
    st.warning("Please enter a search query.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center; color:gray;'>Built with arXiv API + Elasticsearch + Streamlit</div>",
    unsafe_allow_html=True
)