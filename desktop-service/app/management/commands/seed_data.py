from django.core.management.base import BaseCommand
from app.models import DesktopProduct


class Command(BaseCommand):
    help = 'Seed desktop products data'

    def handle(self, *args, **options):
        target_per_category = 10
        counts = {
            'laptop': DesktopProduct.objects.filter(category='laptop').count(),
            'pc': DesktopProduct.objects.filter(category='pc').count(),
        }

        products = [
            {
                'name': 'MacBook Pro M4 14"',
                'brand': 'Apple',
                'category': 'laptop',
                'price': 52990000,
                'stock': 20,
                'description': 'MacBook Pro M4 với chip M4 Pro mạnh mẽ, màn hình Liquid Retina XDR và thời lượng pin cả ngày.',
                'image_url': 'https://picsum.photos/400/400?random=11',
                'specs': {
                    'cpu': 'Apple M4 Pro 12-core',
                    'ram': '24GB Unified Memory',
                    'storage': '512GB SSD',
                    'gpu': 'Integrated 20-core GPU',
                    'display': '14.2" Liquid Retina XDR',
                    'battery': '72Wh, up to 18h'
                }
            },
            {
                'name': 'Dell XPS 15',
                'brand': 'Dell',
                'category': 'laptop',
                'price': 38990000,
                'stock': 15,
                'description': 'Dell XPS 15 với màn hình OLED 4K, Intel Core Ultra 9 và thiết kế nhôm cao cấp.',
                'image_url': 'https://picsum.photos/400/400?random=12',
                'specs': {
                    'cpu': 'Intel Core Ultra 9 185H',
                    'ram': '32GB DDR5',
                    'storage': '1TB NVMe SSD',
                    'gpu': 'NVIDIA RTX 4070 8GB',
                    'display': '15.6" OLED 4K Touch',
                    'battery': '86Wh, up to 12h'
                }
            },
            {
                'name': 'ASUS ROG Zephyrus G16',
                'brand': 'ASUS',
                'category': 'laptop',
                'price': 45990000,
                'stock': 10,
                'description': 'ROG Zephyrus G16 gaming laptop với RTX 4080, màn hình OLED 240Hz và thiết kế mỏng nhẹ.',
                'image_url': 'https://picsum.photos/400/400?random=13',
                'specs': {
                    'cpu': 'Intel Core Ultra 9 185H',
                    'ram': '32GB DDR5',
                    'storage': '2TB NVMe SSD',
                    'gpu': 'NVIDIA RTX 4080 12GB',
                    'display': '16" QHD+ OLED 240Hz',
                    'battery': '90Wh, up to 10h'
                }
            },
            {
                'name': 'ThinkPad X1 Carbon Gen 12',
                'brand': 'Lenovo',
                'category': 'laptop',
                'price': 35990000,
                'stock': 25,
                'description': 'ThinkPad X1 Carbon nhẹ nhất dòng doanh nhân với Intel Core Ultra và bảo mật mạnh mẽ.',
                'image_url': 'https://picsum.photos/400/400?random=14',
                'specs': {
                    'cpu': 'Intel Core Ultra 7 165U',
                    'ram': '16GB LPDDR5',
                    'storage': '512GB NVMe SSD',
                    'gpu': 'Intel Iris Xe Graphics',
                    'display': '14" IPS 2.8K OLED',
                    'battery': '57Wh, up to 15h'
                }
            },
            {
                'name': 'HP Spectre x360 14',
                'brand': 'HP',
                'category': 'laptop',
                'price': 32990000,
                'stock': 18,
                'description': 'HP Spectre x360 convertible 2-in-1 với OLED 2.8K, bút stylus và thiết kế xoay 360 độ.',
                'image_url': 'https://picsum.photos/400/400?random=15',
                'specs': {
                    'cpu': 'Intel Core Ultra 7 155H',
                    'ram': '16GB LPDDR5',
                    'storage': '1TB NVMe SSD',
                    'gpu': 'Intel Arc Graphics',
                    'display': '14" OLED 2.8K Touch 120Hz',
                    'battery': '72Wh, up to 17h'
                }
            },
            {
                'name': 'ASUS ROG Strix GT35',
                'brand': 'ASUS',
                'category': 'pc',
                'price': 55990000,
                'stock': 8,
                'description': 'ROG Strix GT35 desktop gaming với RTX 4090, Intel Core i9 và tản nhiệt nước AIO.',
                'image_url': 'https://picsum.photos/400/400?random=16',
                'specs': {
                    'cpu': 'Intel Core i9-14900KF',
                    'ram': '64GB DDR5 6000MHz',
                    'storage': '2TB NVMe SSD + 4TB HDD',
                    'gpu': 'NVIDIA RTX 4090 24GB',
                    'display': 'Not included',
                    'battery': 'N/A (Desktop)'
                }
            },
            {
                'name': 'Mac Mini M4',
                'brand': 'Apple',
                'category': 'pc',
                'price': 18990000,
                'stock': 30,
                'description': 'Mac Mini M4 nhỏ gọn nhất từ trước đến nay với chip M4, hỗ trợ 3 màn hình và Thunderbolt 4.',
                'image_url': 'https://picsum.photos/400/400?random=17',
                'specs': {
                    'cpu': 'Apple M4 10-core',
                    'ram': '16GB Unified Memory',
                    'storage': '256GB SSD',
                    'gpu': 'Integrated 10-core GPU',
                    'display': 'Not included',
                    'battery': 'N/A (Desktop)'
                }
            },
        ]

        to_create = []
        for category in ['laptop', 'pc']:
            count = counts[category]
            if count >= target_per_category:
                continue

            base = [p for p in products if p['category'] == category]
            for p in base:
                if count >= target_per_category:
                    break
                to_create.append(p)
                count += 1

            for i in range(target_per_category - count):
                idx = count + i + 1
                to_create.append({
                    'name': f'{category.title()} Sample {idx}',
                    'brand': 'TechStore',
                    'category': category,
                    'price': 15990000 + (idx * 250000),
                    'stock': 12 + (idx % 8),
                    'description': 'Sản phẩm mẫu bổ sung để đủ 10 sản phẩm cho từng loại.',
                    'image_url': f'https://picsum.photos/400/400?random=80{category[:1]}{idx}',
                    'specs': {
                        'cpu': 'Intel Core Ultra 5',
                        'ram': '16GB',
                        'storage': '512GB SSD',
                        'gpu': 'Integrated',
                        'display': '15.6"',
                        'battery': 'N/A',
                    }
                })

        for product_data in to_create:
            DesktopProduct.objects.create(**product_data)
            self.stdout.write(f'Created: {product_data["name"]}')

        self.stdout.write(self.style.SUCCESS(f'Seeded {len(to_create)} desktop products.'))
