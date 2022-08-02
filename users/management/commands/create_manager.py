from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Profile


class Command(BaseCommand):
    help = 'Creates "manager" user with owner role'

    def handle(self, *args, **kwargs):
        u = User.objects.filter(username='manager').first()
        if u:
            print("User already exists!")
        else:
            u = User.objects.create_user(username='manager', password='supreme_manager#2022') # Put password in .env
            Profile.objects.create(user=u, role=Profile.Role.OWNER, is_approved=True)
            print("User successfully created.")
