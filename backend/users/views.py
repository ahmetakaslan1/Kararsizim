from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer


class RegisterView(APIView):
    """POST /api/auth/register/ — Yeni kullanıcı kaydı."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Token üret
            refresh = RefreshToken.for_user(user)
            return Response({
                'username': user.username,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


from rest_framework.permissions import IsAuthenticated
from polls.serializers import PollListSerializer
from polls.models import Poll, Vote

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
            'email': user.email, # Sadece kullanıcının kendisine döner
            'date_joined': user.date_joined,
            'created_polls': PollListSerializer(created_polls, many=True).data,
            'voted_polls': PollListSerializer(voted_polls, many=True).data,
        }, status=status.HTTP_200_OK)
