from django.http import JsonResponse
from assistant.rag.retriever import retrieve
from assistant.rag.generator import generate_answer
from django.shortcuts import render

def assistant_page(request):
    return render(request, "assistant/chat.html")
def ask(request):
    q = request.GET.get("q", "")
    if not q:
        return JsonResponse({"error": "No query"}, status=400)

    context = retrieve(q)[0]
    answer = generate_answer(q, context)

    return JsonResponse({"answer": answer})