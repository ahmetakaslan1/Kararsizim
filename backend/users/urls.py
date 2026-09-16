from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, UserMeView,
    VerifyEmailView, PasswordResetRequestView, PasswordResetConfirmView,
    AdminUserListView, AdminUserDeleteView, AdminUserPollsView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('verify-email/', VerifyEmailView.as_view(), name='auth-verify-email'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='auth-password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('me/', UserMeView.as_view(), name='auth-me'),
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/users/<int:pk>/', AdminUserDeleteView.as_view(), name='admin-user-delete'),
    path('admin/users/<int:user_id>/polls/', AdminUserPollsView.as_view(), name='admin-user-polls'),
]
