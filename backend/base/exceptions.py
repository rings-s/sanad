import logging

from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed, NotAuthenticated, PermissionDenied as DRFPermissionDenied,
    NotFound, Throttled, ValidationError as DRFValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)

_STATUS_CODE_MAP = {
    400: 'VALIDATION_ERROR',
    401: 'AUTHENTICATION_REQUIRED',
    403: 'PERMISSION_DENIED',
    404: 'NOT_FOUND',
    429: 'RATE_LIMITED',
    500: 'SERVER_ERROR',
}


def _error_envelope(code: str, message: str, details=None, http_status=400):
    payload = {'success': False, 'error': {'code': code, 'message': message}}
    if details:
        payload['error']['details'] = details
    return Response(payload, status=http_status)


def sanad_exception_handler(exc, context):
    """
    Unified exception handler — every error response follows:
      { "success": false, "error": { "code": "...", "message": "...", "details": {...} } }
    """
    if isinstance(exc, PermissionDenied):
        return _error_envelope('PERMISSION_DENIED', str(exc) or 'Permission denied.', http_status=403)

    if isinstance(exc, DjangoValidationError):
        msg = exc.message if hasattr(exc, 'message') else str(exc)
        return _error_envelope('VALIDATION_ERROR', msg, http_status=400)

    response = drf_exception_handler(exc, context)

    if response is None:
        view = context.get('view')
        logger.exception(
            'Unhandled exception in %s.%s',
            view.__class__.__name__ if view else '?',
            context.get('request').method if context.get('request') else '?',
        )
        return _error_envelope('SERVER_ERROR', 'A server error occurred.', http_status=500)

    http_status = response.status_code
    code = _STATUS_CODE_MAP.get(http_status, 'ERROR')
    data = response.data

    # Extract human-readable message and field-level details
    if isinstance(data, dict):
        message = data.get('detail', '')
        if hasattr(message, 'code'):
            message = str(message)
        details = {k: v for k, v in data.items() if k != 'detail'} or None
    elif isinstance(data, list):
        message = str(data[0]) if data else 'An error occurred.'
        details = None
    else:
        message = str(data)
        details = None

    if not message:
        message = {
            400: 'Invalid input.',
            401: 'Authentication credentials were not provided.',
            403: 'You do not have permission to perform this action.',
            404: 'Not found.',
            429: 'Too many requests.',
        }.get(http_status, 'An error occurred.')

    # For validation errors, reshape field details
    if http_status == 400 and isinstance(response.data, dict) and response.data:
        non_field = response.data.get('non_field_errors') or response.data.get('detail')
        field_errors = {k: v for k, v in response.data.items()
                        if k not in ('detail', 'non_field_errors')}
        if non_field:
            message = str(non_field[0]) if isinstance(non_field, list) else str(non_field)
        details = field_errors or None

    return _error_envelope(code, message, details, http_status)
