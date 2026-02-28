from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Task
from .serializers import TaskSerializer


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
