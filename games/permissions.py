from rest_framework.permissions import BasePermission, SAFE_METHODS


class EsAdministradorOConsulta(BasePermission):
    # Cualquier usuario autenticado puede consultar; solo staff puede modificar.
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_staff


class EsAutorOConsulta(BasePermission):
    # Las reseñas se pueden consultar; solo su autor puede editar o borrar.
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.usuario_id == request.user.id
