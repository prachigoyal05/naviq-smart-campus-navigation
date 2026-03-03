import requests

def generate_answer(query, context):
    prompt = f"""
Answer using ONLY the context.

Context:
{context}

Question:
{query}

Answer in one sentence:
"""

    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi3",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1,
                        "num_predict": 60}
        },
        timeout=60
    )

    return r.json()["response"].strip()
