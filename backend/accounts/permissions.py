from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSheikh(BasePermission):
    """Only the Sheikh can perform this action (e.g. archive/delete content)."""

    message = 'Only the Sheikh can perform this action.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_sheikh


class IsContentCreator(BasePermission):
    """Sheikh or a content manager can create and edit content."""

    message = 'Only the Sheikh or a content manager can perform this action.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_content_creator


class IsContentCreatorOrReadOnly(BasePermission):
    """Anonymous/regular users get read-only access; content creators can write."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_content_creator


class IsOwnerOrContentCreator(BasePermission):
    """
    Object-level permission:
    - Content creators (Sheikh/manager) can act on any object.
    - Regular users can only act on their own objects.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and request.user.is_content_creator:
            return True
        return obj.user == request.user
