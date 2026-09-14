from rest_framework import serializers
from users.serializers import PublicUserSerializer
from .models import Poll, PollOption, Vote


class PollOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollOption
        fields = ('id', 'text', 'vote_count')
        read_only_fields = ('vote_count',)


class PollListSerializer(serializers.ModelSerializer):
    """Liste görünümü — kısa bilgiler."""
    creator = PublicUserSerializer(read_only=True)
    options = PollOptionSerializer(many=True, read_only=True)
    total_votes = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = ('id', 'question', 'category', 'creator', 'created_at', 'is_active', 'options', 'total_votes')

    def get_total_votes(self, obj):
        return sum(opt.vote_count for opt in obj.options.all())


class PollDetailSerializer(PollListSerializer):
    """Detay görünümü — aynı ama ileride genişletilebilir."""
    class Meta(PollListSerializer.Meta):
        pass


class PollCreateSerializer(serializers.ModelSerializer):
    """Anket oluşturma — 2-5 seçenek zorunlu."""
    options = serializers.ListField(
        child=serializers.CharField(max_length=200),
        min_length=2,
        max_length=5,
        write_only=True
    )

    class Meta:
        model = Poll
        fields = ('question', 'category', 'options')

    def validate_options(self, options):
        # Boş seçenek ve tekrar kontrolü
        cleaned = [opt.strip() for opt in options]
        if any(not opt for opt in cleaned):
            raise serializers.ValidationError('Seçenekler boş bırakılamaz.')
        if len(set(cleaned)) != len(cleaned):
            raise serializers.ValidationError('Seçenekler birbirinden farklı olmalıdır.')
        return cleaned

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        poll = Poll.objects.create(**validated_data)
        for text in options_data:
            PollOption.objects.create(poll=poll, text=text)
        return poll


class VoteSerializer(serializers.Serializer):
    """Oy verme — option_id ve isteğe bağlı voter_token."""
    option_id = serializers.IntegerField()
    voter_token = serializers.CharField(max_length=128, required=False, default='')
