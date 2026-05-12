#!/usr/bin/env python3
"""
Data Processing Pipeline: Convert raw papers.json to processed_papers.json

Pipeline Steps:
1. Load raw papers from data/papers.json
2. Clean text (remove LaTeX, URLs, normalize whitespace)
3. Extract keywords using TF-IDF
4. Save processed papers to data/processed_papers.json

Usage:
    python scripts/process_papers.py
"""

import json
import re
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer


def clean_text(text: str) -> str:
    """Clean text by removing LaTeX, URLs, and normalizing whitespace"""
    if not text:
        return ""
    
    # Fix encoding issues
    text = text.encode('utf-8', 'ignore').decode('utf-8')
    
    # Remove LaTeX math expressions  
    text = re.sub(r'\$.*?\$', '', text)
    text = re.sub(r'\\[a-zA-Z]+\{.*?\}', '', text)
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def extract_keywords_tfidf(texts: list[str], top_n: int = 10) -> list[list[str]]:
    """
    Extract keywords from abstracts using TF-IDF.
    
    Args:
        texts: List of cleaned abstracts
        top_n: Number of top keywords to extract per document
        
    Returns:
        List of keyword lists (one per document)
    """
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=2,  # Ignore terms that appear in less than 2 documents
        max_df=0.8  # Ignore terms that appear in more than 80% of documents
    )
 
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()
 
    keywords_per_doc = []
    for row in tfidf_matrix:
        scores = zip(feature_names, np.asarray(row.todense()).flatten())
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
        top_keywords = [word for word, score in sorted_scores[:top_n] if score > 0]
        keywords_per_doc.append(top_keywords)
 
    return keywords_per_doc


def process_papers(input_file: str = "data/papers.json", 
                   output_file: str = "data/processed_papers.json") -> int:
    """
    Process raw papers and save to processed format.
    
    Args:
        input_file: Path to raw papers JSON
        output_file: Path to save processed papers JSON
        
    Returns:
        Number of papers processed
    """
    # Load raw papers
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ Error: {input_file} not found")
        return 0
    
    print(f"📄 Loading papers from {input_file}...")
    with open(input_path) as f:
        papers = json.load(f)
    
    print(f"📊 Loaded {len(papers)} papers")
    
    # Clean abstracts and extract keywords
    print("🧹 Cleaning abstracts and extracting keywords...")
    cleaned_abstracts = []
    
    for i, paper in enumerate(papers):
        if (i + 1) % 500 == 0:
            print(f"   Processing {i + 1}/{len(papers)}...")
        paper['abstract'] = clean_text(paper.get('abstract', ''))
        cleaned_abstracts.append(paper['abstract'])
    
    # Extract keywords using TF-IDF
    print("🔑 Extracting keywords using TF-IDF...")
    keywords_list = extract_keywords_tfidf(cleaned_abstracts)
    
    for paper, keywords in zip(papers, keywords_list):
        paper['keywords'] = keywords
    
    # Save processed papers
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"💾 Saving to {output_file}...")
    with open(output_path, 'w') as f:
        json.dump(papers, f, indent=2)
    
    print(f"✅ Successfully processed {len(papers)} papers")
    print(f"📁 Saved to {output_file}")
    
    return len(papers)


if __name__ == "__main__":
    process_papers()
