#!/usr/bin/env python3
"""
Script to initialize the FEVER evidence corpus.
This script downloads and processes the FEVER dataset to create a searchable evidence corpus.
"""

import os
import sys
import logging
from fever_evidence_corpus import FEVEREvidenceCorpus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Initialize the FEVER evidence corpus."""
    logger.info("Starting FEVER evidence corpus initialization...")
    
    try:
        # Initialize the corpus
        corpus = FEVEREvidenceCorpus()
        
        # Get and display statistics
        stats = corpus.get_corpus_stats()
        logger.info("FEVER corpus initialization completed successfully!")
        logger.info(f"Corpus statistics:")
        logger.info(f"  - Total unique articles: {stats['total_articles']}")
        logger.info(f"  - Total chunks: {stats['total_chunks']}")
        logger.info(f"  - Total embeddings: {stats['total_embeddings']}")
        logger.info(f"  - FAISS index size: {stats['index_size']}")
        
        # Test search functionality
        logger.info("Testing search functionality...")
        test_query = "climate change"
        results = corpus.search_evidence(test_query, top_k=3)
        logger.info(f"Test search for '{test_query}' returned {len(results)} results")
        
        if results:
            logger.info("Sample result:")
            sample = results[0]
            logger.info(f"  - Title: {sample['title']}")
            logger.info(f"  - Relevance score: {sample['relevance_score']:.3f}")
            logger.info(f"  - Content preview: {sample['content'][:100]}...")
        
        logger.info("FEVER corpus is ready for use!")
        
    except Exception as e:
        logger.error(f"Error initializing FEVER corpus: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 