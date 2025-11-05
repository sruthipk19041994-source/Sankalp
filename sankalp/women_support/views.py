import threading
from datetime import timedelta
from django.utils.timezone import now
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import WomenSupportCampaign, WomenSupportArticle, WomenSupportQuestion
from .forms import (
    CampaignRequestForm,
    CampaignApprovalForm,
    WomenSupportArticleForm,
    WomenSupportQuestionForm,
    WomenSupportAnswerForm
)

# 🌸 Utility — Send Email in a Background Thread
def send_async_email(subject, html_template, context, recipient_list):
    def send_email_task():
        html_content = render_to_string(html_template, context)
        for recipient in recipient_list:
            msg = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [recipient])
            msg.attach_alternative(html_content, "text/html")
            try:
                msg.send()
            except Exception as e:
                print(f"❌ Email sending failed to {recipient}: {e}")
    threading.Thread(target=send_email_task).start()


# 🌸 1️⃣ Common Info
class WomenSupportInfoView(LoginRequiredMixin, View):
    def get(self, request):
        role = request.user.role
        articles, questions = None, None

        if role == 'Volunteer':
            campaigns = WomenSupportCampaign.objects.filter(volunteer=request.user)
            title = "My Requested Campaigns"
        elif role == 'Supporter':
            campaigns = WomenSupportCampaign.objects.filter(supporter=request.user)
            title = "Campaigns You Manage"
        elif role == 'Beneficiary':
            campaigns = WomenSupportCampaign.objects.filter(status__in=['Approved', 'Scheduled'])
            title = "Upcoming Women Support Campaigns"
            articles = WomenSupportArticle.objects.all().order_by('-id')[:5]
            questions = WomenSupportQuestion.objects.filter(answer__isnull=False).order_by('-created_at')[:5]
        else:
            messages.error(request, "Access denied.")
            return redirect('dashboard')

        return render(request, 'women_support/info.html', {
            'campaigns': campaigns,
            'articles': articles,
            'questions': questions,
            'title': title
        })


class CampaignRequestView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'Volunteer':
            messages.error(request, "Access denied.")
            return redirect('dashboard')
        return render(request, 'women_support/request_campaign.html', {'form': CampaignRequestForm()})

    def post(self, request):
        form = CampaignRequestForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.volunteer = request.user
            campaign.status = 'Pending'
            campaign.supporter = form.cleaned_data['supporter']  # assign selected supporter
            campaign.save()

            # 🌸 Notify selected supporter only
            subject = f"🆕 New Women Support Campaign Request: {campaign.title}"
            domain = request.build_absolute_uri('/')[:-1]
            context = {
                'title': campaign.title,
                'description': campaign.description,
                'location': campaign.location,
                'proposed_date': campaign.proposed_date,
                'volunteer_name': request.user.username,
                'status': campaign.status,
                'camp_id': campaign.id,
                'domain': domain,
            }
            recipient_list = [campaign.supporter.email]
            send_async_email(subject, 'women_support/new_campaign_request.html', context, recipient_list)

            messages.success(request, "✅ Your campaign request has been submitted to the selected supporter.")
            return redirect('women_support_info')

        return render(request, 'women_support/request_campaign.html', {'form': form})


# 🌸 3️⃣ Supporter — Approve or Reject campaign from dashboard
class CampaignApprovalView(LoginRequiredMixin, View):
    def get(self, request, pk):
        if request.user.role != 'Supporter':
            messages.error(request, "Access denied.")
            return redirect('dashboard')
        campaign = get_object_or_404(WomenSupportCampaign, pk=pk)
        return render(request, 'women_support/approve_campaign.html', {
            'form': CampaignApprovalForm(instance=campaign),
            'campaign': campaign
        })

    def post(self, request, pk):
        campaign = get_object_or_404(WomenSupportCampaign, pk=pk)
        if campaign.status == 'Approved' and campaign.supporter and campaign.supporter != request.user:
            messages.info(request, f"⚠️ '{campaign.title}' is already approved by {campaign.supporter.username}.")
            return redirect('supporter_dashboard')

        form = CampaignApprovalForm(request.POST, instance=campaign)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.supporter = request.user
            updated.save()

            context = {'title': updated.title, 'volunteer_name': updated.volunteer.username}
            if updated.status == 'Approved':
                subject = f"✅ Your Campaign '{updated.title}' Has Been Approved!"
                send_async_email(subject, 'women_support/campaign_approved.html', context, [updated.volunteer.email])
            elif updated.status == 'Rejected':
                subject = f"❌ Your Campaign '{updated.title}' Was Rejected"
                context['reason'] = request.POST.get('reason', 'Not specified')
                send_async_email(subject, 'women_support/campaign_rejected.html', context, [updated.volunteer.email])

            messages.success(request, f"✅ '{updated.title}' updated successfully.")
            return redirect('supporter_dashboard')
        return render(request, 'women_support/approve_campaign.html', {'form': form, 'campaign': campaign})


# 🌸 4️⃣ Supporter Dashboard
class SupporterDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'Supporter':
            messages.error(request, "Access denied.")
            return redirect('dashboard')
        context = {
            'pending_campaigns': WomenSupportCampaign.objects.filter(status='Pending'),
            'approved_campaigns': WomenSupportCampaign.objects.filter(status='Approved'),
            'rejected_campaigns': WomenSupportCampaign.objects.filter(status='Rejected'),
            'scheduled_campaigns': WomenSupportCampaign.objects.filter(status='Scheduled'),
        }
        return render(request, 'accounts/supporter_dashboard.html', context)


# 🌸 5️⃣ Admin — Schedule campaign
class ScheduleWomenCampaignView(LoginRequiredMixin, View):
    def post(self, request, campaign_id):
        campaign = get_object_or_404(WomenSupportCampaign, id=campaign_id)
        scheduled_date = request.POST.get('scheduled_date')
        scheduled_time = request.POST.get('scheduled_time')

        if scheduled_date and scheduled_time:
            campaign.scheduled_date = scheduled_date
            campaign.scheduled_time = scheduled_time
            campaign.status = 'Scheduled'
            campaign.save()

            subject = f"📅 Campaign Scheduled: {campaign.title}"
            context = {
                'campaign': campaign,
                'date': scheduled_date,
                'time': scheduled_time,
            }
            recipients = [campaign.volunteer.email]
            if campaign.supporter and campaign.supporter.email:
                recipients.append(campaign.supporter.email)

            send_async_email(subject, 'women_support/campaign_scheduled_email.html', context, recipients)

            messages.success(request, f"📅 '{campaign.title}' scheduled for {scheduled_date} at {scheduled_time}.")
        else:
            messages.error(request, "Please provide both a valid date and time.")

        return redirect('admin_campaign_management')


# 🌸 6️⃣ Articles (Create, View, Edit, Delete)
class WomenSupportArticleView(LoginRequiredMixin, View):
    def get(self, request):
        role = request.user.role
        if role == 'Supporter':
            articles = WomenSupportArticle.objects.filter(author=request.user)
        elif role == 'Beneficiary':
            articles = WomenSupportArticle.objects.all()
        else:
            messages.warning(request, "Only supporters and beneficiaries can view articles.")
            return redirect('dashboard')
        return render(request, 'women_support/articles.html', {'articles': articles})


class WomenSupportArticleCreateView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'Supporter':
            messages.error(request, "Only supporters can post articles.")
            return redirect('dashboard')
        return render(request, 'women_support/article_form.html', {
            'form': WomenSupportArticleForm(),
            'form_title': 'Create Article'
        })

    def post(self, request):
        form = WomenSupportArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, "📝 Article published successfully.")
            return redirect('women_support_articles')
        return render(request, 'women_support/article_form.html', {'form': form, 'form_title': 'Create Article'})


class WomenSupportArticleEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        article = get_object_or_404(WomenSupportArticle, pk=pk, author=request.user)
        return render(request, 'women_support/article_form.html', {'form': WomenSupportArticleForm(instance=article)})

    def post(self, request, pk):
        article = get_object_or_404(WomenSupportArticle, pk=pk, author=request.user)
        form = WomenSupportArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Article updated successfully.")
            return redirect('women_support_articles')
        return render(request, 'women_support/article_form.html', {'form': form})


class WomenSupportArticleDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        article = get_object_or_404(WomenSupportArticle, pk=pk, author=request.user)
        article.delete()
        messages.success(request, "🗑️ Article deleted successfully.")
        return redirect('women_support_articles')


class ViewArticleView(LoginRequiredMixin, View):
    def get(self, request, pk):
        article = get_object_or_404(WomenSupportArticle, pk=pk)
        return render(request, 'women_support/article_detail.html', {'article': article})


# 🌸 7️⃣ Beneficiary Q&A (Ask / Answer)
class WomenSupportQuestionView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role == 'Beneficiary':
            questions = WomenSupportQuestion.objects.filter(answer__isnull=False)
        elif request.user.role == 'Supporter':
            questions = WomenSupportQuestion.objects.all().order_by('-created_at')
        else:
            messages.error(request, "Access denied.")
            return redirect('dashboard')
        return render(request, 'women_support/questions.html', {'questions': questions})


class WomenAskQuestionView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'Beneficiary':
            messages.error(request, "Access denied.")
            return redirect('dashboard')
        return render(request, 'women_support/ask_question.html', {'form': WomenSupportQuestionForm()})

    def post(self, request):
        form = WomenSupportQuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.asked_by = request.user
            q.save()
            messages.success(request, "💬 Question submitted successfully.")
            return redirect('women_support_info')
        return render(request, 'women_support/info.html', {'form': form})


class WomenSupportAnswerView(LoginRequiredMixin, View):
    def get(self, request, pk):
        question = get_object_or_404(WomenSupportQuestion, pk=pk)
        form = WomenSupportAnswerForm(instance=question)
        return render(request, 'women_support/reply_question.html', {'question': question, 'form': form})

    def post(self, request, pk):
        question = get_object_or_404(WomenSupportQuestion, pk=pk)
        form = WomenSupportAnswerForm(request.POST, instance=question)

        if form.is_valid():
            answer = form.save(commit=False)
            answer.answered_by = request.user
            answer.answered_at = timezone.now()
            answer.status = "Answered"
            answer.save()

            if question.asked_by.email:
                subject = "Your Question Has Been Answered 🌸"
                context = {'user': question.asked_by, 'question': question.question, 'answer': question.answer}
                send_async_email(subject, 'women_support/email_question_answered.html', context, [question.asked_by.email])

            messages.success(request, "✅ Answer submitted and email sent successfully.")
            return redirect('supporter_dashboard')

        messages.error(request, "⚠️ Please fill in your answer before submitting.")
        return render(request, 'women_support/reply_question.html', {'question': question, 'form': form})


# 🌸 8️⃣ Approve / Reject via Email Link (no login required)
class ApproveWomenCampaignView(View):
    def get(self, request, pk):
        camp = get_object_or_404(WomenSupportCampaign, pk=pk)
        if camp.status == "Pending":
            camp.status = "Approved"
            if request.user.is_authenticated:
                camp.supporter = request.user
            camp.save()
            messages.success(request, "✅ Campaign approved successfully.")
        else:
            messages.info(request, f"⚠️ Campaign is already {camp.status}.")
        return redirect(reverse('campaign_handled', args=[camp.id]))


class RejectWomenCampaignView(View):
    def get(self, request, pk):
        camp = get_object_or_404(WomenSupportCampaign, pk=pk)
        if camp.status == "Pending":
            camp.status = "Rejected"
            camp.save()
            messages.warning(request, "❌ Campaign rejected.")
        else:
            messages.info(request, f"⚠️ Campaign is already {camp.status.lower()}.")
        return redirect(reverse('campaign_handled', args=[camp.id]))


class CampaignHandledView(View):
    def get(self, request, pk):
        camp = get_object_or_404(WomenSupportCampaign, pk=pk)
        return render(request, 'women_support/campaign_handled.html', {'camp': camp})


# 🌸 9️⃣ View campaign details
class ViewCampaignDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        campaign = get_object_or_404(WomenSupportCampaign, pk=pk)
        return render(request, 'women_support/view_campaign.html', {'campaign': campaign})
