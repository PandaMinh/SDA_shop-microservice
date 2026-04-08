import requests
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

CUSTOMER_SERVICE = settings.CUSTOMER_SERVICE
STAFF_SERVICE = settings.STAFF_SERVICE
MOBILE_SERVICE = settings.MOBILE_SERVICE
DESKTOP_SERVICE = settings.DESKTOP_SERVICE
CART_SERVICE = getattr(settings, 'CART_SERVICE', 'http://cart-service:8000')
CLOTHES_SERVICE = getattr(settings, 'CLOTHES_SERVICE', 'http://clothes-service:8000')
AI_SERVICE = getattr(settings, 'AI_SERVICE', 'http://ai-service:8000')

REQUEST_TIMEOUT = 10


def _get_customer_id(request):
    return request.headers.get('X-Customer-Id') or request.data.get('customer_id') or request.GET.get('customer_id')


def _get_staff_token(request):
    return request.headers.get('X-Staff-Token', '')


def _is_staff(token):
    """Verify staff token with staff-service."""
    if not token:
        return False, None
    try:
        r = requests.get(
            f"{STAFF_SERVICE}/staff/verify/",
            headers={'X-Staff-Token': token},
            timeout=REQUEST_TIMEOUT
        )
        if r.status_code == 200:
            data = r.json()
            return data.get('valid', False), data
        return False, None
    except requests.RequestException:
        return False, None


# ─── Health ───────────────────────────────────────────────────────────────────

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'ok', 'service': 'api-gateway'})


# ─── Auth ─────────────────────────────────────────────────────────────────────

@api_view(['POST'])
def customer_register(request):
    try:
        r = requests.post(
            f"{CUSTOMER_SERVICE}/customers/register/",
            json=request.data,
            timeout=REQUEST_TIMEOUT
        )
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['POST'])
def customer_login(request):
    try:
        r = requests.post(
            f"{CUSTOMER_SERVICE}/customers/login/",
            json=request.data,
            timeout=REQUEST_TIMEOUT
        )
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['POST'])
def staff_login(request):
    try:
        r = requests.post(
            f"{STAFF_SERVICE}/staff/login/",
            json=request.data,
            timeout=REQUEST_TIMEOUT
        )
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# ─── Products ─────────────────────────────────────────────────────────────────

@api_view(['GET'])
def get_all_products(request):
    """Aggregate products from mobile, desktop, and clothes services."""
    all_products = []

    def fetch_products(service_url, service_type):
        try:
            params = {}
            category = request.GET.get('category')
            if category:
                params['category'] = category
            r = requests.get(f"{service_url}/{service_type}-products/", params=params, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                for p in r.json():
                    p['type'] = service_type
                    all_products.append(p)
        except requests.RequestException:
            pass

    product_type = request.GET.get('type')

    if product_type == 'mobile' or not product_type:
        fetch_products(MOBILE_SERVICE, 'mobile')
    if product_type == 'desktop' or not product_type:
        fetch_products(DESKTOP_SERVICE, 'desktop')
    if product_type == 'clothes' or not product_type:
        fetch_products(CLOTHES_SERVICE, 'clothes')

    return Response({'products': all_products})


@api_view(['GET', 'POST'])
def mobile_products(request):
    try:
        if request.method == 'GET':
            r = requests.get(f"{MOBILE_SERVICE}/mobile-products/", params=request.GET, timeout=REQUEST_TIMEOUT)
        else:
            # POST requires staff auth
            token = _get_staff_token(request)
            valid, _ = _is_staff(token)
            if not valid:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
            r = requests.post(f"{MOBILE_SERVICE}/mobile-products/", json=request.data, timeout=REQUEST_TIMEOUT)
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET', 'PUT', 'DELETE'])
def mobile_product_detail(request, pk):
    try:
        if request.method == 'GET':
            r = requests.get(f"{MOBILE_SERVICE}/mobile-products/{pk}/", timeout=REQUEST_TIMEOUT)
        elif request.method == 'PUT':
            token = _get_staff_token(request)
            valid, _ = _is_staff(token)
            if not valid:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
            r = requests.put(f"{MOBILE_SERVICE}/mobile-products/{pk}/", json=request.data, timeout=REQUEST_TIMEOUT)
        else:
            token = _get_staff_token(request)
            valid, _ = _is_staff(token)
            if not valid:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
            r = requests.delete(f"{MOBILE_SERVICE}/mobile-products/{pk}/", timeout=REQUEST_TIMEOUT)
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET', 'POST'])
def desktop_products(request):
    try:
        if request.method == 'GET':
            r = requests.get(f"{DESKTOP_SERVICE}/desktop-products/", params=request.GET, timeout=REQUEST_TIMEOUT)
        else:
            token = _get_staff_token(request)
            valid, _ = _is_staff(token)
            if not valid:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
            r = requests.post(f"{DESKTOP_SERVICE}/desktop-products/", json=request.data, timeout=REQUEST_TIMEOUT)
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET', 'PUT', 'DELETE'])
def desktop_product_detail(request, pk):
    try:
        if request.method == 'GET':
            r = requests.get(f"{DESKTOP_SERVICE}/desktop-products/{pk}/", timeout=REQUEST_TIMEOUT)
        elif request.method == 'PUT':
            token = _get_staff_token(request)
            valid, _ = _is_staff(token)
            if not valid:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
            r = requests.put(f"{DESKTOP_SERVICE}/desktop-products/{pk}/", json=request.data, timeout=REQUEST_TIMEOUT)
        else:
            token = _get_staff_token(request)
            valid, _ = _is_staff(token)
            if not valid:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
            r = requests.delete(f"{DESKTOP_SERVICE}/desktop-products/{pk}/", timeout=REQUEST_TIMEOUT)
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET', 'POST'])
def clothes_products(request):
    try:
        if request.method == 'GET':
            r = requests.get(f"{CLOTHES_SERVICE}/clothes-products/", params=request.GET, timeout=REQUEST_TIMEOUT)
        else:
            token = _get_staff_token(request)
            valid, _ = _is_staff(token)
            if not valid:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
            r = requests.post(f"{CLOTHES_SERVICE}/clothes-products/", json=request.data, timeout=REQUEST_TIMEOUT)
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET', 'PUT', 'DELETE'])
def clothes_product_detail(request, pk):
    try:
        if request.method == 'GET':
            r = requests.get(f"{CLOTHES_SERVICE}/clothes-products/{pk}/", timeout=REQUEST_TIMEOUT)
        elif request.method == 'PUT':
            token = _get_staff_token(request)
            valid, _ = _is_staff(token)
            if not valid:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
            r = requests.put(f"{CLOTHES_SERVICE}/clothes-products/{pk}/", json=request.data, timeout=REQUEST_TIMEOUT)
        else:
            token = _get_staff_token(request)
            valid, _ = _is_staff(token)
            if not valid:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
            r = requests.delete(f"{CLOTHES_SERVICE}/clothes-products/{pk}/", timeout=REQUEST_TIMEOUT)
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# ─── Nhập Hàng (Inventory Import) ─────────────────────────────────────────────

def _get_product_service(product_type):
    if product_type == 'mobile': return MOBILE_SERVICE
    if product_type == 'desktop': return DESKTOP_SERVICE
    if product_type == 'clothes': return CLOTHES_SERVICE
    return None

@api_view(['POST'])
def import_product(request, product_type, pk):
    token = _get_staff_token(request)
    valid, _ = _is_staff(token)
    if not valid:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
    svc = _get_product_service(product_type)
    if not svc:
        return Response({'error': 'Invalid product type'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        r = requests.post(
            f"{svc}/{product_type}-products/{pk}/import/",
            json=request.data,
            timeout=REQUEST_TIMEOUT
        )
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

@api_view(['GET'])
def import_history(request, product_type, pk):
    token = _get_staff_token(request)
    valid, _ = _is_staff(token)
    if not valid:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    svc = _get_product_service(product_type)
    if not svc:
        return Response({'error': 'Invalid product type'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        r = requests.get(f"{svc}/{product_type}-products/{pk}/imports/", timeout=REQUEST_TIMEOUT)
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

@api_view(['GET'])
def all_imports(request):
    token = _get_staff_token(request)
    valid, _ = _is_staff(token)
    if not valid:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    # Fetch from all 3 services and combine
    all_imp = []
    for svc, ptype in [(MOBILE_SERVICE, 'mobile'), (DESKTOP_SERVICE, 'desktop'), (CLOTHES_SERVICE, 'clothes')]:
        try:
            r = requests.get(f"{svc}/{ptype}-products/imports/all/", timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                for i in r.json():
                    i['product_type'] = ptype
                    all_imp.append(i)
        except requests.RequestException:
            pass

    return Response(sorted(all_imp, key=lambda x: x.get('created_at', ''), reverse=True))


# ─── Cart ─────────────────────────────────────────────────────────────────────

@api_view(['GET'])
def get_cart(request):
    customer_id = _get_customer_id(request)
    if not customer_id:
        return Response({'error': 'Vui lòng đăng nhập'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        r = requests.get(f"{CART_SERVICE}/carts/{customer_id}/", timeout=REQUEST_TIMEOUT)
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['POST'])
def add_cart_item(request):
    customer_id = _get_customer_id(request)
    if not customer_id:
        return Response({'error': 'Vui lòng đăng nhập'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        payload = {**request.data, 'customer_id': customer_id}
        r = requests.post(f"{CART_SERVICE}/cart-items/", json=payload, timeout=REQUEST_TIMEOUT)
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['PUT'])
def update_cart_item(request, item_id):
    try:
        r = requests.put(
            f"{CART_SERVICE}/cart-items/{item_id}/",
            json=request.data,
            timeout=REQUEST_TIMEOUT
        )
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['DELETE'])
def remove_cart_item(request, item_id):
    try:
        r = requests.delete(f"{CART_SERVICE}/cart-items/{item_id}/delete/", timeout=REQUEST_TIMEOUT)
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['DELETE'])
def clear_cart(request):
    customer_id = _get_customer_id(request)
    if not customer_id:
        return Response({'error': 'Vui lòng đăng nhập'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        r = requests.delete(f"{CART_SERVICE}/carts/{customer_id}/clear/", timeout=REQUEST_TIMEOUT)
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# ─── Orders ───────────────────────────────────────────────────────────────────

@api_view(['POST'])
def checkout(request):
    customer_id = _get_customer_id(request)
    if not customer_id:
        return Response({'error': 'Vui lòng đăng nhập'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        payload = {
            **request.data,
            'customer_id': customer_id,
        }
        r = requests.post(f"{CUSTOMER_SERVICE}/orders/", json=payload, timeout=REQUEST_TIMEOUT)
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
def customer_orders(request):
    customer_id = _get_customer_id(request)
    if not customer_id:
        return Response({'error': 'Vui lòng đăng nhập'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        r = requests.get(
            f"{CUSTOMER_SERVICE}/orders/customer/",
            params={'customer_id': customer_id},
            timeout=REQUEST_TIMEOUT
        )
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
def admin_orders(request):
    token = _get_staff_token(request)
    valid, _ = _is_staff(token)
    if not valid:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        r = requests.get(f"{CUSTOMER_SERVICE}/orders/all/", timeout=REQUEST_TIMEOUT)
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['PUT'])
def update_order_status(request, order_id):
    token = _get_staff_token(request)
    valid, _ = _is_staff(token)
    if not valid:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        r = requests.put(
            f"{CUSTOMER_SERVICE}/orders/{order_id}/status/",
            json=request.data,
            timeout=REQUEST_TIMEOUT
        )
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# ─── AI ──────────────────────────────────────────────────────────────────────

@api_view(['POST'])
def ai_chat(request):
    try:
        r = requests.post(f"{AI_SERVICE}/chat/", json=request.data, timeout=REQUEST_TIMEOUT)
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['POST'])
def ai_track_event(request):
    try:
        r = requests.post(f"{AI_SERVICE}/events/", json=request.data, timeout=REQUEST_TIMEOUT)
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
def ai_recommendations(request):
    try:
        customer_id = request.GET.get('customer_id')
        r = requests.get(
            f"{AI_SERVICE}/recommendations/",
            params={'customer_id': customer_id},
            timeout=REQUEST_TIMEOUT,
        )
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
