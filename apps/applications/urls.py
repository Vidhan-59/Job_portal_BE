from django.urls import path
from . import views

urlpatterns = [
    path('', views.ApplicationListCreateView.as_view(), name='application_list_create'),
    path('<int:pk>/', views.ApplicationDetailView.as_view(), name='application_detail'),
    path('<int:pk>/history/', views.application_history, name='application_history'),
]