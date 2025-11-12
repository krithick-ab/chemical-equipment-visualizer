from django.urls import path
from .views import UploadCSVAPIView, HistoryAPIView, DownloadPDFReportAPIView, DatasetDetailAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

class PingView(APIView):
    def get(self, request):
        return Response({"ok": True})

urlpatterns = [
    path('upload/', UploadCSVAPIView.as_view(), name='upload_csv'),
    path('history/', HistoryAPIView.as_view(), name='history'),
    path('datasets/<int:dataset_id>/', DatasetDetailAPIView.as_view(), name='dataset_detail'),
    path('ping/', PingView.as_view(), name='ping'),
    path('download-report/latest/', DownloadPDFReportAPIView.as_view(), {'dataset_id': 'latest'}, name='download_latest_report'),
    path('download-report/<int:dataset_id>/', DownloadPDFReportAPIView.as_view(), name='download_report'),
]