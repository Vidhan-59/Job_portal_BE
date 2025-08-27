from django.urls import path
from . import views

urlpatterns = [
    path('', views.JobListCreateView.as_view(), name='job_list_create'),
    path('<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path('<int:pk>/close/', views.close_job, name='close_job'),
    path('hr-team-members/', views.hr_team_members, name='hr_team_members'),
]