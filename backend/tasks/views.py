from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Task
from .serializers import TaskSerializer
from .ai_service import ai_service, OpenRouterError


class TaskViewSet(viewsets.ModelViewSet):
	serializer_class = TaskSerializer
	permission_classes = [IsAuthenticated]
	
	filterset_fields = ['status', 'due_date']
	
	search_fields = ['title', 'description']
	
	ordering_fields = ['created_at', 'updated_at', 'due_date', 'title', 'status']
	ordering = ['-created_at']  

	def get_queryset(self):
		"""Return tasks filtered by authenticated user"""
		return Task.objects.filter(user=self.request.user)
	
	def perform_create(self, serializer):
		"""Assign authenticated user to task on creation"""
		serializer.save(user=self.request.user)
	
	@action(detail=True, methods=['post'], url_path='ai-breakdown')
	def ai_breakdown(self, request, pk=None):
		"""
		Break down a task into smaller, actionable subtasks using AI
		
		POST /api/tasks/{id}/ai-breakdown/
		
		Request body (optional):
		{
			"num_steps": 5  // Number of subtasks to generate (1-10, default 5)
		}
		
		Response:
		{
			"subtasks": ["Step 1", "Step 2", ...],
			"notes": "Optional helpful notes"
		}
		"""
		task = self.get_object()
		num_steps = request.data.get('num_steps', 5)
		
		# Validate num_steps
		if not isinstance(num_steps, int) or num_steps < 1 or num_steps > 10:
			return Response(
				{'error': 'num_steps must be between 1 and 10'},
				status=status.HTTP_400_BAD_REQUEST
			)
		
		try:
			breakdown = ai_service.breakdown_task(
				title=task.title,
				description=task.description or "",
				num_steps=num_steps
			)
			
			return Response(breakdown)
			
		except OpenRouterError as e:
			return Response(
				{'error': str(e)},
				status=status.HTTP_503_SERVICE_UNAVAILABLE
			)
		except Exception as e:
			return Response(
				{'error': 'An unexpected error occurred'},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_task_suggestions(request):
	"""
	Generate AI-powered task suggestions based on context
	
	POST body:
	{
		"context": "Project description or context",
		"num_suggestions": 3  // optional, default 3
	}
	"""
	try:
		context = request.data.get('context', '')
		num_suggestions = request.data.get('num_suggestions', 3)
		
		if not context:
			return Response(
				{'error': 'Context is required'},
				status=status.HTTP_400_BAD_REQUEST
			)
		
		if not isinstance(num_suggestions, int) or num_suggestions < 1 or num_suggestions > 10:
			return Response(
				{'error': 'num_suggestions must be between 1 and 10'},
				status=status.HTTP_400_BAD_REQUEST
			)
		
		suggestions = ai_service.generate_task_suggestions(
			context=context,
			num_suggestions=num_suggestions
		)
		
		return Response({
			'suggestions': suggestions
		})
		
	except OpenRouterError as e:
		return Response(
			{'error': str(e)},
			status=status.HTTP_503_SERVICE_UNAVAILABLE
		)
	except Exception as e:
		return Response(
			{'error': 'An unexpected error occurred'},
			status=status.HTTP_500_INTERNAL_SERVER_ERROR
		)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enhance_task_description(request):
	"""
	Enhance a task description using AI
	
	POST body:
	{
		"title": "Task title",
		"description": "Current description"  // optional
	}
	"""
	try:
		title = request.data.get('title', '')
		description = request.data.get('description', '')
		
		if not title:
			return Response(
				{'error': 'Title is required'},
				status=status.HTTP_400_BAD_REQUEST
			)
		
		enhanced_description = ai_service.enhance_task_description(
			title=title,
			description=description
		)
		
		return Response({
			'enhanced_description': enhanced_description
		})
		
	except OpenRouterError as e:
		return Response(
			{'error': str(e)},
			status=status.HTTP_503_SERVICE_UNAVAILABLE
		)
	except Exception as e:
		return Response(
			{'error': 'An unexpected error occurred'},
			status=status.HTTP_500_INTERNAL_SERVER_ERROR
		)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_task_priority(request):
	"""
	Analyze a task and suggest priority level with reasoning
	
	POST body:
	{
		"title": "Task title",
		"description": "Task description",  // optional
		"due_date": "2024-12-31"  // optional
	}
	"""
	try:
		title = request.data.get('title', '')
		description = request.data.get('description', '')
		due_date = request.data.get('due_date', None)
		
		if not title:
			return Response(
				{'error': 'Title is required'},
				status=status.HTTP_400_BAD_REQUEST
			)
		
		analysis = ai_service.analyze_task_priority(
			title=title,
			description=description,
			due_date=due_date
		)
		
		return Response(analysis)
		
	except OpenRouterError as e:
		return Response(
			{'error': str(e)},
			status=status.HTTP_503_SERVICE_UNAVAILABLE
		)
	except Exception as e:
		return Response(
			{'error': 'An unexpected error occurred'},
			status=status.HTTP_500_INTERNAL_SERVER_ERROR
		)

