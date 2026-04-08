import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from .models import Customer, Order, OrderItem
from .serializers import CustomerSerializer, OrderSerializer, OrderItemSerializer

MOBILE_SERVICE = getattr(settings, 'MOBILE_SERVICE_URL', 'http://mobile-service:8000')
DESKTOP_SERVICE = getattr(settings, 'DESKTOP_SERVICE_URL', 'http://desktop-service:8000')


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'ok', 'service': 'customer-service'})


# ─── Customer Auth ───────────────────────────────────────────────────────────

@api_view(['POST'])
def register(request):
    name = request.data.get('name')
    email = request.data.get('email')
    password = request.data.get('password')
    phone = request.data.get('phone', '')
    address = request.data.get('address', '')

    if not name or not email or not password:
        return Response({'error': 'Tên, email và mật khẩu là bắt buộc'}, status=status.HTTP_400_BAD_REQUEST)

    if Customer.objects.filter(email=email).exists():
        return Response({'error': 'Email đã được sử dụng'}, status=status.HTTP_400_BAD_REQUEST)

    customer = Customer.objects.create(
        name=name,
        email=email,
        password=make_password(password),
        phone=phone,
        address=address,
    )

    return Response({
        'customer_id': customer.id,
        'name': customer.name,
        'email': customer.email,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Email và mật khẩu là bắt buộc'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        customer = Customer.objects.get(email=email)
    except Customer.DoesNotExist:
        return Response({'error': 'Email hoặc mật khẩu không đúng'}, status=status.HTTP_401_UNAUTHORIZED)

    if not check_password(password, customer.password):
        return Response({'error': 'Email hoặc mật khẩu không đúng'}, status=status.HTTP_401_UNAUTHORIZED)

    return Response({
        'customer_id': customer.id,
        'name': customer.name,
        'email': customer.email,
        'phone': customer.phone,
        'address': customer.address,
    })


@api_view(['GET'])
def customer_detail(request, pk):
    try:
        customer = Customer.objects.get(pk=pk)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)



# ─── Orders ──────────────────────────────────────────────────────────────────

@api_view(['POST'])
def create_order(request):
    customer_id = request.data.get('customer_id')
    shipping_address = request.data.get('shipping_address')
    payment_method = request.data.get('payment_method', 'cod')
    customer_name = request.data.get('customer_name', '')
    customer_email = request.data.get('customer_email', '')

    if not customer_id or not shipping_address:
        return Response({'error': 'customer_id và địa chỉ giao hàng là bắt buộc'}, status=status.HTTP_400_BAD_REQUEST)

    items_data = request.data.get('items', [])
    if not items_data:
        return Response({'error': 'Danh sách sản phẩm trống'}, status=status.HTTP_400_BAD_REQUEST)

    # Calculate total
    total_amount = sum(float(item.get('price', 0)) * int(item.get('quantity', 1)) for item in items_data)

    order = Order.objects.create(
        customer_id=customer_id,
        total_amount=total_amount,
        shipping_address=shipping_address,
        payment_method=payment_method,
        customer_name=customer_name,
        customer_email=customer_email,
        status='pending',
    )

    for item in items_data:
        OrderItem.objects.create(
            order=order,
            product_id=item.get('product_id'),
            product_type=item.get('product_type'),
            product_name=item.get('product_name', f'Product #{item.get("product_id")}'),
            quantity=item.get('quantity', 1),
            price=item.get('price', 0),
        )

    return Response({
        'order_id': order.id,
        'status': order.status,
        'total_amount': str(order.total_amount),
        'message': f'Đặt hàng thành công! Mã đơn hàng: #{order.id}',
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def customer_orders(request):
    customer_id = request.query_params.get('customer_id')
    if not customer_id:
        return Response({'error': 'customer_id là bắt buộc'}, status=status.HTTP_400_BAD_REQUEST)
    orders = Order.objects.filter(customer_id=customer_id).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def all_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
def update_order_status(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    valid_statuses = ['pending', 'confirmed', 'shipping', 'delivered', 'cancelled']
    if new_status not in valid_statuses:
        return Response({'error': f'Trạng thái không hợp lệ. Chọn một trong: {valid_statuses}'}, status=status.HTTP_400_BAD_REQUEST)

    order.status = new_status
    order.save()
    serializer = OrderSerializer(order)
    return Response(serializer.data)


@api_view(['GET'])
def order_detail(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
