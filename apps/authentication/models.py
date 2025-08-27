from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('recruiting_hr', 'Recruiting HR'),
        ('hr_team_member', 'HR Team Member'),
        ('team_lead', 'Team Lead'),
        ('main_hr', 'Main HR'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/', blank=True)
    skills = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    portfolio_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)