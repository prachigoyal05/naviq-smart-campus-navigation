import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

STORE_PATH = Path("assistant/rag/store.pkl")

with open(STORE_PATH, "rb") as f:
    chunks, vectorizer, tfidf_matrix = pickle.load(f)

def retrieve(query, top_k=1):
    q_vec = vectorizer.transform([query])
    sims = cosine_similarity(q_vec, tfidf_matrix)[0]
    best = np.argsort(sims)[::-1][:top_k]
    return [chunks[i] for i in best]
