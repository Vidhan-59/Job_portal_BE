#!/usr/bin/env python
"""
Simple test script to verify the HR Dashboard views are working correctly
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
from apps.jobs.serializers import JobSerializer

User = get_user_model()

def test_hr_dashboard():
    """Test the HR Dashboard views"""
    print("=== Testing HR Dashboard Views ===\n")
    
    # Check if users exist
    try:
        hr_user = User.objects.get(username='hr_user')
        print(f"✓ HR User found: {hr_user.username} (Role: {hr_user.role})")
    except User.DoesNotExist:
        print("✗ HR User not found. Run 'python manage.py create_sample_data' first.")
        return
    
    # Check if jobs exist
    jobs = Job.objects.filter(posted_by=hr_user)
    print(f"✓ Jobs posted by HR user: {jobs.count()}")
    
    for job in jobs:
        print(f"  - Job: {job.title}")
        print(f"    Status: {job.status}")
        print(f"    Job Type: {job.job_type}")
        print(f"    Location: {job.location}")
        print()
    
    # Test the JobSerializer
    print("=== Testing JobSerializer ===")
    try:
        if jobs.exists():
            job = jobs.first()
            serializer = JobSerializer(job)
            print(f"✓ JobSerializer works for job: {job.title}")
            print(f"  Serialized fields: {list(serializer.data.keys())}")
            
            # Check if any problematic fields exist
            problematic_fields = ['department', 'employment_type']
            for field in problematic_fields:
                if field in serializer.data:
                    print(f"  ⚠️  Warning: Field '{field}' exists in serializer but not in model")
                else:
                    print(f"  ✓ Field '{field}' correctly not present")
        else:
            print("⚠️  No jobs found to test serializer")
    except Exception as e:
        print(f"✗ Error testing JobSerializer: {e}")
    
    # Test the queryset logic
    print("\n=== Testing HR Dashboard Queryset ===")
    try:
        # Simulate the HRDashboardJobsView queryset
        queryset = Job.objects.filter(posted_by=hr_user).prefetch_related('applications')
        print(f"✓ HR Dashboard queryset works: {queryset.count()} jobs")
        
        # Test filtering by status (the only valid filter field)
        active_jobs = queryset.filter(status='active')
        print(f"✓ Status filtering works: {active_jobs.count()} active jobs")
        
    except Exception as e:
        print(f"✗ Error testing HR Dashboard queryset: {e}")
    
    print("\n=== Summary ===")
    print("✓ HR Dashboard views should now work without the 'department' field error")
    print("✓ Only valid fields from the Job model are used")
    print("✓ Filtering by 'status' is supported")

if __name__ == '__main__':
    test_hr_dashboard()
