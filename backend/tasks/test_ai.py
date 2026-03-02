"""
Tests for AI service integration
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from tasks.ai_service import AIService, OpenRouterError

User = get_user_model()


class AIServiceTests(TestCase):
    """Test the AI service functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        
        self.api_key_patcher = patch('tasks.ai_service.OPENROUTER_API_KEY', 'test-key-123')
        self.api_key_patcher.start()
        self.ai_service = AIService()
    
    def tearDown(self):
        """Clean up patches"""
        self.api_key_patcher.stop()
    
    @patch('tasks.ai_service.requests.post')
    def test_generate_task_suggestions_success(self, mock_post):
        """Test successful task suggestion generation"""
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "1. Task one\n2. Task two\n3. Task three"
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        
        suggestions = self.ai_service.generate_task_suggestions(
            context="Build a web app",
            num_suggestions=3
        )
        
        self.assertEqual(len(suggestions), 3)
        self.assertIn("Task", suggestions[0])
    
    @patch('tasks.ai_service.requests.post')
    def test_enhance_task_description_success(self, mock_post):
        """Test successful task description enhancement"""
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "This is an enhanced description with more details."
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        enhanced = self.ai_service.enhance_task_description(
            title="Test task",
            description="Basic description"
        )
        
        self.assertIn("enhanced", enhanced.lower())
    
    @patch('tasks.ai_service.requests.post')
    def test_analyze_task_priority_success(self, mock_post):
        """Test successful task priority analysis"""
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": '{"priority": "high", "reasoning": "Critical task"}'
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        analysis = self.ai_service.analyze_task_priority(
            title="Fix critical bug",
            description="Production is down"
        )
        
        self.assertIn("priority", analysis)
        self.assertIn("reasoning", analysis)
    
    def test_api_key_not_configured(self):
        """Test error handling when API key is not set"""
        
        with patch('tasks.ai_service.OPENROUTER_API_KEY', ''):
            service = AIService()
            
            with self.assertRaises(OpenRouterError) as context:
                service.generate_task_suggestions("test context")
            
            self.assertIn("not configured", str(context.exception).lower())


class AIEndpointTests(TestCase):
    """Test AI API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = APIClient()
        
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        
        self.client.force_authenticate(user=self.user)
    
    def test_generate_suggestions_requires_auth(self):
        """Test that endpoint requires authentication"""
        
        self.client.force_authenticate(user=None)
        
        response = self.client.post('/api/ai/generate-suggestions/', {
            'context': 'Test context'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_generate_suggestions_missing_context(self):
        """Test validation for missing context"""
        response = self.client.post('/api/ai/generate-suggestions/', {})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_generate_suggestions_invalid_num_suggestions(self):
        """Test validation for invalid num_suggestions"""
        response = self.client.post('/api/ai/generate-suggestions/', {
            'context': 'Test context',
            'num_suggestions': 20  
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('tasks.views.ai_service.generate_task_suggestions')
    def test_generate_suggestions_success(self, mock_generate):
        """Test successful task suggestion generation"""
        
        mock_generate.return_value = [
            "Task 1",
            "Task 2",
            "Task 3"
        ]
        
        response = self.client.post(
            '/api/ai/generate-suggestions/',
            {
                'context': 'Build a mobile app',
                'num_suggestions': 3
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('suggestions', response.data)
        self.assertEqual(len(response.data['suggestions']), 3)
    
    def test_enhance_description_requires_auth(self):
        """Test that endpoint requires authentication"""
        
        self.client.force_authenticate(user=None)
        
        response = self.client.post('/api/ai/enhance-description/', {
            'title': 'Test task'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_enhance_description_missing_title(self):
        """Test validation for missing title"""
        response = self.client.post('/api/ai/enhance-description/', {})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('tasks.views.ai_service.enhance_task_description')
    def test_enhance_description_success(self, mock_enhance):
        """Test successful description enhancement"""
        
        mock_enhance.return_value = "Enhanced description with more details"
        
        response = self.client.post('/api/ai/enhance-description/', {
            'title': 'Write documentation',
            'description': 'Basic docs'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('enhanced_description', response.data)
    
    def test_analyze_priority_requires_auth(self):
        """Test that endpoint requires authentication"""
        
        self.client.force_authenticate(user=None)
        
        response = self.client.post('/api/ai/analyze-priority/', {
            'title': 'Test task'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_analyze_priority_missing_title(self):
        """Test validation for missing title"""
        response = self.client.post('/api/ai/analyze-priority/', {})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('tasks.views.ai_service.analyze_task_priority')
    def test_analyze_priority_success(self, mock_analyze):
        """Test successful priority analysis"""
        
        mock_analyze.return_value = {
            "priority": "high",
            "reasoning": "Critical task requiring immediate attention"
        }
        
        response = self.client.post('/api/ai/analyze-priority/', {
            'title': 'Fix production bug',
            'description': 'Users cannot login'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('priority', response.data)
        self.assertIn('reasoning', response.data)
    
    @patch('tasks.views.ai_service.generate_task_suggestions')
    def test_openrouter_error_handling(self, mock_generate):
        """Test handling of OpenRouter API errors"""
        
        mock_generate.side_effect = OpenRouterError("API error")
        
        response = self.client.post('/api/ai/generate-suggestions/', {
            'context': 'Test context'
        })
        
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn('error', response.data)


class AIBreakdownTests(TestCase):
    """Test AI task breakdown functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        
        self.api_key_patcher = patch('tasks.ai_service.OPENROUTER_API_KEY', 'test-key-123')
        self.api_key_patcher.start()
        self.ai_service = AIService()
    
    def tearDown(self):
        """Clean up patches"""
        self.api_key_patcher.stop()
    
    @patch('tasks.ai_service.requests.post')
    def test_breakdown_task_success(self, mock_post):
        """Test successful task breakdown"""
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": '{"subtasks": ["Step 1", "Step 2", "Step 3"], "notes": "Test notes"}'
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        
        result = self.ai_service.breakdown_task(
            title="Build a website",
            description="Create a portfolio site",
            num_steps=3
        )
        
        
        self.assertIn('subtasks', result)
        self.assertIn('notes', result)
        self.assertEqual(len(result['subtasks']), 3)


class AIBreakdownEndpointTests(TestCase):
    """Test AI breakdown API endpoint"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = APIClient()
        
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        
        self.client.force_authenticate(user=self.user)
        
        
        from tasks.models import Task
        self.task = Task.objects.create(
            user=self.user,
            title='Build mobile app',
            description='Create a task management app',
            status='todo'
        )
    
    def test_breakdown_requires_auth(self):
        """Test that endpoint requires authentication"""
        
        self.client.force_authenticate(user=None)
        
        response = self.client.post(f'/api/tasks/{self.task.id}/ai-breakdown/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_breakdown_invalid_num_steps(self):
        """Test validation for invalid num_steps"""
        response = self.client.post(
            f'/api/tasks/{self.task.id}/ai-breakdown/',
            {'num_steps': 20},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('tasks.views.ai_service.breakdown_task')
    def test_breakdown_success(self, mock_breakdown):
        """Test successful task breakdown"""
        
        mock_breakdown.return_value = {
            "subtasks": [
                "Design UI mockups",
                "Set up development environment",
                "Implement authentication",
                "Create task CRUD",
                "Add notifications"
            ],
            "notes": "Focus on MVP features first"
        }
        
        response = self.client.post(
            f'/api/tasks/{self.task.id}/ai-breakdown/',
            {'num_steps': 5},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('subtasks', response.data)
        self.assertIn('notes', response.data)
        self.assertEqual(len(response.data['subtasks']), 5)
    
    @patch('tasks.views.ai_service.breakdown_task')
    def test_breakdown_default_num_steps(self, mock_breakdown):
        """Test breakdown with default num_steps"""
        
        mock_breakdown.return_value = {
            "subtasks": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"],
            "notes": ""
        }
        
        response = self.client.post(
            f'/api/tasks/{self.task.id}/ai-breakdown/',
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        mock_breakdown.assert_called_once_with(
            title=self.task.title,
            description=self.task.description,
            num_steps=5
        )
    
    def test_breakdown_task_not_found(self):
        """Test breakdown for non-existent task"""
        response = self.client.post(
            '/api/tasks/99999/ai-breakdown/',
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_breakdown_other_user_task(self):
        """Test that users cannot breakdown other users' tasks"""
        
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        from tasks.models import Task
        other_task = Task.objects.create(
            user=other_user,
            title='Other user task',
            description='Should not be accessible',
            status='todo'
        )
        
        response = self.client.post(
            f'/api/tasks/{other_task.id}/ai-breakdown/',
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    @patch('tasks.views.ai_service.breakdown_task')
    def test_breakdown_openrouter_error(self, mock_breakdown):
        """Test handling of OpenRouter errors"""
        
        mock_breakdown.side_effect = OpenRouterError("API error")
        
        response = self.client.post(
            f'/api/tasks/{self.task.id}/ai-breakdown/',
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn('error', response.data)
