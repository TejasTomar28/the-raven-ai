# RAVEN AI Offline Document Classification

This standalone package trains a traditional machine-learning classifier for labelled PDF documents. It does not depend on FastAPI, Ollama, LangChain, OpenAI, embeddings, or transformer models.

## Dataset

Place labelled PDFs in the existing class-directory structure:

```text
ml/dataset/train/
├── research/
├── technical/
├── resume/
├── finance/
├── legal/
└── hr/
```

Each directory name is used as the target label. The `dataset/test/` directory is an untouched final holdout. If it is empty when training starts, the training command creates a deterministic, duplicate-safe stratified split from `dataset/train/` using the fixed random seed.

## Pipeline

1. **PDF extraction** — PyMuPDF extracts text from non-empty pages.
2. **Preprocessing** — text is lowercased; punctuation, numbers, and extra whitespace are removed; English stopwords are filtered; remaining tokens are lemmatized with WordNet.
3. **Features** — `TfidfVectorizer` creates unigram and bigram document features.
4. **Models** — Logistic Regression, Linear SVM, and XGBoost train on the same split.
5. **Selection** — the model with the highest weighted F1 score is persisted.

Before splitting, the pipeline audits SHA-256 hashes of normalized text. Exact copies are kept in the same partition with a deterministic group-aware split, preventing duplicate-text leakage into validation.

## Training

Install the ML-only dependencies from the repository root:

```bash
.venv/bin/pip install -r ml/requirements.txt
.venv/bin/python -m ml.train
```

Training prints accuracy, weighted precision, weighted recall, weighted F1, and a confusion matrix for all three models. It also downloads NLTK's small WordNet corpus automatically when it is not already available.

## Evaluation

```bash
.venv/bin/python -m ml.evaluate
```

This loads the saved final model and reports the final holdout metrics, confusion matrix, and full per-class classification report from `dataset/test/`.

## Prediction

```bash
.venv/bin/python -m ml.predict path/to/document.pdf
```

The script extracts and preprocesses the PDF, transforms it with the persisted TF-IDF vectorizer, predicts the category, and prints its confidence. Linear SVM confidence is derived by normalizing decision scores because it does not expose probabilities directly.

## Saved models

Training saves these joblib artifacts in `ml/models/`:

- `best_model.pkl`
- `tfidf_vectorizer.pkl`
- `label_encoder.pkl`

Run training again whenever labels or PDFs change. The new run retrains all three classifiers and replaces the persisted artifacts with the new weighted-F1 winner.

## Folder structure

```text
ml/
├── dataset/
├── models/
├── scripts/
│   ├── config.py
│   ├── dataset.py
│   ├── metrics.py
│   ├── pdf_extraction.py
│   └── preprocessing.py
├── train.py
├── evaluate.py
├── predict.py
├── requirements.txt
└── README.md
```
