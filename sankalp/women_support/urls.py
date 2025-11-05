from django.urls import path
from . import views

urlpatterns = [
    # 🌸 Women Support Info
    path('info/', views.WomenSupportInfoView.as_view(), name='women_support_info'),

    # 🌸 Campaign Management
    path('request/', views.CampaignRequestView.as_view(), name='request_campaign'),
    path('approve/<int:pk>/', views.CampaignApprovalView.as_view(), name='approve_campaign'),
    path('schedule/<int:campaign_id>/', views.ScheduleWomenCampaignView.as_view(), name='schedule_women_campaign'),

    # 🧡 Supporter Dashboard
    path('supporter/dashboard/', views.SupporterDashboardView.as_view(), name='supporter_dashboard'),

    # 📝 Article Management
    path('articles/', views.WomenSupportArticleView.as_view(), name='women_support_articles'),
    path('articles/create/', views.WomenSupportArticleCreateView.as_view(), name='create_article'),
    path('articles/edit/<int:pk>/', views.WomenSupportArticleEditView.as_view(), name='edit_article'),
    path('articles/delete/<int:pk>/', views.WomenSupportArticleDeleteView.as_view(), name='delete_article'),

    # 🌸 New additions
    path('articles/view/<int:pk>/', views.ViewArticleView.as_view(), name='view_article'),

    # 💬 Q&A Section
    path('questions/', views.WomenSupportQuestionView.as_view(), name='women_support_questions'),
    path('questions/ask/', views.WomenAskQuestionView.as_view(), name='women_ask_question'),
    path('questions/reply/<int:pk>/', views.WomenSupportAnswerView.as_view(), name='reply_question'),
    path('campaign/<int:pk>/approve/', views.ApproveWomenCampaignView.as_view(), name='approve_women_campaign'),
    path('campaign/<int:pk>/reject/', views.RejectWomenCampaignView.as_view(), name='reject_women_campaign'),
    path('campaign/<int:pk>/handled/', views.CampaignHandledView.as_view(), name='campaign_handled'),
    path('campaign/<int:pk>/', views.ViewCampaignDetailView.as_view(), name='view_campaign'),
]

