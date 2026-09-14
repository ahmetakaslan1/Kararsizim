from django.contrib import admin
from .models import Poll, PollOption, Vote


class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 0
    readonly_fields = ('vote_count',)


class VoteInline(admin.TabularInline):
    model = Vote
    extra = 0
    readonly_fields = ('user', 'voter_token', 'ip_address', 'created_at')
    can_delete = False


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'creator', 'created_at', 'is_active', 'total_votes')
    list_filter = ('is_active', 'created_at')
    search_fields = ('question', 'creator__username')
    inlines = [PollOptionInline]
    readonly_fields = ('created_at',)

    def total_votes(self, obj):
        return sum(opt.vote_count for opt in obj.options.all())
    total_votes.short_description = 'Toplam oy'


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('poll', 'option', 'user', 'voter_token', 'ip_address', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'voter_token', 'ip_address')
    readonly_fields = ('poll', 'option', 'user', 'voter_token', 'ip_address', 'created_at')
