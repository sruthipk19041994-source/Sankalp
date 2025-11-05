from django.urls import path
from . import views

urlpatterns = [
    # 🌿 Static Pages
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),

    # 👤 Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # 🔐 Password Reset (Custom HTML Email Flow)
    path('reset-password/<str:token>/', views.ResetPasswordView.as_view(), name='reset_password'),

    # 🧭 Dashboards
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('admin/dashboard/', views.DashboardView.as_view(), name='admin_dashboard'),
    path('volunteer/dashboard/', views.DashboardView.as_view(), name='volunteer_dashboard'),
    path('donor/dashboard/', views.DashboardView.as_view(), name='donor_dashboard'),
    path('beneficiary/dashboard/', views.DashboardView.as_view(), name='beneficiary_dashboard'),
    path('advocate/dashboard/', views.DashboardView.as_view(), name='advocate_dashboard'),
    path('supporter/dashboard/', views.DashboardView.as_view(), name='supporter_dashboard'),

    # 👑 Admin - User Management
    path('manage/users/', views.AdminUserManagementView.as_view(), name='admin_user_management'),
    path('manage/users/edit/<int:pk>/', views.AdminUserEditView.as_view(), name='admin_user_edit'),
    path('manage/users/delete/<int:pk>/', views.AdminUserDeleteView.as_view(), name='admin_user_delete'),

    # 🌍 Admin - Campaign Management
    path('manage/campaigns/', views.AdminCampaignManagementView.as_view(), name='admin_campaign_management'),
]
