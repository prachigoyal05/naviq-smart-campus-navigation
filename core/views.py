from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'core/home.html')

def about(request):
    return render(request, 'core/about.html')

def your_view(request):
    print(request.POST)   # for form data
    print(request.body)   # for raw data
    return HttpResponse("OK")