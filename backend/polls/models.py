from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Poll(models.Model):
    """Anket modeli."""
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='polls',
        verbose_name='Oluşturan'
    )
    question = models.CharField(max_length=500, verbose_name='Soru')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma tarihi')
    is_active = models.BooleanField(default=True, verbose_name='Aktif mi?')

    class Meta:
        verbose_name = 'Anket'
        verbose_name_plural = 'Anketler'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.question[:60]}...' if len(self.question) > 60 else self.question


class PollOption(models.Model):
    """Anket seçeneği modeli."""
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name='Anket'
    )
    text = models.CharField(max_length=200, verbose_name='Seçenek metni')
    vote_count = models.PositiveIntegerField(default=0, verbose_name='Oy sayısı')

    class Meta:
        verbose_name = 'Anket seçeneği'
        verbose_name_plural = 'Anket seçenekleri'

    def __str__(self):
        return f'{self.text} ({self.poll})'


class Vote(models.Model):
    """Oy modeli — hem üye hem anonim kullanıcıları destekler."""
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name='Anket'
    )
    option = models.ForeignKey(
        PollOption,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name='Seçenek'
    )
    # Üye kullanıcı
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='votes',
        verbose_name='Kullanıcı'
    )
    # Anonim kullanıcı için kimlik
    voter_token = models.CharField(
        max_length=128,
        blank=True,
        default='',
        verbose_name='Anonim token'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP adresi'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oy tarihi')

    class Meta:
        verbose_name = 'Oy'
        verbose_name_plural = 'Oylar'
        constraints = [
            # Üye kullanıcı aynı ankete birden fazla oy veremez
            models.UniqueConstraint(
                fields=['poll', 'user'],
                condition=models.Q(user__isnull=False),
                name='unique_vote_per_user'
            ),
            # Anonim kullanıcı aynı ankete aynı token ile birden fazla oy veremez
            models.UniqueConstraint(
                fields=['poll', 'voter_token'],
                condition=models.Q(voter_token__gt=''),
                name='unique_vote_per_token'
            ),
        ]

    def __str__(self):
        identifier = self.user.username if self.user else f'anonim:{self.voter_token[:8]}'
        return f'{identifier} → {self.option.text}'
