# ArXiv Research Paper Search Engine

A professional information retrieval system for academic papers using Elasticsearch, Python, and Streamlit.

**Coursework:** 6CS030 Big Data — University of Wolverhampton

## Overview

This project implements a complete search engine pipeline:

1. **Data Acquisition**: Fetch papers from arXiv API (500 per category, 2553 total)
2. **Data Processing**: Clean abstracts, extract keywords using TF-IDF
3. **Indexing**: Bulk index papers into Elasticsearch with BM25 ranking
4. **Search**: Multi-field query with field boosting (title^3, keywords^2, abstract^1)
5. **UI**: Professional Streamlit interface with results display

## Architecture

```
arXiv API
    ↓
src/arxiv_client.py → data/papers.json (raw)
    ↓
scripts/process_papers.py → data/processed_papers.json (cleaned + keywords)
    ↓
indexing/indexer.py → Elasticsearch Index
    ↓
query/search_engine.py ← app.py (Streamlit UI)
```

## Tech Stack

- **Language**: Python 3.10+
- **Search Engine**: Elasticsearch 8.13
- **API**: arXiv API (arxiv package)
- **Frontend**: Streamlit
- **NLP**: scikit-learn (TF-IDF), NLTK
- **Data**: JSON, pandas

## Quick Start

### 1. Install Dependencies

```bash
# Install from pyproject.toml
pip install -e .

# Or install manually
pip install elasticsearch>=8.0 streamlit>=1.28 pandas>=2.0 scikit-learn>=1.3 nltk>=3.8 arxiv>=1.4
```

### 2. Start Elasticsearch

**Option A: Docker (Recommended)**
```bash
docker run -d \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.13.0
```

**Option B: Local Installation**
```bash
# Download from https://www.elastic.co/downloads/elasticsearch
cd elasticsearch-8.13.0
./bin/elasticsearch
```

### 3. Fetch Papers from arXiv

```bash
python src/arxiv_client.py
```

This fetches ~500 papers from each category:
- cs.AI (Artificial Intelligence)
- cs.LG (Machine Learning)
- cs.CL (NLP)
- cs.CV (Computer Vision)
- cs.IR (Information Retrieval)
- cs.NE (Neural & Evolutionary)

**Output**: `data/papers.json` (raw data)

### 4. Process and Extract Keywords

```bash
python scripts/process_papers.py
```

This script:
- Cleans abstracts (removes LaTeX, URLs)
- Extracts top 10 keywords per paper using TF-IDF
- Normalizes whitespace

**Output**: `data/processed_papers.json` (cleaned data with keywords)

### 5. Create Index and Bulk Index Papers

```bash
python indexing/indexer.py
```

This:
- Creates Elasticsearch index with English analyzer
- Bulk indexes 2553 papers
- Verifies indexing success

**Output**: Elasticsearch index ready for search

### 6. Start Streamlit UI

```bash
streamlit run app.py
```

Then open: http://localhost:8501

## Project Structure

```
research_paper_engine/
├── app.py                          # Streamlit frontend
├── main.py                         # CLI demo script
├── pyproject.toml                  # Dependencies
├── README.md                       # This file
├── CODE_REVIEW.md                  # Full code review
│
├── src/
│   └── arxiv_client.py            # Fetch papers from arXiv API
│
├── scripts/
│   └── process_papers.py          # Clean data & extract keywords
│
├── indexing/
│   ├── es_client.py               # Elasticsearch connection
│   ├── index_mapping.py           # Index schema & settings
│   └── indexer.py                 # Bulk indexing script
│
├── query/
│   ├── query_builder.py           # Build BM25 multi-match queries
│   └── search_engine.py           # Execute searches & format results
│
├── notebook/
│   ├── Data_Exploration.ipynb     # EDA & keyword extraction (reference)
│   └── .ipynb_checkpoints/
│
├── data/
│   ├── papers.json                # Raw papers (2553 unique)
│   └── processed_papers.json      # Cleaned papers with keywords
│
└── .gitignore
```

## Features

### Search Capabilities
- **Multi-field search**: title, abstract, keywords, authors
- **Field boosting**: title (3x) > keywords (2x) > abstract (1x)
- **Category filtering**: cs.AI, cs.LG, cs.CL, cs.CV, cs.IR, cs.NE
- **Fuzzy matching**: Handles typos (e.g., "tranformer" → "transformer")
- **BM25 ranking**: Probabilistic relevance framework

### UI Features
- Search bar with placeholder guidance
- Category dropdown filter
- Results limit selector (10, 20, 50)
- Result cards showing:
  - Rank & relevance score
  - Title (clickable link to arXiv)
  - Authors (first 3 shown)
  - Categories
  - Keywords (top 5)
  - Abstract snippet (first ~50 words)
  - Expandable full abstract
  - Links to arXiv abstract and PDF

### Data Pipeline
- Automatic deduplication by arxiv_id
- LaTeX equation removal
- URL sanitization
- Whitespace normalization
- TF-IDF keyword extraction (ngram_range=(1,2))

## Usage Examples

### CLI Search Example
```bash
python main.py
```

Output:
```
🔍 Found 42 results for 'object detection' (showing top 10)
[8.742] Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks
  Authors   : ['Shaoqing Ren', 'Kaiming He', 'Ross Girshick']
  Keywords  : ['object detection', 'region proposal', 'fast r-cnn']
  URL       : http://arxiv.org/abs/1506.01497v3
```

### Streamlit Search Examples
1. **Query**: "transformer attention" → Returns papers on attention mechanisms & transformers
2. **Query**: "graph neural networks" + Filter: cs.LG → Returns ML-specific graph papers
3. **Query**: "quantum computing" → Returns quantum computation papers

## Configuration

### Environment Variables
Create `.env` file to customize:
```bash
ES_URL=http://localhost:9200
ARXIV_CATEGORIES=cs.AI,cs.LG,cs.CL,cs.CV,cs.IR,cs.NE
PAPERS_PER_CATEGORY=500
```

### Search Parameters (in `app.py`)
```python
top_n = [10, 20, 50]  # Adjustable result limits
category_filter = None  # Filter by arXiv category
```

### TF-IDF Settings (in `scripts/process_papers.py`)
```python
TfidfVectorizer(
    max_features=5000,
    stop_words='english',
    ngram_range=(1, 2),  # Unigrams + bigrams
    min_df=2,            # Minimum document frequency
    max_df=0.8           # Maximum document frequency
)
```

## Troubleshooting

### Error: "Connection refused" when starting app
→ Elasticsearch is not running. Start it with Docker or local installation.

### Error: "Index not found"
→ Run: `python indexing/indexer.py` to create and populate index.

### No results found for a valid query
→ Query might not match keywords extracted by TF-IDF. Try broader terms.

### Slow queries
→ Check Elasticsearch status: `curl http://localhost:9200`
→ Verify index has documents: `curl http://localhost:9200/arxiv_papers/_count`

## Performance Metrics

| Metric | Value |
|--------|-------|
| Total Papers Indexed | 2,553 |
| Index Size | ~50 MB |
| Query Time (avg) | 50-200 ms |
| Indexing Time | ~30 seconds |
| BM25 Algorithm | Probabilistic relevance |

## Ranking & Relevance

The search uses **Elasticsearch BM25 algorithm** with:
- **Title boost**: 3x (most important)
- **Keywords boost**: 2x (moderate importance)
- **Abstract boost**: 1x (baseline)
- **Authors**: 1x (baseline)

**Example**: Query "transformer" returns papers where "transformer" appears in title first, then keywords, then abstract.

## Future Enhancements

1. **Vector Search**: Add semantic search using embeddings (Sentence-Transformers)
2. **Query Expansion**: Synonym support (ML → Machine Learning)
3. **Advanced Filtering**: Date range, author search, citation count
4. **Analytics**: Track popular queries, search trends
5. **Result Export**: CSV/JSON download
6. **Caching**: Cache frequent queries
7. **Pagination**: Proper result pagination
8. **Result Reranking**: Re-rank using BERT or other models

## References

- **Elasticsearch**: https://www.elastic.co/elasticsearch/
- **arXiv API**: https://arxiv.org/help/api/
- **TF-IDF**: https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
- **BM25**: https://en.wikipedia.org/wiki/Okapi_BM25
- **Streamlit**: https://streamlit.io/

## Author

Built for 6CS030 Big Data — University of Wolverhampton

## License

Educational use only (University of Wolverhampton coursework)
