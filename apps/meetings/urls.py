from django.urls import path
from . import views

urlpatterns = [
    # Main CRUD endpoints
    path('', views.MeetingListCreateView.as_view(), name='meeting_list_create'),
    path('<int:pk>/', views.MeetingDetailView.as_view(), name='meeting_detail'),
    
    # Meeting management endpoints
    path('<int:pk>/reschedule/', views.reschedule_meeting, name='reschedule_meeting'),
    path('<int:pk>/cancel/', views.cancel_meeting, name='cancel_meeting'),
    path('<int:pk>/complete/', views.complete_meeting, name='complete_meeting'),
    
    # Attendee management endpoints
    path('<int:pk>/add-attendee/', views.add_attendee, name='add_attendee'),
    path('<int:pk>/remove-attendee/', views.remove_attendee, name='remove_attendee'),
    
    # Statistics endpoint
    path('stats/', views.MeetingStatsView.as_view(), name='meeting_stats'),
]   