from django.urls import path
from . import views

urlpatterns = [
    # Volunteer: Create Request
    path('request/', views.MedicalCampRequestView.as_view(), name='medical_camp_request'),

    # Volunteer: View Own Requests
    path('list/', views.VolunteerMedicalCampListView.as_view(), name='volunteer_medical_list'),

    # Beneficiary: View Info
    path('info/', views.MedicalCampInfoView.as_view(), name='medical_info'),

    # Detailed View
    path('<int:pk>/', views.MedicalCampDetailView.as_view(), name='medical_camp_detail'),

    # Admin/Volunteer: Schedule or Reschedule

    # Hospital: Approve/Reject via Email
    path('approve/<uuid:token>/', views.HospitalApproveRequestView.as_view(), name='hospital_approve_request'),
    
]
