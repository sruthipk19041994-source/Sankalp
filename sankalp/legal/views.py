from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import FormView
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from .forms import LegalAwarenessCampForm, LegalArticleForm, LegalQuestionForm
from .models import LegalAwarenessCamp, LegalQuestion, LegalArticle
from education.models import Profile
import threading
from django.utils import timezone


# 🧵 Utility: Send Email in Background
def send_email_async(subject, html_message, recipient_list):
    def _send():
        msg = EmailMultiAlternatives(subject, "", settings.DEFAULT_FROM_EMAIL, recipient_list)
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=True)
    threading.Thread(target=_send).start()


# 🌿 Volunteer: Request Legal Awareness Camp
class LegalCampRequestView(LoginRequiredMixin, FormView):
    template_name = 'legal/request_legal_camp.html'
    form_class = LegalAwarenessCampForm
    success_url = '/legal/info/'

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'Volunteer':
            messages.error(request, "Access denied: Only volunteers can request legal camps.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        camp = form.save(commit=False)
        camp.requested_by = self.request.user
        camp.save()

        advocates = Profile.objects.filter(role='Advocate').exclude(email__isnull=True)
        for advocate in advocates:
            approval_link = self.request.build_absolute_uri(reverse('approve_legal_camp', args=[camp.id]))
            subject = f"🧾 New Legal Camp Request: {camp.title}"
            html_message = render_to_string('legal/legal_camp_request_email.html', {
                'advocate': advocate,
                'camp': camp,
                'approval_link': approval_link,
            })
            send_email_async(subject, html_message, [advocate.email])

        messages.success(self.request, "✅ Legal awareness camp request submitted successfully.")
        return super().form_valid(form)

# 💡 Legal Info Section (Updated)
class LegalInfoView(LoginRequiredMixin, View):
    def get(self, request):
        role = request.user.role
        advocates = Profile.objects.filter(role='Advocate')

        # Default context values
        articles = None
        questions = None

        if role == 'Volunteer':
            camps = LegalAwarenessCamp.objects.filter(requested_by=request.user)
            title = "📋 My Legal Awareness Camp Requests"

        elif role == 'Beneficiary':
            camps = LegalAwarenessCamp.objects.filter(status='Approved')
            title = "⚖️ Approved Legal Awareness Camps"
            # 👇 Add these for beneficiaries
            articles = LegalArticle.objects.all().order_by('-created_at')
            questions = LegalQuestion.objects.filter(asked_by=request.user).order_by('-created_at')

        elif role == 'Advocate':
            camps = LegalAwarenessCamp.objects.all().order_by('-proposed_date')
            title = "🧾 All Legal Awareness Camps"

        else:
            messages.error(request, "Access denied.")
            return redirect('home')

        return render(request, 'legal/info.html', {
            'role': role,
            'title': title,
            'camps': camps,
            'advocates': advocates,
            'articles': articles,
            'questions': questions,
        })



# 👩‍⚖️ Advocate List
class AdvocateListView(LoginRequiredMixin, View):
    def get(self, request):
        advocates = Profile.objects.filter(role='Advocate')
        return render(request, 'legal/advocate_list.html', {'advocates': advocates})


# 👩‍⚖️ Advocate Dashboard (Updated)
class AdvocateDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'Advocate':
            messages.error(request, "Access denied: Only advocates can view this page.")
            return redirect('home')

        pending_camps = LegalAwarenessCamp.objects.filter(status='Pending').select_related('requested_by')
        approved_camps = LegalAwarenessCamp.objects.filter(status='Approved').select_related('requested_by')
        rejected_camps = LegalAwarenessCamp.objects.filter(status='Rejected').select_related('requested_by')

        # Added
        articles = LegalArticle.objects.filter(author=request.user).order_by('-created_at')
        questions = LegalQuestion.objects.filter(answer__isnull=True).order_by('-created_at')

        article_form = LegalArticleForm()

        return render(request, 'accounts/advocate_dashboard.html', {
            'pending_camps': pending_camps,
            'approved_camps': approved_camps,
            'rejected_camps': rejected_camps,
            'articles': articles,
            'questions': questions,
            'article_form': article_form,
        })

    def post(self, request):
        if request.user.role != 'Advocate':
            messages.error(request, "Access denied.")
            return redirect('home')

        form = LegalArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, "✅ Article added successfully.")
        else:
            messages.error(request, "Error adding article. Please check the form.")

        return redirect('advocate_dashboard')


# 🔄 Approve / Reject Legal Camp
class UpdateCampStatusView(LoginRequiredMixin, View):
    def post(self, request, camp_id):
        if request.user.role != 'Advocate':
            messages.error(request, "Access denied.")
            return redirect('home')

        camp = get_object_or_404(LegalAwarenessCamp, id=camp_id)
        status = request.POST.get('status')

        if camp.status != 'Pending':
            messages.warning(request, f"⚠️ This camp has already been {camp.status.lower()}.")
            return redirect('advocate_dashboard')

        if status in ['Approved', 'Rejected']:
            camp.status = status
            camp.save()

            subject = f"⚖️ Legal Camp {status}: {camp.title}"
            html_message = render_to_string('legal/legal_camp_status_update_mail.html', {
                'camp': camp,
                'status': status,
                'advocate': request.user,
            })
            send_email_async(subject, html_message, [camp.requested_by.email])

            messages.success(request, f"✅ '{camp.title}' marked as {status}.")
        else:
            messages.error(request, "Invalid status update.")

        return redirect('advocate_dashboard')


# ✅ Approve from Email
class ApproveLegalCampView(View):
    template_name = 'legal/approve_from_email.html'

    def get(self, request, camp_id):
        camp = get_object_or_404(LegalAwarenessCamp, id=camp_id)
        if camp.status == 'Approved':
            return render(request, self.template_name, {'camp': camp, 'already_approved': True})
        return render(request, self.template_name, {'camp': camp, 'already_approved': False})

    def post(self, request, camp_id):
        camp = get_object_or_404(LegalAwarenessCamp, id=camp_id)
        if camp.status != 'Approved':
            camp.status = 'Approved'
            camp.save()

            subject = f"✅ Legal Camp Approved: {camp.title}"
            html_message = render_to_string('legal/legal_camp_status_update_mail.html', {
                'camp': camp,
                'status': 'Approved',
                'advocate': 'Email Approval',
            })
            send_email_async(subject, html_message, [camp.requested_by.email])

        return render(request, self.template_name, {'camp': camp, 'approved_now': True})


# 🗓️ Schedule Legal Camp

# 📰 Article List (Visible to all)
class LegalArticleListView(LoginRequiredMixin, View):
    def get(self, request):
        articles = LegalArticle.objects.all().order_by('-created_at')
        return render(request, 'legal/articles.html', {'articles': articles})


# 💬 Q&A Section
class LegalQuestionView(LoginRequiredMixin, View):
    def get(self, request):
        questions = LegalQuestion.objects.all().order_by('-created_at')
        form = LegalQuestionForm()
        return render(request, 'legal/questions.html', {'questions': questions, 'form': form})

    def post(self, request):
        form = LegalQuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.asked_by = request.user
            q.save()
            messages.success(request, "✅ Your question has been submitted.")
        return redirect('legal_info')

class AnswerLegalQuestionView(LoginRequiredMixin, View):
    def post(self, request, question_id):
        question = get_object_or_404(LegalQuestion, pk=question_id)

        if question.is_answered:
            messages.warning(request, "This question is already answered.")
            return redirect('advocate_dashboard')

        answer = request.POST.get('answer')
        question.answer = answer
        question.answered_by = request.user
        question.is_answered = True
        question.answered_at = timezone.now()
        question.save()

        # send email to questioner
        subject = "Your Legal Question Has Been Answered"
        message = f"Hi {question.asked_by.username},\n\nYour question:\n{question.question}\n\nAnswer:\n{answer}\n\nBest regards,\nNyayaSakhi Team"
        question.asked_by.email_user(subject, message)

        messages.success(request, "Answer sent successfully!")
        return redirect('advocate_dashboard')


class EditLegalArticleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        article = get_object_or_404(LegalArticle, pk=pk, created_by=request.user)
        title = request.POST.get('title')
        content = request.POST.get('content')

        if title and content:
            article.title = title
            article.content = content
            article.save()
            messages.success(request, "Article updated successfully.")
        else:
            messages.error(request, "Both title and content are required.")
        return redirect('advocate_dashboard')

class DeleteLegalArticleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        article = get_object_or_404(LegalArticle, pk=pk, author=request.user)
        article.delete()
        messages.success(request, "Article deleted successfully.")
        return redirect('legal_articles')


class LegalArticleDetailView(View):
    def get(self, request, pk):
        article = get_object_or_404(LegalArticle, pk=pk)
        return render(request, 'legal/article_details.html', {'article': article})
