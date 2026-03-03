# qrnav/urls.py
from django.urls import path
from .views import qr_scan_page

app_name = 'qrnav'

urlpatterns = [
    # QR navigation URLs will come here later
    path("", qr_scan_page, name="qr_scan"),
]
