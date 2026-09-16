from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Sadece nesnenin sahibi (creator) düzenleme/silme işlemi yapabilir.
    Güvenli metodlar (GET, HEAD, OPTIONS) herkese açıktır.
    """
    def has_object_permission(self, request, view, obj):
        # Okuma izinleri herkese açıktır (GET, HEAD veya OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Yazma izinleri (DELETE, vb.) sadece anketin sahibine (creator) veya admine verilir
        return obj.creator == request.user or getattr(request.user, 'is_admin', False)
