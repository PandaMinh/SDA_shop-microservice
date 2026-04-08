from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from app.models import Staff


class Command(BaseCommand):
    help = 'Seed staff/admin data'

    def handle(self, *args, **options):
        if Staff.objects.exists():
            self.stdout.write('Staff already seeded.')
            return

        Staff.objects.create(
            username='admin',
            email='admin@techstore.com',
            password=make_password('Admin@123456'),
            role='admin'
        )
        self.stdout.write('Created admin: admin@techstore.com / Admin@123456')

        Staff.objects.create(
            username='staff01',
            email='staff01@techstore.com',
            password=make_password('Staff@123456'),
            role='staff'
        )
        self.stdout.write('Created staff01: staff01@techstore.com / Staff@123456')

        self.stdout.write(self.style.SUCCESS('Staff seeded successfully!'))
