from django.urls import path
from .views import (
    EducationRequestView, EducationInfoView, VolunteerEducationRequestsView,
    VolunteerForwardRequestView, ApproveStudentRequestView,
    RejectStudentRequestView, EducationDetailView,AdminEducationRequestsView
)

urlpatterns = [
    path('request/', EducationRequestView.as_view(), name='education_request'),
    path('info/', EducationInfoView.as_view(), name='education_info'),
    path('volunteer/requests/', VolunteerEducationRequestsView.as_view(), name='volunteer_education_requests'),
    path('admin/requests/', AdminEducationRequestsView.as_view(), name='admin_education_requests'),
    path('volunteer/forward/<int:pk>/', VolunteerForwardRequestView.as_view(), name='volunteer_forward_request'),
    path('donor/approve/<int:request_id>/', ApproveStudentRequestView.as_view(), name='approve_student_request'),
    path('donor/reject/<int:request_id>/', RejectStudentRequestView.as_view(), name='reject_student_request'),
    path('details/', EducationDetailView.as_view(), name='education_details'),
]
