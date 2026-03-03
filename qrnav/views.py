from django.shortcuts import render

def qr_scan_page(request):
    return render(request, "qrnav/scan.html")

# Create your views here.
