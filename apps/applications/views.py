from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.permissions import IsStudentOrReadOnly, IsHROrReadOnly
from .models import Application, ApplicationHistory
from .serializers import ApplicationSerializer, ApplicationHistorySerializer
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
class ApplicationListCreateView(generics.ListCreateAPIView):
    serializer_class = ApplicationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'job']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Application.objects.filter(applicant=user)
        elif user.role in ['recruiting_hr', 'main_hr']:
            return Application.objects.filter(job__posted_by=user)
        elif user.role == 'hr_team_member':
            return Application.objects.filter(job__hr_team_members=user)
        return Application.objects.none()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsStudentOrReadOnly()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

class ApplicationDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ApplicationSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Application.objects.filter(applicant=user)
        elif user.role in ['recruiting_hr', 'hr_team_member', 'main_hr']:
            return Application.objects.all()
        return Application.objects.none()

    def get_permissions(self):
        if self.request.method == 'PUT':
            return [permissions.IsAuthenticated(), IsHROrReadOnly()]
        return [permissions.IsAuthenticated()]

    def perform_update(self, serializer):
        # Create history record and send email notification when status changes
        instance = self.get_object()
        previous_status = instance.status
        is_status_changing = 'status' in serializer.validated_data

        if is_status_changing:
            ApplicationHistory.objects.create(
                application=instance,
                status=serializer.validated_data['status'],
                notes=serializer.validated_data.get('notes', ''),
                changed_by=self.request.user
            )

        serializer.save()

        # If status changed, email the applicant
        if is_status_changing and previous_status != serializer.instance.status:
            application = serializer.instance
            applicant_email = application.applicant.email

            if applicant_email:
                job_title = application.job.title
                new_status = application.status
                previous_status_readable = previous_status.replace('_', ' ').title()
                new_status_readable = new_status.replace('_', ' ').title()
                applicant_name = application.applicant.first_name or application.applicant.username

                subject = f"Update on your application for '{job_title}'"

                context = {
                    "applicant_name": applicant_name,
                    "job_title": job_title,
                    "previous_status": previous_status_readable,
                    "new_status": new_status_readable,
                    "company_email": getattr(settings, 'DEFAULT_FROM_EMAIL', 'HR Team'),
                }

                html_content = render_to_string("emails/application_status_update.html", context)
                text_content = f"""
        Hello {applicant_name},

        The status of your application for '{job_title}' has changed from
        '{previous_status_readable}' to '{new_status_readable}'.

        You can log in to your dashboard to view more details.

        Regards,  
        {context['company_email']}
                """

                try:
                    email = EmailMultiAlternatives(
                        subject,
                        text_content,
                        context["company_email"],
                        [applicant_email],
                    )
                    email.attach_alternative(html_content, "text/html")
                    email.send()
                except Exception:
                    # Avoid breaking the API if the email fails
                    pass

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def application_history(request, pk):
    try:
        application = Application.objects.get(pk=pk)
        history = ApplicationHistory.objects.filter(application=application).order_by('-changed_at')
        serializer = ApplicationHistorySerializer(history, many=True)
        return Response(serializer.data)
    except Application.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)