from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from accounts.models import User, UserProfile
from faker import Faker
import random

fake = Faker()

class Command(BaseCommand):
    help = 'Seeds the database with regular users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--number',
            type=int,
            default=20,
            help='Number of users to create (default: 20)'
        )

    def handle(self, *args, **options):
        num_users = options['number']
        self.stdout.write(f"Creating {num_users} regular users...")

        for i in range(num_users):
            try:
                # Create user
                user = User.objects.create(
                    email=fake.unique.email(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    password=make_password('password123'),  # Default password
                    role=User.Role.USER,
                    is_staff=False,
                    is_superuser=False,
                    is_active=True
                )

                # Create profile
                UserProfile.objects.create(
                    user=user,
                    interests=', '.join(fake.words(nb=random.randint(3, 7))),
                    education_level=random.choice([
                        'High School', 
                        'Associate Degree',
                        'Bachelor\'s Degree',
                        'Master\'s Degree',
                        'Doctorate'
                    ])
                )

                self.stdout.write(self.style.SUCCESS(f"Created user {user.email}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating user: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully created {num_users} users!"))