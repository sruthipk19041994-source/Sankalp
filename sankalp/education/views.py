import threading
from django.shortcuts import render, redirect, get_object_or_404 
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .forms import EducationRequestForm
from .models import EducationRequest
from accounts.models import Profile
from accounts.utility import send_phone_sms, create_notification  # ✅ Twilio + notification

# 🌸 Utility: Send notification/SMS asynchronously
def run_in_thread(func, *args, **kwargs):
    threading.Thread(target=func, args=args, kwargs=kwargs).start()


# 🎓 Beneficiary – Submit Education Request
class EducationRequestView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'Beneficiary':
            messages.error(request, "Access denied: Only beneficiaries can submit education support requests.")
            return redirect('dashboard')

        form = EducationRequestForm()
        return render(request, 'education/request_support.html', {'form': form})

    def post(self, request):
        if request.user.role != 'Beneficiary':
            messages.error(request, "Access denied.")
            return redirect('dashboard')

        form = EducationRequestForm(request.POST, request.FILES)
        if form.is_valid():
            edu_req = form.save(commit=False)
            edu_req.beneficiary = request.user
            edu_req.status = 'Pending'
            edu_req.created_at = timezone.now()
            edu_req.save()

            # ✅ Notify all volunteers asynchronously
            volunteers = Profile.objects.filter(role='Volunteer')
            for v in volunteers:
                run_in_thread(create_notification, v,
                    f"🎓 New education support request submitted by {request.user.get_full_name() or request.user.username}."
                )

            messages.success(request, "🎓 Education support request submitted successfully!")
            return redirect('education_info')

        return render(request, 'education/request_support.html', {'form': form})


# 🎓 Beneficiary – View Latest Request Info
class EducationInfoView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'Beneficiary':
            messages.error(request, "Access denied.")
            return redirect('dashboard')

        edu_req = EducationRequest.objects.filter(beneficiary=request.user).last()
        return render(request, 'education/education_info.html', {'education_request': edu_req})


# 🧑‍🤝‍🧑 Volunteer – View Pending & Forwarded Requests
class VolunteerEducationRequestsView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'Volunteer':
            messages.error(request, "Access denied.")
            return redirect('dashboard')

        all_requests = EducationRequest.objects.exclude(status__in=['Approved', 'Rejected']).order_by('-created_at')
        donors = Profile.objects.filter(role='Donor')
        forwarded_requests = EducationRequest.objects.filter(status='Forwarded').order_by('-forwarded_at')

        return render(request, 'education/volunteer_requests.html', {
            'requests': all_requests,
            'donors': donors,
            'forwarded_requests': forwarded_requests,
        })


# 📨 Volunteer – Forward Request to Donor
class VolunteerForwardRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if request.user.role != 'Volunteer':
            messages.error(request, "Access denied.")
            return redirect('dashboard')

        donor_id = request.POST.get('donor_id')
        donor_profile = get_object_or_404(Profile, id=donor_id)
        edu_req = get_object_or_404(EducationRequest, pk=pk)

        if edu_req.status != 'Pending':
            messages.warning(request, "This request has already been processed.")
            return redirect('volunteer_education_requests')

        # ✅ Update forwarding details
        edu_req.volunteer = request.user
        edu_req.forwarded_to = donor_profile
        edu_req.forwarded_at = timezone.now()
        edu_req.status = 'Forwarded'
        edu_req.save()

        # ✅ Notify admin asynchronously
        admins = Profile.objects.filter(role='Admin')
        for admin in admins:
            run_in_thread(create_notification, admin,
                f"📨 Volunteer {request.user.username} forwarded an education request to donor {donor_profile.username}."
            )

        # ✅ SMS: Only Donor gets a message asynchronously
        run_in_thread(send_phone_sms,
            '9061525199',  # dummy number
            f"🎓 A new education support request has been forwarded to you by Volunteer {request.user.username}. "
            "Please check your Sankalp dashboard to view details."
        )

        messages.success(request, f"🎓 Request forwarded to Donor {donor_profile.username}.")
        return redirect('volunteer_education_requests')


# ✅ Donor – Approve Request
class ApproveStudentRequestView(LoginRequiredMixin, View):
    def post(self, request, request_id):
        if request.user.role != 'Donor':
            messages.error(request, "Access denied.")
            return redirect('dashboard')

        donor_profile = request.user
        edu_req = get_object_or_404(EducationRequest, id=request_id, forwarded_to=donor_profile)
        edu_req.status = 'Approved'
        edu_req.decision_at = timezone.now()
        edu_req.save()

        # ✅ Notify admin and volunteer asynchronously
        admins = Profile.objects.filter(role='Admin')
        for admin in admins:
            run_in_thread(create_notification, admin,
                f"✅ Donor {donor_profile.username} approved a student request."
            )
        if edu_req.volunteer:
            run_in_thread(create_notification, edu_req.volunteer,
                f"✅ Donor {donor_profile.username} approved the request you forwarded."
            )

        # ✅ SMS to Student asynchronously
        run_in_thread(send_phone_sms,
            '9061525199',
            f"✅ Congratulations {edu_req.beneficiary.get_full_name() or edu_req.beneficiary.username}! "
            f"Your education support request has been approved by Donor {donor_profile.username}."
        )

        messages.success(request, f"✅ Sponsorship for '{edu_req.full_name}' approved.")
        return redirect('donor_dashboard')


# ❌ Donor – Reject Request
class RejectStudentRequestView(LoginRequiredMixin, View):
    def post(self, request, request_id):
        if request.user.role != 'Donor':
            messages.error(request, "Access denied.")
            return redirect('dashboard')

        donor_profile = request.user
        edu_req = get_object_or_404(EducationRequest, id=request_id, forwarded_to=donor_profile)
        edu_req.status = 'Rejected'
        edu_req.decision_at = timezone.now()
        edu_req.save()

        # ✅ Notify admin and volunteer asynchronously
        admins = Profile.objects.filter(role='Admin')
        for admin in admins:
            run_in_thread(create_notification, admin,
                f"❌ Donor {donor_profile.username} rejected a student request."
            )
        if edu_req.volunteer:
            run_in_thread(create_notification, edu_req.volunteer,
                f"❌ Donor {donor_profile.username} rejected the request you forwarded."
            )

        # ✅ SMS to Student asynchronously
        run_in_thread(send_phone_sms,
            '9061525199',
            f"❌ Dear {edu_req.beneficiary.get_full_name() or edu_req.beneficiary.username}, "
            f"your education support request was not approved by Donor {donor_profile.username}. "
            "Don’t lose hope — your request will remain active for other sponsors."
        )

        messages.warning(request, f"❌ Sponsorship for '{edu_req.full_name}' rejected.")
        return redirect('donor_dashboard')


# 📄 Beneficiary – View Details
class EducationDetailView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'Beneficiary':
            messages.error(request, "Access denied.")
            return redirect('dashboard')

        edu_req = EducationRequest.objects.filter(beneficiary=request.user).last()
        if not edu_req:
            messages.warning(request, "No education requests found. Please submit one first.")
            return redirect('education_request')

        return render(request, 'education/education_details.html', {'education_request': edu_req})


# 🧩 Admin – View All Education Requests
class AdminEducationRequestsView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'Admin':
            messages.error(request, "Access denied.")
            return redirect('dashboard')

        requests = EducationRequest.objects.all().order_by('-created_at')
        return render(request, 'education/admin_education_requests.html', {'requests': requests})
