#!/usr/bin/env python
"""
Quick script to verify backend is working and create a test task
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from tasks.models import Task
from datetime import datetime, timedelta

User = get_user_model()


user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'test@example.com'
    }
)

if created:
    user.set_password('testpass123')
    user.save()
    print(f"✓ Created test user: testuser / testpass123")
else:
    print(f"✓ Test user exists: testuser")


existing_tasks = Task.objects.filter(user=user).count()
print(f"✓ Existing tasks for testuser: {existing_tasks}")


if existing_tasks == 0:
    task = Task.objects.create(
        user=user,
        title="Create the timetable!",
        description="create the timetable for the next week and make sure to include all the important tasks and deadlines. This will help you stay organized and manage your time effectively.",
        status="pending",
        due_date=datetime.now() + timedelta(days=7)
    )
    print(f"✓ Created sample task: {task.title}")
    
    
    Task.objects.create(
        user=user,
        title="Test the AI Breakdown feature",
        description="Click the sparkles icon to generate AI-powered subtasks",
        status="pending",
        due_date=datetime.now() + timedelta(days=3)
    )
    
    Task.objects.create(
        user=user,
        title="Explore inline status updates",
        description="Change task status directly from the task list",
        status="in_progress",
        due_date=datetime.now() + timedelta(days=5)
    )
    
    print(f"✓ Created 3 sample tasks total")
else:
    print("✓ Tasks already exist, skipping sample task creation")

print("\n" + "="*50)
print("LOGIN CREDENTIALS:")
print("="*50)
print("Username: testuser")
print("Password: testpass123")
print("="*50)
print("\nGo to: http://localhost:5173/login")
print("Then navigate to: http://localhost:5173/tasks")
