from django.urls import path
from .views import PollListCreateView, PollDetailView, VoteView

urlpatterns = [
    path('', PollListCreateView.as_view(), name='poll-list-create'),
    path('<int:pk>/', PollDetailView.as_view(), name='poll-detail'),
    path('<int:pk>/vote/', VoteView.as_view(), name='poll-vote'),
]
