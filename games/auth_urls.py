from django.urls import path
from .views import RegistroAPIView, LogoutAPIView

urlpatterns = [
    path("registro/", RegistroAPIView.as_view(), name="registro"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
]
