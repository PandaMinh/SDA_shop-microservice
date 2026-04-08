from django.core.management.base import BaseCommand
from app.models import MobileProduct


class Command(BaseCommand):
    help = 'Seed mobile products data'

    def handle(self, *args, **options):
        if MobileProduct.objects.exists():
            self.stdout.write('Mobile products already seeded.')
            return

        products = [
            {
                'name': 'iPhone 16 Pro',
                'brand': 'Apple',
                'category': 'phone',
                'price': 28990000,
                'stock': 50,
                'description': 'iPhone 16 Pro với chip A18 Pro mạnh mẽ, camera 48MP và màn hình Super Retina XDR.',
                'image_url': 'https://picsum.photos/400/400?random=1',
                'specs': {
                    'screen': '6.3 inch Super Retina XDR',
                    'ram': '8GB',
                    'storage': '256GB',
                    'battery': '3274mAh',
                    'camera': '48MP Triple Camera'
                }
            },
            {
                'name': 'Samsung Galaxy S25 Ultra',
                'brand': 'Samsung',
                'category': 'phone',
                'price': 33990000,
                'stock': 30,
                'description': 'Galaxy S25 Ultra với bút S Pen tích hợp, chip Snapdragon 8 Elite và camera 200MP.',
                'image_url': 'https://picsum.photos/400/400?random=2',
                'specs': {
                    'screen': '6.9 inch Dynamic AMOLED 2X',
                    'ram': '12GB',
                    'storage': '512GB',
                    'battery': '5000mAh',
                    'camera': '200MP Quad Camera'
                }
            },
            {
                'name': 'Xiaomi 15 Ultra',
                'brand': 'Xiaomi',
                'category': 'phone',
                'price': 22990000,
                'stock': 45,
                'description': 'Xiaomi 15 Ultra với camera Leica, sạc nhanh HyperCharge 90W và màn hình LTPO.',
                'image_url': 'https://picsum.photos/400/400?random=3',
                'specs': {
                    'screen': '6.73 inch LTPO AMOLED',
                    'ram': '16GB',
                    'storage': '512GB',
                    'battery': '5500mAh',
                    'camera': '50MP Leica Quad Camera'
                }
            },
            {
                'name': 'Google Pixel 9 Pro',
                'brand': 'Google',
                'category': 'phone',
                'price': 24990000,
                'stock': 20,
                'description': 'Pixel 9 Pro với AI mạnh mẽ từ Google, camera chụp ảnh thiên văn và Google Tensor G4.',
                'image_url': 'https://picsum.photos/400/400?random=4',
                'specs': {
                    'screen': '6.3 inch LTPO OLED',
                    'ram': '16GB',
                    'storage': '256GB',
                    'battery': '4700mAh',
                    'camera': '50MP Triple AI Camera'
                }
            },
            {
                'name': 'OPPO Find X8 Pro',
                'brand': 'OPPO',
                'category': 'phone',
                'price': 19990000,
                'stock': 35,
                'description': 'OPPO Find X8 Pro với camera Hasselblad, sạc nhanh SUPERVOOC 80W.',
                'image_url': 'https://picsum.photos/400/400?random=5',
                'specs': {
                    'screen': '6.78 inch LTPO AMOLED',
                    'ram': '12GB',
                    'storage': '256GB',
                    'battery': '5910mAh',
                    'camera': '50MP Hasselblad Quad'
                }
            },
            {
                'name': 'OnePlus 13',
                'brand': 'OnePlus',
                'category': 'phone',
                'price': 17990000,
                'stock': 40,
                'description': 'OnePlus 13 flagship 2025 với Snapdragon 8 Elite, sạc nhanh 100W SUPERVOOC.',
                'image_url': 'https://picsum.photos/400/400?random=6',
                'specs': {
                    'screen': '6.82 inch LTPO AMOLED',
                    'ram': '12GB',
                    'storage': '256GB',
                    'battery': '6000mAh',
                    'camera': '50MP Hasselblad Triple'
                }
            },
            {
                'name': 'iPad Pro M4 11"',
                'brand': 'Apple',
                'category': 'tablet',
                'price': 25990000,
                'stock': 20,
                'description': 'iPad Pro M4 mỏng nhất từ trước đến nay với chip M4, màn hình OLED Ultra Retina XDR.',
                'image_url': 'https://picsum.photos/400/400?random=7',
                'specs': {
                    'screen': '11 inch Ultra Retina XDR OLED',
                    'ram': '8GB',
                    'storage': '256GB',
                    'battery': '7606mAh',
                    'camera': '12MP Wide + LiDAR'
                }
            },
            {
                'name': 'Samsung Galaxy Tab S10 Ultra',
                'brand': 'Samsung',
                'category': 'tablet',
                'price': 29990000,
                'stock': 15,
                'description': 'Galaxy Tab S10 Ultra với màn hình 14.6 inch Dynamic AMOLED, bút S Pen đi kèm.',
                'image_url': 'https://picsum.photos/400/400?random=8',
                'specs': {
                    'screen': '14.6 inch Dynamic AMOLED 2X',
                    'ram': '12GB',
                    'storage': '256GB',
                    'battery': '11200mAh',
                    'camera': '13MP Dual Camera'
                }
            },
        ]

        for product_data in products:
            MobileProduct.objects.create(**product_data)
            self.stdout.write(f'Created: {product_data["name"]}')

        self.stdout.write(self.style.SUCCESS('Mobile products seeded successfully!'))
