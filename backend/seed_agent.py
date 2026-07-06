import os
import django
import sys

sys.path.append('/workspaces/BimaGrid/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.models import Profile

User = get_user_model()

def seed_agent():
    agent_id = "AGN-G26A001"
    email = "agent@bimagrid.com"
    password = "password123"
    
    user, created = User.objects.get_or_create(username=agent_id, defaults={'email': email})
    if created:
        user.set_password(password)
        user.save()
        print(f"Created user {agent_id}")
    else:
        user.email = email
        user.set_password(password)
        user.save()
        print(f"User {agent_id} already exists, updated email and password")
        
    profile, p_created = Profile.objects.get_or_create(user=user)
    profile.role = Profile.Role.BROKER
    profile.full_name = "Test Agent"
    profile.save()
    
    print(f"Seeded Agent successfully! ID: {agent_id}, Password: {password}")

if __name__ == '__main__':
    seed_agent()
