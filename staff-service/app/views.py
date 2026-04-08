import hashlib
import hmac
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from .models import Staff
from .serializers import StaffSerializer


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'ok', 'service': 'staff-service'})


@api_view(['POST'])
def staff_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Email và mật khẩu là bắt buộc'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        staff = Staff.objects.get(email=email)
    except Staff.DoesNotExist:
        return Response({'error': 'Email hoặc mật khẩu không đúng'}, status=status.HTTP_401_UNAUTHORIZED)

    if not check_password(password, staff.password):
        return Response({'error': 'Email hoặc mật khẩu không đúng'}, status=status.HTTP_401_UNAUTHORIZED)

    # Generate a simple token (staff_id + secret)
    token = f"staff_{staff.id}_{staff.email}"

    return Response({
        'staff_id': staff.id,
        'username': staff.username,
        'email': staff.email,
        'role': staff.role,
        'token': token,
    })


@api_view(['GET'])
def staff_detail(request, pk):
    try:
        staff = Staff.objects.get(pk=pk)
        serializer = StaffSerializer(staff)
        return Response(serializer.data)
    except Staff.DoesNotExist:
        return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def verify_token(request):
    """Verify staff token — used by gateway."""
    token = request.headers.get('X-Staff-Token', '')
    if not token or not token.startswith('staff_'):
        return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        parts = token.split('_')
        if len(parts) < 3:
            return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)
        staff_id = int(parts[1])
        staff = Staff.objects.get(pk=staff_id)
        return Response({'valid': True, 'staff_id': staff.id, 'role': staff.role})
    except (Staff.DoesNotExist, ValueError, IndexError):
        return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)
