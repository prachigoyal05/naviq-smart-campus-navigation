# assistant/urls.py
from django.urls import path
from .views import assistant_page,ask


urlpatterns = [
      path("", assistant_page, name="assistant-page"),
      path("ask/", ask, name="assistant-ask"),
     # AI assistant chat URLs will be added here
]
