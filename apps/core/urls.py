from django.urls import path
from . import views

urlpatterns = [
    # HR Dashboard endpoints
    path('hr/dashboard/stats/', views.HRDashboardStatsView.as_view(), name='hr_dashboard_stats'),
    path('hr/dashboard/jobs/', views.HRDashboardJobsView.as_view(), name='hr_dashboard_jobs'),
    path('hr/dashboard/applications/', views.HRDashboardApplicationsView.as_view(), name='hr_dashboard_applications'),
]
