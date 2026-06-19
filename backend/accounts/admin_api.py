"""
accounts/admin_api.py — in-app user administration for the Sheikh.

Separate from Django's admin site. Gated by IsSheikh. Supports listing users,
searching, and changing a user's role / active flag. Deletion is intentionally
not offered — accounts are deactivated, never hard-deleted — and the acting
Sheikh cannot lock themselves out (no self role-change or self-deactivation).
"""
from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsSheikh
from base.pagination import StandardPagination
from base.responses import success
from base.serializers import display_name

User = get_user_model()


class AdminUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    is_sheikh = serializers.BooleanField(read_only=True)
    is_content_creator = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            'public_id', 'email', 'username', 'name', 'role', 'is_active',
            'is_sheikh', 'is_content_creator', 'date_joined',
        )
        read_only_fields = fields

    def get_name(self, obj) -> str:
        return display_name(obj)


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('role', 'is_active')

    def validate_role(self, value):
        valid = {choice[0] for choice in User.ROLE_CHOICES}
        if value not in valid:
            raise serializers.ValidationError(f'role must be one of {sorted(valid)}.')
        return value


@extend_schema(tags=['admin'])
class AdminUserListView(APIView):
    permission_classes = (IsSheikh,)

    @extend_schema(
        summary='List user accounts (Sheikh only)',
        parameters=[OpenApiParameter('search', str, description='Match email or username')],
        responses={200: AdminUserSerializer(many=True)},
    )
    def get(self, request):
        qs = User.objects.select_related('profile').order_by('-date_joined')
        search = request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(Q(email__icontains=search) | Q(username__icontains=search))
        role = request.query_params.get('role', '').strip()
        if role:
            qs = qs.filter(role=role)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(AdminUserSerializer(page, many=True).data)


@extend_schema(tags=['admin'])
class AdminUserDetailView(APIView):
    permission_classes = (IsSheikh,)

    def _get(self, public_id):
        try:
            return User.objects.select_related('profile').get(public_id=public_id)
        except User.DoesNotExist:
            return None

    @extend_schema(summary='Retrieve a user (Sheikh only)', responses={200: AdminUserSerializer})
    def get(self, request, public_id):
        user = self._get(public_id)
        if user is None:
            return Response(
                {'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'User not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return success(AdminUserSerializer(user).data)

    @extend_schema(
        summary='Update a user role / active flag (Sheikh only)',
        request=AdminUserUpdateSerializer,
        responses={200: AdminUserSerializer},
    )
    def patch(self, request, public_id):
        user = self._get(public_id)
        if user is None:
            return Response(
                {'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'User not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Anti-lockout: a Sheikh cannot change their own role or deactivate self.
        if user.pk == request.user.pk:
            return Response(
                {'success': False, 'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'You cannot change your own role or active status.',
                }},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ser = AdminUserUpdateSerializer(user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return success(AdminUserSerializer(user).data)
