from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.jobs.models import Job
from apps.applications.models import Application

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates sample data for testing purposes'
    def handle(self, *args, **options):
        # Create users
        hr_user = User.objects.create_user(
            username='hr_user',
            email='hr@company.com',
            first_name='John',
            last_name='HR',
            role='recruiting_hr',
            password='password123'
        )
        
        student_user = User.objects.create_user(
            username='student_user',
            email='student@email.com',
            first_name='Jane',
            last_name='Student',
            role='student',
            password='password123'
        )
        
        # Create job
        job = Job.objects.create(
            title='Software Engineer',
            description='We are looking for a skilled software engineer...',
            requirements='Python, Django, REST APIs',
            company_name='Tech Company',
            location='Remote',
            job_type='full_time',
            experience_level='mid',
            salary_min=70000,
            salary_max=100000,
            skills_required='Python, Django, PostgreSQL',
            status='active',
            posted_by=hr_user
        )
        
        # Create application
        Application.objects.create(
            job=job,
            applicant=student_user,
            cover_letter='I am very interested in this position...',
            status='pending'
        )
        
        self.stdout.write(
            self.style.SUCCESS('Sample data created successfully!')
        )