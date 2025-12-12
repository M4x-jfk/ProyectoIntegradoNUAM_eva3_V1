from rest_framework import routers
from django.urls import path

from .views_api import CalificacionViewSet, RegisterInvestorView, RegisterShareholderView

router = routers.DefaultRouter()
router.register(r"calificaciones", CalificacionViewSet)

urlpatterns = [
    path('auth/register-investor/', RegisterInvestorView.as_view(), name='api_register_investor'),
    path('auth/register-shareholder/', RegisterShareholderView.as_view(), name='api_register_shareholder'),
] + router.urls

