from django.db import models
from django.contrib.auth import get_user_model
from apps.applications.models import Application

User = get_user_model()

class Meeting(models.Model):
    MEETING_TYPE_CHOICES = [
        ('hr_screening', 'HR Screening'),
        ('technical_interview', 'Technical Interview'),
        ('final_interview', 'Final Interview'),
        ('team_discussion', 'Team Discussion'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='meetings')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPE_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    meeting_link = models.URLField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='scheduled')
    attendees = models.ManyToManyField(User, related_name='meetings')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_meetings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)