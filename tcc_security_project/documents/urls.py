from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
	path('', views.document_list_view, name = 'list'),
	path('upload/', views.upload_document_view, name='upload'),
	path('download/<int:doc_id>/', views.secure_download_view, name='download'),
	path('audit/', views.audit_log_view, name='audit'),
]