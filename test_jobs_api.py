#!/usr/bin/env python
"""
Simple test script to verify the jobs API is working correctly
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.jobs.models import Job

User = get_user_model()

def test_jobs_api():
    """Test the jobs API logic"""
    print("=== Testing Jobs API Logic ===\n")
    
    # Check if users exist
    try:
        hr_user = User.objects.get(username='hr_user')
        print(f"✓ HR User found: {hr_user.username} (Role: {hr_user.role})")
    except User.DoesNotExist:
        print("✗ HR User not found. Run 'python manage.py create_sample_data' first.")
        return
    
    try:
        student_user = User.objects.get(username='student_user')
        print(f"✓ Student User found: {student_user.username} (Role: {student_user.role})")
    except User.DoesNotExist:
        print("✗ Student User not found. Run 'python manage.py create_sample_data' first.")
        return
    
    # Check if jobs exist
    jobs = Job.objects.all()
    print(f"\n✓ Total jobs in database: {jobs.count()}")
    
    for job in jobs:
        print(f"  - Job: {job.title}")
        print(f"    Status: {job.status}")
        print(f"    Posted by: {job.posted_by.username} (Role: {job.posted_by.role})")
        print()
    
    # Test the queryset logic for different user roles
    print("=== Testing Role-Based Access Control ===\n")
    
    # Test HR user access
    hr_jobs = Job.objects.filter(posted_by=hr_user)
    print(f"Jobs posted by HR user '{hr_user.username}': {hr_jobs.count()}")
    
    # Test student access to active jobs
    active_jobs = Job.objects.filter(status='active')
    print(f"Active jobs available to students: {active_jobs.count()}")
    
    # Test the specific logic from the view
    print("\n=== View Logic Test ===")
    
    # Simulate HR user request
    if hr_user.role in ['recruiting_hr', 'hr_team_member', 'main_hr']:
        hr_visible_jobs = Job.objects.filter(posted_by=hr_user)
        print(f"HR user '{hr_user.username}' can see: {hr_visible_jobs.count()} jobs")
    else:
        print(f"HR user '{hr_user.username}' has role '{hr_user.role}' - not in allowed list")
    
    # Simulate student user request
    if student_user.role == 'student':
        student_visible_jobs = Job.objects.filter(status='active')
        print(f"Student user '{student_user.username}' can see: {student_visible_jobs.count()} active jobs")
    else:
        print(f"Student user '{student_user.username}' has role '{student_user.role}' - not 'student'")
    
    print("\n=== Summary ===")
    if hr_visible_jobs.count() > 0:
        print("✓ HR user can see jobs - API should work for HR users")
    else:
        print("✗ HR user cannot see any jobs - check job ownership")
    
    if student_visible_jobs.count() > 0:
        print("✓ Students can see active jobs - API should work for students")
    else:
        print("✗ No active jobs available for students - check job status")

if __name__ == '__main__':
    test_jobs_api()
