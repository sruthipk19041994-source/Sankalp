from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .forms import ProfileRegistrationForm
from education.models import EducationRequest
from medical.models import MedicalCampRequest
from legal.models import LegalAwarenessCamp, LegalQuestion
from women_support.models import WomenSupportCampaign, WomenSupportArticle, WomenSupportQuestion
from accounts.models import Profile, Notification
import threading
from datetime import timedelta
from django.utils.timezone import now
from twilio.rest import Client


# 🌿 Threaded Email Sender
class EmailThread(threading.Thread):
    def __init__(self, subject, plain_message, from_email, recipient_list, html_message):
        self.subject = subject
        self.plain_message = plain_message
        self.from_email = from_email
        self.recipient_list = recipient_list
        self.html_message = html_message
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            subject=self.subject,
            message=self.plain_message,
            from_email=self.from_email,
            recipient_list=self.recipient_list,
            html_message=self.html_message,
        )


# 🌿 Auth & Static Views
class HomeView(View):
    def get(self, request):
        return render(request, 'accounts/home.html')


class AboutView(View):
    def get(self, request):
        return render(request, 'accounts/about.html')


class ContactView(View):
    def get(self, request):
        volunteers = Profile.objects.filter(role='Volunteer')
        return render(request, 'accounts/contact.html', {'volunteers': volunteers})


class RegisterView(View):
    def get(self, request):
        form = ProfileRegistrationForm()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        form = ProfileRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password1')  # ✅ Correct field name
            user.set_password(password)
            user.save()
            messages.success(request, "✅ Registration successful! Please login.")
            return redirect('login')
        else:
            print("❌ Form errors:", form.errors)
            messages.error(request, "Registration failed! Check your inputs.")
        return render(request, 'accounts/register.html', {'form': form})


class LoginView(View):
    def get(self, request):
        return render(request, 'accounts/login.html')

    def post(self, request):
        action = request.POST.get('action')

        # 🔹 Normal Login
        if action == 'login':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)

            if user and user.is_active:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('dashboard')
            messages.error(request, "Invalid username or password.")
            return render(request, 'accounts/login.html')

        # 🔹 Forgot Password
        elif action == 'forgot':
            email = request.POST.get('email')
            user = Profile.objects.filter(email=email).first()

            if not user:
                messages.error(request, "⚠️ Email not registered.")
                return render(request, 'accounts/login.html')

            token = get_random_string(40)
            user.reset_token = token
            user.save()

            reset_link = request.build_absolute_uri(reverse('reset_password', args=[token]))

            try:
                html_message = render_to_string('accounts/forgot_password_email.html', {
                    'user': user,
                    'reset_link': reset_link,
                })
                plain_message = strip_tags(html_message)

                EmailThread(
                    subject='Sankalp Password Reset',
                    plain_message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=html_message,
                ).start()

                messages.success(request, "📧 Password reset link sent to your email.")
                return render(request, 'accounts/login.html')

            except Exception as e:
                messages.error(request, f"❌ Failed to send email: {str(e)}")
                return render(request, 'accounts/login.html')


# 🔐 Reset Password
class ResetPasswordView(View):
    def get(self, request, token):
        user = Profile.objects.filter(reset_token=token).first()
        if not user:
            messages.error(request, "❌ Invalid or expired password reset link.")
            return redirect('login')
        return render(request, 'accounts/reset_password.html', {'token': token})

    def post(self, request, token):
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')
        user = Profile.objects.filter(reset_token=token).first()

        if not user:
            messages.error(request, "❌ Invalid or expired reset link.")
            return redirect('login')

        if not password or not confirm:
            messages.error(request, "⚠️ Both fields are required.")
            return render(request, 'accounts/reset_password.html', {'token': token})

        if password != confirm:
            messages.error(request, "❌ Passwords do not match. Please try again.")
            return render(request, 'accounts/reset_password.html', {'token': token})

        user.set_password(password)
        user.reset_token = None
        user.save()

        # Email confirmation
        try:
            html_message = render_to_string('accounts/password_changed_email.html', {'user': user})
            plain_message = strip_tags(html_message)
            EmailThread(
                subject='Sankalp Password Changed',
                plain_message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
            ).start()
        except Exception:
            pass

        messages.success(request, "✅ Password updated successfully! Please log in.")
        return redirect('login')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')


# 🌿 Unified Dashboard
class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        role = getattr(user, 'role', None)

        # ✅ Admin Dashboard
        if role == 'Admin':
            context = {
                'total_requests': EducationRequest.objects.count(),
                'pending_requests': EducationRequest.objects.filter(status='Pending').count(),
                'forwarded_requests': EducationRequest.objects.filter(status='Forwarded').count(),
                'approved_requests': EducationRequest.objects.filter(status='Approved').count(),
                'rejected_requests': EducationRequest.objects.filter(status='Rejected').count(),
                'total_volunteers': Profile.objects.filter(role='Volunteer').count(),
                'total_donors': Profile.objects.filter(role='Donor').count(),
                'total_beneficiaries': Profile.objects.filter(role='Beneficiary').count(),
            }
            return render(request, 'accounts/admin_dashboard.html', context)

        # ✅ Volunteer Dashboard
        elif role == 'Volunteer':
            volunteer = request.user
            notifications = Notification.objects.filter(recipient=volunteer).order_by('-created_at')
            return render(request, 'accounts/volunteer_dashboard.html', {
                'pending_requests': EducationRequest.objects.filter(status='Pending'),
                'forwarded_requests': EducationRequest.objects.filter(forwarded_to__role='Donor', status='Forwarded'),
                'approved_requests': EducationRequest.objects.filter(status='Approved'),
                'notifications': notifications,
                'unread_count': notifications.filter(is_read=False).count(),
            })

        # ✅ Donor Dashboard
        elif role == 'Donor':
            donor = request.user
            notifications = Notification.objects.filter(recipient=donor).order_by('-created_at')
            return render(request, 'accounts/donor_dashboard.html', {
                'forwarded_requests': EducationRequest.objects.filter(forwarded_to=donor, status='Forwarded'),
                'approved_requests': EducationRequest.objects.filter(forwarded_to=donor, status='Approved'),
                'rejected_requests': EducationRequest.objects.filter(forwarded_to=donor, status='Rejected'),
                'notifications': notifications,
                'unread_count': notifications.filter(is_read=False).count(),
            })

        # ✅ Beneficiary Dashboard
        elif role == 'Beneficiary':
            return render(request, 'accounts/beneficiary_dashboard.html', {
                'education_requests': EducationRequest.objects.filter(beneficiary=request.user).order_by('-created_at'),
                'medical_camps': MedicalCampRequest.objects.filter(approval_status__in=['Approved', 'Scheduled']).order_by('-scheduled_date', '-created_at'),
                'women_camps': WomenSupportCampaign.objects.filter(status__in=['Approved', 'Scheduled']).order_by('-scheduled_date', '-created_at'),
            })

        # ✅ Advocate Dashboard
        elif role == 'Advocate':
            camps_by_status = {
                'Pending': LegalAwarenessCamp.objects.filter(status='Pending'),
                'Approved': LegalAwarenessCamp.objects.filter(status='Approved'),
                'Rejected': LegalAwarenessCamp.objects.filter(status='Rejected'),
            }
            questions = LegalQuestion.objects.all().order_by('-created_at')
            return render(request, 'accounts/advocate_dashboard.html', {
                'camps_by_status': camps_by_status,
                'questions': questions,
            })

        # ✅ Supporter Dashboard
        elif role == 'Supporter':
            context = {
                'pending_campaigns': WomenSupportCampaign.objects.filter(status='Pending'),
                'approved_campaigns': WomenSupportCampaign.objects.filter(status='Approved'),
                'rejected_campaigns': WomenSupportCampaign.objects.filter(status='Rejected'),
                'scheduled_campaigns': WomenSupportCampaign.objects.filter(status='Scheduled'),
                'articles': WomenSupportArticle.objects.filter(author=request.user),
                'questions': WomenSupportQuestion.objects.all().order_by('-created_at'),
            }
            return render(request, 'accounts/supporter_dashboard.html', context)
    # 🔹 Fallback for undefined or missing role
        messages.error(request, "⚠️ Dashboard not available for your role. Contact admin.")
        return redirect('home')  # or any safe page


# 🌈 Admin — Manage Users
class AdminUserManagementView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'Admin':
            messages.error(request, "Access denied.")
            return redirect('dashboard')
        users = Profile.objects.all().order_by('role', 'username')
        return render(request, 'accounts/admin_users.html', {'users': users})


# 🧑‍💼 Admin — Edit User
class AdminUserEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        user = get_object_or_404(Profile, pk=pk)
        return render(request, 'accounts/admin_user_edit.html', {'user': user})

    def post(self, request, pk):
        user = get_object_or_404(Profile, pk=pk)
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.role = request.POST.get('role')
        user.save()
        messages.success(request, "User details updated successfully.")
        return redirect('admin_user_management')


# ❌ Admin — Delete User
class AdminUserDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(Profile, pk=pk)
        name = user.username
        user.delete()
        messages.warning(request, f"User '{name}' has been deleted.")
        return redirect('admin_user_management')


# 🌈 Admin — Manage & Schedule Campaigns
class AdminCampaignManagementView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'Admin':
            messages.error(request, "Access denied.")
            return redirect('dashboard')

        context = {
            'education_campaigns': EducationRequest.objects.all(),
            'medical_campaigns': MedicalCampRequest.objects.all(),
            'legal_campaigns': LegalAwarenessCamp.objects.all(),
             'women_support_campaigns': WomenSupportCampaign.objects.all(),        }
        return render(request, 'accounts/admin_campaigns.html', context)
