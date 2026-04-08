import requests as http
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

REQUEST_TIMEOUT = 10


def _get_or_create_cart(customer_id):
    cart, _ = Cart.objects.get_or_create(customer_id=customer_id)
    return cart


def _fetch_product_info(product_id, product_type):
    """Validate and fetch product info from the appropriate service."""
    urls = {
        'mobile': f"{settings.MOBILE_SERVICE_URL}/mobile-products/check/{product_id}/",
        'desktop': f"{settings.DESKTOP_SERVICE_URL}/desktop-products/check/{product_id}/",
        'clothes': f"{settings.CLOTHES_SERVICE_URL}/clothes-products/check/{product_id}/",
    }
    url = urls.get(product_type)
    if not url:
        return None, 'Loại sản phẩm không hợp lệ'
    try:
        r = http.get(url, timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            return r.json(), None
        return None, 'Sản phẩm không tồn tại'
    except Exception as e:
        return None, f'Lỗi kết nối service: {str(e)}'


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'cart-service ok'})


@api_view(['GET'])
def get_cart(request, customer_id):
    cart = _get_or_create_cart(customer_id)
    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(['POST'])
def add_cart_item(request):
    customer_id = request.data.get('customer_id')
    product_id = request.data.get('product_id')
    product_type = request.data.get('product_type')
    quantity = int(request.data.get('quantity', 1))

    if not all([customer_id, product_id, product_type]):
        return Response({'error': 'Thiếu thông tin'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate product from corresponding service
    product_info, error = _fetch_product_info(product_id, product_type)
    if error:
        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

    if product_info.get('stock', 0) < quantity:
        return Response({'error': 'Sản phẩm không đủ số lượng'}, status=status.HTTP_400_BAD_REQUEST)

    cart = _get_or_create_cart(customer_id)

    # Check if item already exists → update quantity
    try:
        item = CartItem.objects.get(cart=cart, product_id=product_id, product_type=product_type)
        item.quantity += quantity
        item.product_name = product_info.get('name', '')
        item.price = product_info.get('price', item.price)
        item.image_url = product_info.get('image_url', '')
        item.save()
    except CartItem.DoesNotExist:
        item = CartItem.objects.create(
            cart=cart,
            product_id=product_id,
            product_type=product_type,
            product_name=product_info.get('name', ''),
            price=product_info.get('price', 0),
            quantity=quantity,
            image_url=product_info.get('image_url', ''),
        )

    serializer = CartItemSerializer(item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def update_cart_item(request, item_id):
    try:
        item = CartItem.objects.get(pk=item_id)
    except CartItem.DoesNotExist:
        return Response({'error': 'Không tìm thấy item'}, status=status.HTTP_404_NOT_FOUND)

    quantity = int(request.data.get('quantity', 1))
    if quantity <= 0:
        item.delete()
        return Response({'message': 'Item đã được xóa'})

    item.quantity = quantity
    item.save()
    return Response(CartItemSerializer(item).data)


@api_view(['DELETE'])
def remove_cart_item(request, item_id):
    try:
        item = CartItem.objects.get(pk=item_id)
        item.delete()
        return Response({'message': 'Đã xóa sản phẩm khỏi giỏ hàng'})
    except CartItem.DoesNotExist:
        return Response({'error': 'Không tìm thấy item'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def clear_cart(request, customer_id):
    try:
        cart = Cart.objects.get(customer_id=customer_id)
        cart.items.all().delete()
        return Response({'message': 'Đã xóa tất cả sản phẩm trong giỏ hàng'})
    except Cart.DoesNotExist:
        return Response({'message': 'Giỏ hàng đã trống'})
