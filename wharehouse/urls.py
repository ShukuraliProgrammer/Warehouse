from django.urls import path
from . import views

app_name = 'wharehouse'

urlpatterns = [
    path('order-stats/', views.OrderStatsView.as_view(), name='order-stats'),
]
