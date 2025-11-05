from django.urls import path
from . import views

urlpatterns = [
    path('request/', views.LegalCampRequestView.as_view(), name='request_legal_camp'),
    path('info/', views.LegalInfoView.as_view(), name='legal_info'),
    path('advocate-list/', views.AdvocateListView.as_view(), name='advocate_list'),
    path('advocate/dashboard/', views.AdvocateDashboardView.as_view(), name='advocate_dashboard'),
    path('advocate/camp/<int:camp_id>/update/', views.UpdateCampStatusView.as_view(), name='update_camp_status'),
    path('approve/<int:camp_id>/', views.ApproveLegalCampView.as_view(), name='approve_legal_camp'),
    path('articles/', views.LegalArticleListView.as_view(), name='legal_articles'),
    path('questions/', views.LegalQuestionView.as_view(), name='legal_questions'),
    path('questions/answer/<int:question_id>/', views.AnswerLegalQuestionView.as_view(), name='answer_legal_question'),
    path('article/edit/<int:pk>/', views.EditLegalArticleView.as_view(), name='edit_legal_article'),
path('article/delete/<int:pk>/', views.DeleteLegalArticleView.as_view(), name='delete_legal_article'),
path('article/<int:pk>/', views.LegalArticleDetailView.as_view(), name='legal_article_detail'),


]

