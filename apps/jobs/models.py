from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    company_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=15, choices=JOB_TYPE_CHOICES)
    experience_level = models.CharField(max_length=10, choices=EXPERIENCE_CHOICES)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    skills_required = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    hr_team_members = models.ManyToManyField(User, related_name='assigned_jobs', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)