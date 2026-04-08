from django.core.management.base import BaseCommand
from app.models import ClothesProduct


class Command(BaseCommand):
    help = 'Seed clothes products sample data'

    def handle(self, *args, **options):
        if ClothesProduct.objects.exists():
            self.stdout.write('Clothes data already seeded.')
            return

        products = [
            {
                'name': 'Áo Polo Nam Basic',
                'brand': 'Uniqlo',
                'category': 'ao',
                'price': 399000,
                'stock': 50,
                'description': 'Áo polo nam chất liệu cotton cao cấp, thoáng mát.',
                'image_url': 'https://picsum.photos/400/400?random=201',
                'specs': {'material': 'Cotton 100%', 'sizes': 'S,M,L,XL', 'colors': 'Trắng, Đen, Navy'},
            },
            {
                'name': 'Áo Thun Nữ Oversize',
                'brand': 'H&M',
                'category': 'ao',
                'price': 199000,
                'stock': 80,
                'description': 'Áo thun form oversize hiện đại, năng động.',
                'image_url': 'https://picsum.photos/400/400?random=202',
                'specs': {'material': 'Cotton 95% Spandex 5%', 'sizes': 'S,M,L', 'colors': 'Trắng, Hồng, Xám'},
            },
            {
                'name': 'Quần Jeans Nam Slim Fit',
                'brand': 'Levi\'s',
                'category': 'quan',
                'price': 1290000,
                'stock': 30,
                'description': 'Quần jeans nam form slim fit, co giãn nhẹ.',
                'image_url': 'https://picsum.photos/400/400?random=203',
                'specs': {'material': 'Denim 98% Cotton 2% Elastane', 'sizes': '28,29,30,31,32,33', 'colors': 'Xanh đậm, Đen'},
            },
            {
                'name': 'Quần Âu Nữ Ống Rộng',
                'brand': 'Zara',
                'category': 'quan',
                'price': 790000,
                'stock': 25,
                'description': 'Quần âu nữ form ống rộng thanh lịch, phù hợp công sở.',
                'image_url': 'https://picsum.photos/400/400?random=204',
                'specs': {'material': 'Polyester', 'sizes': 'XS,S,M,L', 'colors': 'Đen, Beige'},
            },
            {
                'name': 'Đầm Maxi Chiffon Hoa',
                'brand': 'Mango',
                'category': 'dam',
                'price': 990000,
                'stock': 20,
                'description': 'Đầm maxi vải chiffon họa tiết hoa nhẹ nhàng, phù hợp du lịch.',
                'image_url': 'https://picsum.photos/400/400?random=205',
                'specs': {'material': 'Chiffon', 'sizes': 'XS,S,M,L', 'colors': 'Trắng hoa, Xanh hoa'},
            },
            {
                'name': 'Áo Khoác Bomber Basic',
                'brand': 'Adidas',
                'category': 'ao_khoac',
                'price': 1590000,
                'stock': 15,
                'description': 'Áo khoác bomber unisex kiểu dáng trẻ trung.',
                'image_url': 'https://picsum.photos/400/400?random=206',
                'specs': {'material': 'Polyester', 'sizes': 'S,M,L,XL,XXL', 'colors': 'Đen, Xanh Navy'},
            },
            {
                'name': 'Áo Khoác Denim Nam',
                'brand': 'Calvin Klein',
                'category': 'ao_khoac',
                'price': 2190000,
                'stock': 10,
                'description': 'Áo khoác denim nam phong cách Americana.',
                'image_url': 'https://picsum.photos/400/400?random=207',
                'specs': {'material': 'Denim', 'sizes': 'S,M,L,XL', 'colors': 'Xanh nhạt, Xanh đậm'},
            },
            {
                'name': 'Mũ Bucket Hat Canvas',
                'brand': 'Nike',
                'category': 'phu_kien',
                'price': 350000,
                'stock': 40,
                'description': 'Mũ bucket hat vải canvas bền chắc.',
                'image_url': 'https://picsum.photos/400/400?random=208',
                'specs': {'material': 'Canvas', 'sizes': 'Free size', 'colors': 'Đen, Trắng, Be'},
            },
        ]

        for p in products:
            ClothesProduct.objects.create(**p)
            self.stdout.write(f'  ✓ {p["name"]}')

        self.stdout.write(self.style.SUCCESS(f'Seeded {len(products)} clothes products.'))
