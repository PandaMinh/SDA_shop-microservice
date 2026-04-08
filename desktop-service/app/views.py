from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import DesktopProduct, InventoryImport
from .serializers import DesktopProductSerializer, InventoryImportSerializer


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'ok', 'service': 'desktop-service'})


@api_view(['GET', 'POST'])
def desktop_product_list(request):
    if request.method == 'GET':
        category = request.query_params.get('category', None)
        products = DesktopProduct.objects.filter(is_active=True)
        if category:
            products = products.filter(category=category)
        serializer = DesktopProductSerializer(products, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = DesktopProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def desktop_product_detail(request, pk):
    try:
        product = DesktopProduct.objects.get(pk=pk)
    except DesktopProduct.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DesktopProductSerializer(product)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = DesktopProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        product.is_active = False
        product.save()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def check_product(request, pk):
    """Check if a product exists — used by customer-service."""
    try:
        product = DesktopProduct.objects.get(pk=pk, is_active=True)
        return Response({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'stock': product.stock,
            'image_url': product.image_url,
        })
    except DesktopProduct.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


# ─── Nhập Hàng (Inventory Import) ─────────────────────────────────────────────

@api_view(['POST'])
def import_product(request, pk):
    """Admin: Record a stock import, increase product stock."""
    try:
        product = DesktopProduct.objects.get(pk=pk)
    except DesktopProduct.DoesNotExist:
        return Response({'error': 'Không tìm thấy sản phẩm'}, status=status.HTTP_404_NOT_FOUND)

    quantity = request.data.get('quantity_imported')
    cost_price = request.data.get('cost_price', 0)
    supplier = request.data.get('supplier', '')
    note = request.data.get('note', '')
    imported_by = request.data.get('imported_by', 'admin')

    if not quantity or int(quantity) <= 0:
        return Response({'error': 'Số lượng nhập phải lớn hơn 0'}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        imp = InventoryImport.objects.create(
            product=product,
            quantity_imported=int(quantity),
            cost_price=cost_price,
            supplier=supplier,
            note=note,
            imported_by=imported_by,
        )
        product.stock += int(quantity)
        product.save()

    return Response({
        'message': f'Nhập thành công {quantity} sản phẩm "{product.name}"',
        'product_id': product.id,
        'new_stock': product.stock,
        'import_id': imp.id,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def import_history(request, pk):
    """Admin: Get import history for a product."""
    try:
        product = DesktopProduct.objects.get(pk=pk)
    except DesktopProduct.DoesNotExist:
        return Response({'error': 'Không tìm thấy sản phẩm'}, status=status.HTTP_404_NOT_FOUND)

    imports = InventoryImport.objects.filter(product=product)
    serializer = InventoryImportSerializer(imports, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def all_imports(request):
    """Admin: Get all inventory imports."""
    imports = InventoryImport.objects.select_related('product').all()
    serializer = InventoryImportSerializer(imports, many=True)
    return Response(serializer.data)

