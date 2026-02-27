from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Task
from datetime import datetime, timedelta


class UnauthorizedAccessTests(APITestCase):
    """Test unauthorized access to task endpoints"""
    
    def setUp(self):
       
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.task = Task.objects.create(
            user=self.user,
            title='Test Task',
            description='Test Description',
            status='pending'
        )
    
    def test_list_tasks_without_authentication(self):
        """Test that listing tasks requires authentication"""
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_retrieve_task_without_authentication(self):
        """Test that retrieving a task requires authentication"""
        response = self.client.get(f'/api/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_task_without_authentication(self):
        """Test that creating a task requires authentication"""
        data = {
            'title': 'New Task',
            'description': 'New Description',
            'status': 'pending'
        }
        response = self.client.post('/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_task_without_authentication(self):
        """Test that updating a task requires authentication"""
        data = {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'status': 'in_progress'
        }
        response = self.client.put(f'/api/tasks/{self.task.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_partial_update_task_without_authentication(self):
        """Test that partially updating a task requires authentication"""
        data = {'status': 'completed'}
        response = self.client.patch(f'/api/tasks/{self.task.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_delete_task_without_authentication(self):
        """Test that deleting a task requires authentication"""
        response = self.client.delete(f'/api/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DataIsolationTests(APITestCase):
    """Test data isolation between different users"""
    
    def setUp(self):
       
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass123'
        )
        
       
        self.user1_task1 = Task.objects.create(
            user=self.user1,
            title='User1 Task 1',
            description='Description 1',
            status='pending'
        )
        self.user1_task2 = Task.objects.create(
            user=self.user1,
            title='User1 Task 2',
            description='Description 2',
            status='in_progress'
        )
        
      
        self.user2_task1 = Task.objects.create(
            user=self.user2,
            title='User2 Task 1',
            description='Description 1',
            status='pending'
        )
        self.user2_task2 = Task.objects.create(
            user=self.user2,
            title='User2 Task 2',
            description='Description 2',
            status='completed'
        )
    
    def test_user_can_only_see_own_tasks(self):
        """Test that users can only see their own tasks"""
        
        self.client.force_authenticate(user=self.user1)
        
        
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
       
        task_ids = [task['id'] for task in response.data['results']]
        self.assertIn(self.user1_task1.id, task_ids)
        self.assertIn(self.user1_task2.id, task_ids)
        self.assertNotIn(self.user2_task1.id, task_ids)
        self.assertNotIn(self.user2_task2.id, task_ids)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_user_cannot_retrieve_other_users_task(self):
        """Test that users cannot retrieve another user's task"""
        
        self.client.force_authenticate(user=self.user1)
        
        
        response = self.client.get(f'/api/tasks/{self.user2_task1.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_user_cannot_update_other_users_task(self):
        """Test that users cannot update another user's task"""
        
        self.client.force_authenticate(user=self.user1)
        
       
        data = {
            'title': 'Hacked Task',
            'description': 'Hacked Description',
            'status': 'completed'
        }
        response = self.client.put(f'/api/tasks/{self.user2_task1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
       
        self.user2_task1.refresh_from_db()
        self.assertEqual(self.user2_task1.title, 'User2 Task 1')
    
    def test_user_cannot_partial_update_other_users_task(self):
        """Test that users cannot partially update another user's task"""
        
        self.client.force_authenticate(user=self.user1)
        
       
        data = {'status': 'cancelled'}
        response = self.client.patch(f'/api/tasks/{self.user2_task1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
       
        self.user2_task1.refresh_from_db()
        self.assertEqual(self.user2_task1.status, 'pending')
    
    def test_user_cannot_delete_other_users_task(self):
        """Test that users cannot delete another user's task"""
        
        self.client.force_authenticate(user=self.user1)
        
        
        response = self.client.delete(f'/api/tasks/{self.user2_task1.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
       
        self.assertTrue(Task.objects.filter(id=self.user2_task1.id).exists())
    
    def test_created_task_belongs_to_authenticated_user(self):
        """Test that newly created tasks are assigned to the authenticated user"""
        
        self.client.force_authenticate(user=self.user1)
        
      
        data = {
            'title': 'New Task for User1',
            'description': 'New Description',
            'status': 'pending'
        }
        response = self.client.post('/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
       
        task_id = response.data['id']
        task = Task.objects.get(id=task_id)
        self.assertEqual(task.user, self.user1)
        
        
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'/api/tasks/{task_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_user_can_update_own_task(self):
        """Test that users can update their own tasks"""
       
        self.client.force_authenticate(user=self.user1)
        
       
        data = {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'status': 'completed'
        }
        response = self.client.put(f'/api/tasks/{self.user1_task1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
        self.user1_task1.refresh_from_db()
        self.assertEqual(self.user1_task1.title, 'Updated Title')
        self.assertEqual(self.user1_task1.status, 'completed')
    
    def test_user_can_delete_own_task(self):
        """Test that users can delete their own tasks"""
       
        self.client.force_authenticate(user=self.user1)
        
        
        response = self.client.delete(f'/api/tasks/{self.user1_task1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
       
        self.assertFalse(Task.objects.filter(id=self.user1_task1.id).exists())
