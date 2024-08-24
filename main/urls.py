# urls.py
from django.conf.urls.static import static
from django.urls import path

from scms import settings
from .views import RegisterView, LoginView, CreateComplaintView, DownloadView, HistoryView, GetUserInfoView, \
    AdminComplaintView, AdminComplaintUpdateView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    # Add other views here
    path('history/', HistoryView.as_view(), name='history'),
    path('download/', DownloadView.as_view(), name='download'),
    path('complaint/', CreateComplaintView.as_view(), name='upload'),
    path('admin-complaints/<int:uid>/', AdminComplaintView.as_view(), name='admin-complaints'),
    path('admin-complaints/<int:uid>/<int:complaint_id>/', AdminComplaintUpdateView.as_view(),
         name='admin-complaints-update'),
    path('user/', GetUserInfoView.as_view(), name='user')
]

# file storage urls
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
