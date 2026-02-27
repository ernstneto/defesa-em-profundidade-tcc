from django.urls import path, include
from . import views
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
import base64
from io import BytesIO
from django.forms import Form
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import views as auth_views
from rest_framework.authtoken.views import obtain_auth_token
from . import api_views


app_name = 'accounts'

urlpatterns = [
	path('register/', views.register_view, name='register'),
	path('login/', views.login_view, name='login'),
	path('logout/', views.logout_view, name='logout'),
	path('mydata/', views.data_profile_view, name='mydata'),
	path('profile/<int:user_id>/', views.profile_view, name='profile'),
	#2FA/ MFA
	path('otp/setup/', views.otp_setup_view, name='otp_setup'),
	path('otp/verify/', views.otp_verify_setup_view, name='otp_verify_setup'),
	path('otp/manage/', views.otp_manage_view, name='otp_manage'),
	path('otp/remove/<int:device_id>/', views.otp_remove_view, name='otp_remove'),
	path('otp/login-verify/', views.otp_login_verify_view, name='otp_login_verify'),
	#Reset Or Edit
	path('password_reset/',
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html',
                                              email_template_name='accounts/password_reset_email.html',
                                              subject_template_name='accounts/password_reset_subject.txt',
                                              success_url='/accounts/password_reset/done/'),
         name='password_reset'),
	path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html',
                                                     success_url='/accounts/reset/done/'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    #Login History
    path('history/', views.login_history_view, name='login_history'),
    # --- URL PARA MUDANÇA DE E-MAIL ---
    path('email-change/', views.email_change_request_view, name='email_change_request'),
    path('email-confirm/<str:token>/', views.email_change_confirm_view, name='email_change_confirm'),
    # --- SECURITY ----
    path('security-check/', views.security_check_view, name='security_check'),
    path('finance-check/', views.finance_security_check_view, name='finance_security_check'),
    # ---- MOBILE ----
    path('api/login/', obtain_auth_token, name='api_token_auth'),
    path('api/user/', api_views.UserProfileAPI.as_view(), name='api_user_profile'),
    # ---- VPN ----
    path('vpn/', views.vpn_dashboard_view, name='vpn_dashboard'),
    path('vpn/download/', views.download_vpn_config_view, name='download_vpn'),
    # ---- SSL ----
    path('ssl-check/', views.ssl_check_view, name='sll_check'),
    path('api/ssl-check/', views.ssl_check_view, name='api_ssl_check'),
    path('', views.home_segura, name='home'),
]