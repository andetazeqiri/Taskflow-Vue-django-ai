import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/axios'

export const useTaskStore = defineStore('tasks', () => {
  
  const tasks = ref([])
  const loading = ref(false)
  const error = ref(null)

  
  const taskCount = computed(() => tasks.value.length)

  
  const fetchTasks = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/tasks/', { params })
      tasks.value = response.data.results || response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch tasks'
      console.error('Fetch tasks error:', err)
    } finally {
      loading.value = false
    }
  }

  const createTask = async (taskData) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/tasks/', taskData)
      tasks.value.unshift(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create task'
      console.error('Create task error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateTask = async (taskId, taskData) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.patch(`/tasks/${taskId}/`, taskData)
      const index = tasks.value.findIndex((t) => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update task'
      console.error('Update task error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteTask = async (taskId) => {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/tasks/${taskId}/`)
      tasks.value = tasks.value.filter((t) => t.id !== taskId)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete task'
      console.error('Delete task error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchTaskById = async (taskId) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get(`/tasks/${taskId}/`)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch task'
      console.error('Fetch task error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateTaskStatus = async (taskId, status) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.patch(`/tasks/${taskId}/`, { status })
      const index = tasks.value.findIndex((t) => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update task status'
      console.error('Update status error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const breakdownTask = async (taskId, numSteps = 5) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post(`/tasks/${taskId}/ai-breakdown/`, { num_steps: numSteps })
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to generate task breakdown'
      console.error('Breakdown task error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const generateTaskSuggestions = async (context, numSuggestions = 3) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/ai/generate-suggestions/', { context, num_suggestions: numSuggestions })
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to generate suggestions'
      console.error('Generate suggestions error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const enhanceTaskDescription = async (title, description = '') => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/ai/enhance-description/', { title, description })
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to enhance description'
      console.error('Enhance description error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const analyzeTaskPriority = async (title, description = '', dueDate = null) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/ai/analyze-priority/', { title, description, due_date: dueDate })
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to analyze priority'
      console.error('Analyze priority error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
   
    tasks,
    loading,
    error,
  
    taskCount,
   
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    fetchTaskById,
    updateTaskStatus,
    breakdownTask,
    generateTaskSuggestions,
    enhanceTaskDescription,
    analyzeTaskPriority
  }
})
