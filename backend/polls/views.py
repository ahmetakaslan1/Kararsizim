from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.db import IntegrityError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from .permissions import IsOwnerOrReadOnly

from .models import Poll, PollOption, Vote
from .serializers import (
    PollListSerializer,
    PollDetailSerializer,
    PollCreateSerializer,
    VoteSerializer,
)


class PollListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/polls/ → tüm aktif anketler (herkese açık)
    POST /api/polls/ → yeni anket oluştur (giriş zorunlu)
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Poll.objects.filter(is_active=True).select_related('creator').prefetch_related('options')
        
        # Kategori Filtrelemesi
        category = self.request.query_params.get('category')
        if category and category != 'all':
            queryset = queryset.filter(category=category)
            
        # Sıralama
        sort = self.request.query_params.get('sort')
        if sort == 'popular':
            queryset = queryset.annotate(
                total_votes=Coalesce(Sum('options__vote_count'), 0)
            ).order_by('-total_votes', '-created_at')
        else:
            queryset = queryset.order_by('-created_at')
            
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PollCreateSerializer
        return PollListSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        poll = serializer.save(creator=request.user)
        # Oluşturulan anketi detay serializer ile döndür
        return Response(
            PollDetailSerializer(poll).data,
            status=status.HTTP_201_CREATED
        )


class PollDetailView(generics.RetrieveDestroyAPIView):
    """
    GET /api/polls/<id>/ → tek anket detayı (herkese açık).
    DELETE /api/polls/<id>/ → anketi sil (sadece anket sahibi).
    """
    queryset = Poll.objects.filter(is_active=True).select_related('creator').prefetch_related('options')
    serializer_class = PollDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class VoteView(APIView):
    """
    POST /api/polls/<id>/vote/ → oy ver (herkese açık)
    Body: { option_id: int, voter_token?: str }
    """
    permission_classes = [AllowAny]

    def get_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    def post(self, request, pk):
        # Anketi bul
        try:
            poll = Poll.objects.get(pk=pk, is_active=True)
        except Poll.DoesNotExist:
            return Response({'detail': 'Anket bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)

        # Girdiyi doğrula
        serializer = VoteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        option_id = serializer.validated_data['option_id']
        voter_token = serializer.validated_data.get('voter_token', '')

        # Seçeneğin bu ankete ait olduğunu doğrula
        try:
            option = poll.options.get(pk=option_id)
        except PollOption.DoesNotExist:
            return Response({'detail': 'Bu seçenek bu ankete ait değil.'}, status=status.HTTP_400_BAD_REQUEST)

        # Mükerrer oy kontrolü
        if request.user.is_authenticated:
            if Vote.objects.filter(poll=poll, user=request.user).exists():
                return Response({'detail': 'Bu ankete zaten oy verdiniz.'}, status=status.HTTP_409_CONFLICT)
        elif voter_token:
            if Vote.objects.filter(poll=poll, voter_token=voter_token).exists():
                return Response({'detail': 'Bu ankete zaten oy verdiniz.'}, status=status.HTTP_409_CONFLICT)

        # Oyu kaydet — F() ile race condition'dan güvenli artırım
        try:
            Vote.objects.create(
                poll=poll,
                option=option,
                user=request.user if request.user.is_authenticated else None,
                voter_token=voter_token if not request.user.is_authenticated else '',
                ip_address=self.get_ip(request),
            )
            PollOption.objects.filter(pk=option.pk).update(vote_count=F('vote_count') + 1)
        except IntegrityError:
            return Response({'detail': 'Bu ankete zaten oy verdiniz.'}, status=status.HTTP_409_CONFLICT)

        # Güncel seçenekleri döndür
        poll.refresh_from_db()
        return Response(PollDetailSerializer(poll).data, status=status.HTTP_200_OK)
