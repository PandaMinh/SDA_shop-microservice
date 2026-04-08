from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import ClothesProduct, InventoryImport
from .serializers import ClothesProductSerializer, InventoryImportSerializer


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'clothes-service ok'})


# ─── Product CRUD ──────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        products = ClothesProduct.objects.filter(is_active=True)
        category = request.query_params.get('category')
        if category:
            products = products.filter(category=category)
        serializer = ClothesProductSerializer(products, many=True)
        return Response(serializer.data)

    # POST — create product (admin)
    serializer = ClothesProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, pk):
    try:
        product = ClothesProduct.objects.get(pk=pk)
    except ClothesProduct.DoesNotExist:
        return Response({'error': 'Không tìm thấy sản phẩm'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ClothesProductSerializer(product)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = ClothesProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE — soft delete
    product.is_active = False
    product.save()
    return Response({'message': 'Đã xóa sản phẩm'})


@api_view(['GET'])
def product_check(request, pk):
    """Used by cart-service to validate product and fetch price/stock."""
    try:
        product = ClothesProduct.objects.get(pk=pk, is_active=True)
        return Response({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'stock': product.stock,
            'image_url': product.image_url,
            'brand': product.brand,
            'category': product.category,
        })
    except ClothesProduct.DoesNotExist:
        return Response({'error': 'Sản phẩm không tồn tại'}, status=status.HTTP_404_NOT_FOUND)


# ─── Nhập Hàng (Inventory Import) ─────────────────────────────────────────────

@api_view(['POST'])
def import_product(request, pk):
    """Admin: Record a stock import, increase product stock."""
    try:
        product = ClothesProduct.objects.get(pk=pk)
    except ClothesProduct.DoesNotExist:
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
        product = ClothesProduct.objects.get(pk=pk)
    except ClothesProduct.DoesNotExist:
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
