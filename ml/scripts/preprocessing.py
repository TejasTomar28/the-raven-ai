"""Scikit-learn compatible text preprocessing for document classification."""

import re
from functools import lru_cache

import nltk
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

_WORDNET_RESOURCE = "corpora/wordnet"


def ensure_nltk_resources() -> None:
    """Ensure the WordNet corpus required for English lemmatization is available."""
    try:
        nltk.data.find(_WORDNET_RESOURCE)
    except LookupError:
        nltk.download("wordnet", quiet=True)


class TextPreprocessor:
    """Normalize document text before TF-IDF vectorization."""

    def __init__(self) -> None:
        """Initialize a reusable English lemmatizer and stopword set."""
        ensure_nltk_resources()
        self._lemmatizer = WordNetLemmatizer()
        self._stopwords = frozenset(ENGLISH_STOP_WORDS)

    @lru_cache(maxsize=50_000)
    def _lemmatize(self, token: str) -> str:
        """Lemmatize a token once per preprocessor instance."""
        return self._lemmatizer.lemmatize(token)

    def transform(self, text: str) -> str:
        """Lowercase, clean, stopword-filter, and lemmatize one document."""
        normalized = text.lower()
        normalized = re.sub(r"[^a-z\s]", " ", normalized)
        tokens = normalized.split()
        processed_tokens = [
            self._lemmatize(token)
            for token in tokens
            if token not in self._stopwords
        ]
        return " ".join(processed_tokens)

    def transform_many(self, texts: list[str]) -> list[str]:
        """Preprocess a collection of documents."""
        return [self.transform(text) for text in texts]
