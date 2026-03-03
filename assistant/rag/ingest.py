from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
from pathlib import Path

DATA_PATH = Path("assistant/rag_data/data.txt")
OUT_PATH = Path("assistant/rag/store.pkl")

def ingest():
    print("INGEST STARTED")

    text = DATA_PATH.read_text(encoding="utf-8")
    chunks = [line.strip() for line in text.split("\n") if len(line.strip()) > 10]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(chunks)

    with open(OUT_PATH, "wb") as f:
        pickle.dump((chunks, vectorizer, tfidf_matrix), f)

    print("Chunks:", len(chunks))
    print("INGEST COMPLETE")

if __name__ == "__main__":
    ingest()
