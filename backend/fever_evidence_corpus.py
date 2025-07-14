import os
import json
import pickle
import numpy as np
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer
import faiss
import wikipediaapi
from datasets import load_dataset
import requests
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FEVEREvidenceCorpus:
    def __init__(
        self, cache_dir: str = "./fever_cache", model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize FEVER evidence corpus with Wikipedia articles and semantic search.

        Args:
            cache_dir: Directory to cache Wikipedia articles and embeddings
            model_name: Sentence transformer model for semantic search
        """
        self.cache_dir = cache_dir
        self.model_name = model_name
        self.embedding_model = None
        self.index = None
        self.articles = {}
        self.article_embeddings = {}

        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs(os.path.join(cache_dir, "articles"), exist_ok=True)
        os.makedirs(os.path.join(cache_dir, "embeddings"), exist_ok=True)

        # Initialize Wikipedia API
        self.wiki = wikipediaapi.Wikipedia(
            language="en",
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent="MisinfoDetector/1.0",
        )

        self._load_or_create_corpus()

    def _load_or_create_corpus(self):
        """Load existing corpus or create new one from FEVER dataset."""
        cache_file = os.path.join(self.cache_dir, "corpus_cache.pkl")

        if os.path.exists(cache_file):
            logger.info("Loading existing FEVER corpus cache...")
            self._load_cached_corpus(cache_file)
        else:
            logger.info("Creating new FEVER evidence corpus...")
            self._create_corpus_from_fever()
            self._save_corpus_cache(cache_file)

    def _load_cached_corpus(self, cache_file: str):
        """Load corpus from cache."""
        with open(cache_file, "rb") as f:
            cached_data = pickle.load(f)
            self.articles = cached_data["articles"]
            self.article_embeddings = cached_data["embeddings"]

        # Load embedding model and index
        self.embedding_model = SentenceTransformer(self.model_name)
        self._rebuild_index()

    def _save_corpus_cache(self, cache_file: str):
        """Save corpus to cache."""
        cached_data = {"articles": self.articles, "embeddings": self.article_embeddings}
        with open(cache_file, "wb") as f:
            pickle.dump(cached_data, f)

    def _create_corpus_from_fever(self):
        """Create evidence corpus from FEVER dataset."""
        logger.info("Loading FEVER dataset...")

        # Load FEVER dataset (streaming to handle large size)
        fever_dataset = load_dataset(
            "fever", "v1.0", streaming=True, trust_remote_code=True
        )

        # Initialize embedding model
        self.embedding_model = SentenceTransformer(self.model_name)

        # Extract unique Wikipedia articles from FEVER
        unique_articles = set()

        logger.info("Extracting unique Wikipedia articles from FEVER...")
        # For streaming datasets, we need to iterate through the data differently
        try:
            # Try to get train split first
            train_dataset = fever_dataset["train"]
            for example in tqdm(train_dataset, desc="Processing train"):
                if "evidence" in example and example["evidence"]:
                    for evidence_item in example["evidence"]:
                        if isinstance(evidence_item, list) and len(evidence_item) > 0:
                            for evidence in evidence_item:
                                if isinstance(evidence, dict) and "title" in evidence:
                                    unique_articles.add(evidence["title"])
        except Exception as e:
            logger.warning(f"Could not process train split: {e}")

        # Try other splits if available
        for split_name in ["validation", "test", "dev"]:
            try:
                split_dataset = fever_dataset[split_name]
                for example in tqdm(split_dataset, desc=f"Processing {split_name}"):
                    if "evidence" in example and example["evidence"]:
                        for evidence_item in example["evidence"]:
                            if (
                                isinstance(evidence_item, list)
                                and len(evidence_item) > 0
                            ):
                                for evidence in evidence_item:
                                    if (
                                        isinstance(evidence, dict)
                                        and "title" in evidence
                                    ):
                                        unique_articles.add(evidence["title"])
            except Exception as e:
                logger.warning(f"Could not process {split_name} split: {e}")

        logger.info(f"Found {len(unique_articles)} unique Wikipedia articles")

        if len(unique_articles) == 0:
            logger.warning("No articles found, using sample articles for demo")
            # Use some sample articles for demo purposes
            sample_articles = [
                "Climate change",
                "Vaccine",
                "COVID-19",
                "Election fraud",
                "Flat Earth",
                "Moon landing",
                "Evolution",
                "Global warming",
            ]
            self._fetch_wikipedia_articles(sample_articles)
        else:
            # Fetch Wikipedia articles
            self._fetch_wikipedia_articles(
                list(unique_articles)[:1000]
            )  # Limit to first 1000 for demo

        # Create embeddings
        self._create_embeddings()

    def _fetch_wikipedia_articles(self, article_titles: List[str]):
        """Fetch Wikipedia articles by title."""
        logger.info(f"Fetching {len(article_titles)} Wikipedia articles...")

        for title in tqdm(article_titles, desc="Fetching articles"):
            try:
                # Try to get the page
                page = self.wiki.page(title)

                if page.exists():
                    # Extract text content
                    content = page.text

                    # Split into chunks (Wikipedia articles can be very long)
                    chunks = self._split_article_into_chunks(content, title)

                    for i, chunk in enumerate(chunks):
                        chunk_id = f"{title}_{i}"
                        self.articles[chunk_id] = {
                            "title": title,
                            "content": chunk,
                            "chunk_id": i,
                            "full_url": page.fullurl,
                        }

            except Exception as e:
                logger.warning(f"Error fetching article '{title}': {e}")
                continue

        logger.info(f"Successfully fetched {len(self.articles)} article chunks")

    def _split_article_into_chunks(
        self, content: str, title: str, max_chunk_size: int = 1000
    ) -> List[str]:
        """Split Wikipedia article into manageable chunks."""
        sentences = content.split(". ")
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks if chunks else [content]

    def _create_embeddings(self):
        """Create embeddings for all article chunks."""
        logger.info("Creating embeddings for article chunks...")

        article_texts = list(self.articles.keys())
        article_contents = [self.articles[aid]["content"] for aid in article_texts]

        # Create embeddings in batches
        batch_size = 32
        all_embeddings = []

        for i in tqdm(
            range(0, len(article_contents), batch_size), desc="Creating embeddings"
        ):
            batch = article_contents[i : i + batch_size]
            embeddings = self.embedding_model.encode(batch, show_progress_bar=False)
            all_embeddings.extend(embeddings)

        # Store embeddings
        for aid, embedding in zip(article_texts, all_embeddings):
            self.article_embeddings[aid] = embedding

        # Build FAISS index
        self._build_faiss_index()

    def _build_faiss_index(self):
        """Build FAISS index for fast similarity search."""
        logger.info("Building FAISS index...")

        embeddings = np.array(list(self.article_embeddings.values())).astype("float32")
        dimension = embeddings.shape[1]

        # Create FAISS index
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.index.add(embeddings)

        logger.info(f"FAISS index built with {self.index.ntotal} vectors")

    def _rebuild_index(self):
        """Rebuild FAISS index from cached embeddings."""
        if not self.article_embeddings:
            return

        embeddings = np.array(list(self.article_embeddings.values())).astype("float32")
        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)

    def search_evidence(self, claim: str, top_k: int = 5) -> List[Dict]:
        """
        Search for evidence related to a claim.

        Args:
            claim: The claim to find evidence for
            top_k: Number of top results to return

        Returns:
            List of evidence documents with relevance scores
        """
        if not self.index or not self.embedding_model:
            logger.error("Corpus not properly initialized")
            return []

        # Encode the claim
        claim_embedding = self.embedding_model.encode([claim])

        # Search the index
        scores, indices = self.index.search(claim_embedding, top_k)

        # Get article IDs
        article_ids = list(self.articles.keys())

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(article_ids):
                article_id = article_ids[idx]
                article = self.articles[article_id]

                results.append(
                    {
                        "article_id": article_id,
                        "title": article["title"],
                        "content": article["content"],
                        "relevance_score": float(score),
                        "url": article.get("full_url", ""),
                        "chunk_id": article["chunk_id"],
                    }
                )

        return results

    def get_article_by_title(self, title: str) -> Optional[Dict]:
        """Get a specific article by title."""
        for article_id, article in self.articles.items():
            if article["title"] == title:
                return article
        return None

    def get_corpus_stats(self) -> Dict:
        """Get statistics about the corpus."""
        return {
            "total_articles": len(
                set(article["title"] for article in self.articles.values())
            ),
            "total_chunks": len(self.articles),
            "total_embeddings": len(self.article_embeddings),
            "index_size": self.index.ntotal if self.index else 0,
        }


# Global instance
fever_corpus = None


def get_fever_corpus() -> FEVEREvidenceCorpus:
    """Get or create global FEVER corpus instance."""
    global fever_corpus
    if fever_corpus is None:
        fever_corpus = FEVEREvidenceCorpus()
    return fever_corpus
