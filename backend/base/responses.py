from rest_framework import status
from rest_framework.response import Response


def success(data, status_code=status.HTTP_200_OK):
    return Response({'success': True, 'data': data}, status=status_code)


def created(data):
    return Response({'success': True, 'data': data}, status=status.HTTP_201_CREATED)


class SuccessResponseMixin:
    """
    Wraps Generic API View responses in the standard {success, data} envelope.

    get_read_serializer_class() — override to use a different serializer for
    responses than for input (e.g. return DetailSerializer after a POST).
    """

    def get_read_serializer_class(self):
        return None

    def _read_data(self, instance):
        read_cls = self.get_read_serializer_class()
        if read_cls:
            return read_cls(instance, context=self.get_serializer_context()).data
        return self.get_serializer(instance).data

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response({'success': True, 'data': self._read_data(instance)})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {'success': True, 'data': self._read_data(serializer.instance)},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response({'success': True, 'data': self._read_data(serializer.instance)})
