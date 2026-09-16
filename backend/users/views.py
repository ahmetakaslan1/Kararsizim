from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, AdminUserListSerializer
from polls.serializers import PollListSerializer
from polls.models import Poll, Vote

User = get_user_model()

class RegisterView(APIView):
    """POST /api/auth/register/ — Yeni kullanıcı kaydı ve doğrulama e-postası gönderimi."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Hesabı pasif yapıyoruz
            user.is_active = False
            user.save()
            
            # E-posta onay token'ı ve linki üret
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_link = f"{settings.FRONTEND_URL.rstrip('/')}/verify-email.html?uid={uid}&token={token}"
            
            html_content = f"""
            <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
                <h2>Kararsızım'a Hoş Geldin, {user.username}!</h2>
                <p>Hesabınızı doğrulamak için aşağıdaki butona tıklayın:</p>
                <a href="{verification_link}" style="display: inline-block; padding: 12px 24px; color: #ffffff; background-color: #6366f1; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 10px 0;">Hesabımı Doğrula</a>
                <p style="margin-top: 20px; font-size: 13px; color: #6b7280;">Buton çalışmıyorsa şu linki kopyalayıp tarayıcınıza yapıştırın:<br>{verification_link}</p>
            </div>
            """
            
            send_mail(
                'Kararsızım - E-posta Doğrulama',
                f'Merhaba {user.username},\n\nHesabınızı doğrulamak için tıklayın: {verification_link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=html_content
            )
            
            return Response({'detail': 'Kayıt başarılı. Lütfen e-postanızı kontrol ederek hesabınızı onaylayın.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    """POST /api/auth/verify-email/ — E-posta onaylama işlemi."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        
        if not uidb64 or not token:
            return Response({'detail': 'UID ve Token gereklidir.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            
            # Hoş geldin maili
            html_content = f"""
            <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
                <h2>Harika, {user.username}! 🎉</h2>
                <p>Hesabınız başarıyla onaylandı. Artık Kararsızım platformunun bir parçasısınız.</p>
                <p>Hemen giriş yapıp fikirlerinizi sormaya başlayabilirsiniz!</p>
            </div>
            """
            
            send_mail(
                'Aramıza Hoş Geldin!',
                f'Merhaba {user.username}, Hesabınız onaylandı.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=html_content
            )
            
            return Response({'detail': 'Hesabınız başarıyla onaylandı.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Geçersiz veya süresi dolmuş bağlantı.'}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """POST /api/auth/password-reset/ — Şifre sıfırlama e-postası gönderir."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'E-posta adresi gereklidir.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Güvenlik amacıyla e-posta bulunamasa bile hata dönmüyoruz.
            return Response({'detail': 'Şifre sıfırlama bağlantısı e-posta adresinize gönderildi.'}, status=status.HTTP_200_OK)
            
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password.html?uid={uid}&token={token}"
        
        html_content = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
            <h2>Merhaba {user.username},</h2>
            <p>Şifrenizi sıfırlamak için bir istekte bulundunuz. Aşağıdaki butona tıklayarak yeni şifrenizi belirleyebilirsiniz:</p>
            <a href="{reset_link}" style="display: inline-block; padding: 12px 24px; color: #ffffff; background-color: #ef4444; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 10px 0;">Şifremi Sıfırla</a>
            <p style="margin-top: 20px; font-size: 13px; color: #6b7280;">Bu isteği siz yapmadıysanız, bu e-postayı görmezden gelebilirsiniz.<br><br>Buton çalışmıyorsa şu linki kopyalayıp tarayıcınıza yapıştırın:<br>{reset_link}</p>
        </div>
        """
        
        send_mail(
            'Kararsızım - Şifre Sıfırlama',
            f'Şifrenizi sıfırlamak için tıklayın: {reset_link}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
            html_message=html_content
        )
        
        return Response({'detail': 'Şifre sıfırlama bağlantısı e-posta adresinize gönderildi.'}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """POST /api/auth/password-reset-confirm/ — Yeni şifreyi ayarlar."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        if not uidb64 or not token or not new_password:
            return Response({'detail': 'Tüm alanlar (uid, token, new_password) gereklidir.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({'detail': 'Şifreniz başarıyla değiştirildi. Şimdi giriş yapabilirsiniz.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Geçersiz veya süresi dolmuş bağlantı.'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/ — Giriş, JWT token döner."""
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    """POST /api/auth/logout/ — Refresh token'ı blacklist'e ekler."""

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Başarıyla çıkış yapıldı.'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'detail': 'Geçersiz token.'}, status=status.HTTP_400_BAD_REQUEST)


class UserMeView(APIView):
    """GET /api/auth/me/ — Profil bilgileri, açılan ve oylanan anketler."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        created_polls = Poll.objects.filter(creator=user).prefetch_related('options').order_by('-created_at')
        
        voted_polls_ids = Vote.objects.filter(user=user).values_list('poll_id', flat=True)
        voted_polls = Poll.objects.filter(id__in=voted_polls_ids).select_related('creator').prefetch_related('options').order_by('-created_at')
        
        return Response({
            'username': user.username,
            'email': user.email,
            'is_admin': getattr(user, 'is_admin', False),
            'date_joined': user.date_joined,
            'created_polls': PollListSerializer(created_polls, many=True).data,
            'voted_polls': PollListSerializer(voted_polls, many=True).data,
        }, status=status.HTTP_200_OK)


from django.db.models import Count
from rest_framework import generics

class IsAdminPermission(IsAuthenticated):
    def has_permission(self, request, view):
        is_auth = super().has_permission(request, view)
        return is_auth and getattr(request.user, 'is_admin', False)

class AdminUserListView(generics.ListAPIView):
    """GET /api/auth/admin/users/ — Tüm kullanıcıları listeler (Sadece Admin)."""
    permission_classes = [IsAdminPermission]
    serializer_class = AdminUserListSerializer

    def get_queryset(self):
        return User.objects.annotate(polls_count=Count('polls')).order_by('-date_joined')

class AdminUserDeleteView(generics.DestroyAPIView):
    """DELETE /api/auth/admin/users/<id>/ — Kullanıcı siler (Sadece Admin)."""
    permission_classes = [IsAdminPermission]
    queryset = User.objects.all()
