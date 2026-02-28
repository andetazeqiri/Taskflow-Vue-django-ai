<template>
  <div class="task-detail-container">
    <!-- Header -->
    <div class="detail-header">
      <Button
        icon="pi pi-arrow-left"
        @click="goBack"
        severity="secondary"
        text
        rounded
      />
      <h1 class="detail-title">Task Details</h1>
      <div></div>
    </div>

    <!-- Content -->
    <div class="detail-content">
      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center py-8">
        <ProgressSpinner />
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="mb-4">
        <Message severity="error">
          {{ error }}
          <Button
            label="Back to Tasks"
            icon="pi pi-arrow-left"
            @click="goBack"
            text
            class="mt-2"
          />
        </Message>
      </div>

      <!-- Task Detail -->
      <div v-else-if="task" class="task-detail-card">
        <!-- Status Update Section -->
        <div class="status-section">
          <div class="status-header">
            <h2>Status</h2>
            <Tag
              :value="formatStatus(task.status)"
              :severity="getStatusSeverity(task.status)"
              :rounded="true"
            />
          </div>

          <div class="status-controls">
            <Button
              v-for="option in statusOptions"
              :key="option.value"
              :label="option.label"
              :severity="option.value === task.status ? 'success' : 'secondary'"
              @click="updateStatus(option.value)"
              :loading="updating && updatingStatus === option.value"
              outlined
            />
          </div>
        </div>

        <!-- Task Details Grid -->
        <div class="details-grid">
          <!-- Title -->
          <div class="detail-field">
            <label>Title</label>
            <p class="detail-value">{{ task.title }}</p>
          </div>

          <!-- Status -->
          <div class="detail-field">
            <label>Current Status</label>
            <p class="detail-value">
              <Tag
                :value="formatStatus(task.status)"
                :severity="getStatusSeverity(task.status)"
              />
            </p>
          </div>

          <!-- Due Date -->
          <div class="detail-field">
            <label>Due Date</label>
            <p class="detail-value">{{ formatDate(task.due_date) }}</p>
          </div>

          <!-- Created Date -->
          <div class="detail-field">
            <label>Created</label>
            <p class="detail-value">{{ formatDate(task.created_at) }}</p>
          </div>

          <!-- Updated Date -->
          <div class="detail-field">
            <label>Last Updated</label>
            <p class="detail-value">{{ formatDate(task.updated_at) }}</p>
          </div>
        </div>

        <!-- Description -->
        <div class="description-section">
          <label>Description</label>
          <div class="description-content">
            {{ task.description || 'No description provided' }}
          </div>
        </div>

        <!-- Actions -->
        <div class="actions-section">
          <Button
            label="Edit Task"
            icon="pi pi-pencil"
            @click="editTask"
            severity="info"
          />
          <Button
            label="Delete Task"
            icon="pi pi-trash"
            @click="deleteTask"
            severity="danger"
          />
          <Button
            label="Back to Tasks"
            icon="pi pi-arrow-left"
            @click="goBack"
            severity="secondary"
          />
        </div>
      </div>
    </div>

    <!-- Toast for feedback -->
    <Toast position="bottom-right" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useTaskStore } from '@/stores/tasks'

import Button from 'primevue/button'
import Message from 'primevue/message'
import Tag from 'primevue/tag'
import Toast from 'primevue/toast'
import ProgressSpinner from 'primevue/progressspinner'

const router = useRouter()
const route = useRoute()
const toast = useToast()
const taskStore = useTaskStore()

const task = ref(null)
const loading = ref(false)
const updating = ref(false)
const updatingStatus = ref(null)
const error = ref(null)

const statusOptions = [
  { label: 'Pending', value: 'pending' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Completed', value: 'completed' },
  { label: 'Cancelled', value: 'cancelled' }
]

const formatStatus = (status) => {
  const statusMap = {
    pending: 'Pending',
    in_progress: 'In Progress',
    completed: 'Completed',
    cancelled: 'Cancelled'
  }
  return statusMap[status] || status
}

const getStatusSeverity = (status) => {
  const severities = {
    pending: 'warning',
    in_progress: 'info',
    completed: 'success',
    cancelled: 'danger'
  }
  return severities[status] || 'info'
}

const formatDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const updateStatus = async (newStatus) => {
  if (newStatus === task.value.status) return

  updating.value = true
  updatingStatus.value = newStatus

  try {
    const updated = await taskStore.updateTaskStatus(route.params.id, newStatus)
    task.value = updated
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: `Task status updated to ${formatStatus(newStatus)}`,
      life: 3000
    })
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: taskStore.error || 'Failed to update task status',
      life: 3000
    })
  } finally {
    updating.value = false
    updatingStatus.value = null
  }
}

const editTask = () => {
  router.push({
    name: 'tasks',
    query: { edit: route.params.id }
  })
}

const deleteTask = () => {
  if (confirm('Are you sure you want to delete this task?')) {
    taskStore.deleteTask(route.params.id).then(() => {
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Task deleted successfully',
        life: 3000
      })
      router.push('/tasks')
    }).catch(err => {
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to delete task',
        life: 3000
      })
    })
  }
}

const goBack = () => {
  router.back()
}

onMounted(async () => {
  loading.value = true
  error.value = null

  try {
    task.value = await taskStore.fetchTaskById(route.params.id)
  } catch (err) {
    error.value = 'Failed to load task details. Please try again.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.task-detail-container {
  min-height: 100vh;
  background: var(--surface-ground);
}

.detail-header {
  background: var(--surface-card);
  border-bottom: 1px solid var(--surface-border);
  padding: 1.5rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.detail-title {
  color: var(--text-color);
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  flex: 1;
}

.detail-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.task-detail-card {
  background: var(--surface-card);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--surface-border);
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Status Section */
.status-section {
  background: var(--primary-50);
  border-bottom: 1px solid var(--surface-border);
  padding: 2rem;
}

.status-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.status-header h2 {
  color: var(--text-color);
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.status-controls {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
}

/* Details Grid */
.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  padding: 2rem;
  border-bottom: 1px solid var(--surface-border);
}

.detail-field {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-field label {
  color: var(--text-color-secondary);
  font-weight: 600;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  color: var(--text-color);
  font-size: 1rem;
  margin: 0;
  word-break: break-word;
}

/* Description Section */
.description-section {
  padding: 2rem;
  border-bottom: 1px solid var(--surface-border);
}

.description-section label {
  display: block;
  color: var(--text-color-secondary);
  font-weight: 600;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.75rem;
}

.description-content {
  background: var(--surface-ground);
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius);
  padding: 1.5rem;
  color: var(--text-color);
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  min-height: 120px;
}

/* Actions Section */
.actions-section {
  padding: 2rem;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

:deep(.p-button) {
  flex: 1;
  min-width: 140px;
}

/* Utilities */
.flex {
  display: flex;
}

.justify-center {
  justify-content: center;
}

.py-8 {
  padding-top: 2rem;
  padding-bottom: 2rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

/* Responsive */
@media (max-width: 768px) {
  .detail-header {
    padding: 1rem;
    flex-direction: column;
    text-align: center;
  }

  .detail-title {
    font-size: 1.5rem;
  }

  .detail-content {
    padding: 1rem;
  }

  .status-section {
    padding: 1.5rem;
  }

  .status-controls {
    grid-template-columns: 1fr;
  }

  .details-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    padding: 1.5rem;
  }

  .description-section,
  .actions-section {
    padding: 1.5rem;
  }

  .actions-section {
    flex-direction: column;
  }

  :deep(.p-button) {
    width: 100%;
  }
}
</style>
