import threading
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse

from .models import MedicalCampRequest, Hospital
from .forms import MedicalCampForm


# 🔹 Helper for background email sending
def send_async_email(email):
    """Send email in a background thread to avoid blocking the response."""
    try:
        email.send(fail_silently=True)
    except Exception as e:
        print("Email sending error:", e)


# 🔹 Volunteer creates a camp request
class MedicalCampRequestView(LoginRequiredMixin, View):
    def get(self, request):
        form = MedicalCampForm()
        return render(request, 'medical/create_camp.html', {'form': form})

    def post(self, request):
        form = MedicalCampForm(request.POST)
        if form.is_valid():
            camp_request = form.save(commit=False)
            camp_request.volunteer = request.user
            camp_request.save()

            # ✅ Send approval email to hospital
            hospital = camp_request.hospital
            subject = f"Medical Camp Request from {request.user.username}"

            approve_url = request.build_absolute_uri(
                reverse('hospital_approve_request', args=[camp_request.approval_token]) + "?status=approved"
            )
            reject_url = request.build_absolute_uri(
                reverse('hospital_approve_request', args=[camp_request.approval_token]) + "?status=rejected"
            )

            html_content = render_to_string('medical/email_approve.html', {
                'hospital': hospital,
                'camp': camp_request,
                'approve_url': approve_url,
                'reject_url': reject_url,
            })
            text_content = strip_tags(html_content)

            if hospital.email:
                email = EmailMessage(subject, html_content, settings.DEFAULT_FROM_EMAIL, [hospital.email])
                email.content_subtype = "html"
                threading.Thread(target=send_async_email, args=(email,)).start()

            messages.success(request, "✅ Your medical camp request has been sent to the hospital.")
            return redirect('volunteer_medical_list')

        messages.error(request, "❌ Please correct the form errors below.")
        return render(request, 'medical/create_camp.html', {'form': form})


# 🔹 Hospital approves or rejects via email link
class HospitalApproveRequestView(View):
    def get(self, request, token):
        camp_request = get_object_or_404(MedicalCampRequest, approval_token=token)
        status = request.GET.get('status')

        if camp_request.approval_status in ['Scheduled', 'Rejected']:
            return render(request, 'medical/email_response.html', {
                'message': "⚠ This request has already been responded to."
            })

        if status == 'approved':
            camp_request.approval_status = 'Scheduled'
            # Use the date/time set by volunteer
            camp_request.scheduled_date = camp_request.date
            camp_request.scheduled_time = camp_request.time
            message = "✅ The medical camp has been approved and scheduled."
        elif status == 'rejected':
            camp_request.approval_status = 'Rejected'
            message = "❌ The medical camp request has been rejected."
        else:
            return render(request, 'medical/email_response.html', {
                'message': "⚠ Invalid approval action."
            })

        camp_request.save()

        # Notify volunteer
        subject = f"Update from {camp_request.hospital.name} – Medical Camp Request"
        html_content = render_to_string('medical/email_status_update.html', {
            'camp': camp_request,
            'message': message,
        })
        volunteer_email = camp_request.volunteer.email
        if volunteer_email:
            email = EmailMessage(subject, html_content, settings.DEFAULT_FROM_EMAIL, [volunteer_email])
            email.content_subtype = "html"
            threading.Thread(target=lambda e: e.send(fail_silently=True), args=(email,)).start()

        return render(request, 'medical/email_response.html', {'message': message})


# 🔹 Volunteer/Admin – View all camp requests
class VolunteerMedicalCampListView(LoginRequiredMixin, View):
    def get(self, request):
        # If admin → show all camps
        if request.user.role == 'Admin':
            camps = MedicalCampRequest.objects.all().order_by('-created_at')
        else:
            # Volunteer → show only their own requests
            camps = MedicalCampRequest.objects.filter(volunteer=request.user).order_by('-created_at')
        
        return render(request, 'medical/volunteer_camp_list.html', {'camps': camps})


# 🔹 Admin/Volunteer schedules or reschedules a camp

# 🔹 Beneficiary view: approved/scheduled medical camps
class MedicalCampInfoView(LoginRequiredMixin, View):
    """Displays approved and scheduled medical camps for beneficiaries."""
    def get(self, request):
        if request.user.role != 'Beneficiary':
            messages.error(request, "Access restricted to beneficiaries only.")
            return redirect('medical_camp_request')

        camps = MedicalCampRequest.objects.filter(
            approval_status__in=['Approved', 'Scheduled']
        ).order_by('-created_at')
        return render(request, 'medical/info.html', {'camps': camps})


# 🔹 Detailed view for a single medical camp
class MedicalCampDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        camp = get_object_or_404(MedicalCampRequest, pk=pk)
        return render(request, 'medical/camp_detail.html', {'camp': camp})

