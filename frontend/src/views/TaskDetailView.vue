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
            label="Enhance Description"
            icon="pi pi-pencil-square"
            @click="showEnhanceDialog = true"
            severity="info"
            outlined
          />
          <Button
            label="Analyze Priority"
            icon="pi pi-chart-bar"
            @click="showPriorityDialog = true"
            severity="warning"
            outlined
          />
          <Button
            label="Break Down Task"
            icon="pi pi-list"
            @click="showAIDialog = true"
            severity="success"
            outlined
          />
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

    <!-- Edit Dialog -->
    <Dialog
      v-model:visible="showEditDialog"
      header="Edit Task"
      :modal="true"
      :style="{ width: '50vw' }"
      @hide="resetForm"
    >
      <div class="dialog-form">
        <div class="form-group">
          <label for="title" class="form-label">Title *</label>
          <InputText
            id="title"
            v-model="formData.title"
            placeholder="Enter task title"
            class="w-full"
          />
        </div>

        <div class="form-group">
          <label for="description" class="form-label">Description</label>
          <Textarea
            id="description"
            v-model="formData.description"
            placeholder="Enter task description"
            class="w-full"
            rows="4"
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="status" class="form-label">Status *</label>
            <Dropdown
              id="status"
              v-model="formData.status"
              :options="statusOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Select status"
              class="w-full"
            />
          </div>

          <div class="form-group">
            <label for="due_date" class="form-label">Due Date</label>
            <Calendar
              id="due_date"
              v-model="formData.due_date"
              :showIcon="true"
              placeholder="Select due date"
              dateFormat="yy-mm-dd"
              class="w-full"
            />
          </div>
        </div>
      </div>

      <template #footer>
        <Button
          label="Cancel"
          icon="pi pi-times"
          @click="showEditDialog = false"
          severity="secondary"
          text
        />
        <Button
          label="Update"
          icon="pi pi-check"
          @click="saveTask"
          severity="success"
        />
      </template>
    </Dialog>

    <!-- AI Breakdown Dialog -->
    <AIBreakdownDialog
      v-model:visible="showAIDialog"
      :task-id="task?.id"
      :task-title="task?.title"
      @success="handleAIBreakdownSuccess"
    />

    <!-- AI Enhance Description Dialog -->
    <AIEnhanceDescriptionDialog
      v-model:visible="showEnhanceDialog"
      :task-title="task?.title"
      :task-description="task?.description"
      @enhanced="handleEnhanceSuccess"
    />

    <!-- AI Analyze Priority Dialog -->
    <AIAnalyzePriorityDialog
      v-model:visible="showPriorityDialog"
      :task-title="task?.title"
      :task-description="task?.description"
      :task-due-date="task?.due_date"
      @analyzed="handleAnalyzeSuccess"
    />

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
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Dropdown from 'primevue/dropdown'
import Calendar from 'primevue/calendar'
import AIBreakdownDialog from '@/components/AIBreakdownDialog.vue'
import AIEnhanceDescriptionDialog from '@/components/AIEnhanceDescriptionDialog.vue'
import AIAnalyzePriorityDialog from '@/components/AIAnalyzePriorityDialog.vue'

const router = useRouter()
const route = useRoute()
const toast = useToast()
const taskStore = useTaskStore()

const task = ref(null)
const loading = ref(false)
const updating = ref(false)
const updatingStatus = ref(null)
const error = ref(null)
const showAIDialog = ref(false)
const showEnhanceDialog = ref(false)
const showPriorityDialog = ref(false)
const showEditDialog = ref(false)
const formData = ref({
  title: '',
  description: '',
  status: 'pending',
  due_date: null
})

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
  formData.value = {
    title: task.value.title,
    description: task.value.description,
    status: task.value.status,
    due_date: task.value.due_date ? new Date(task.value.due_date) : null
  }
  showEditDialog.value = true
}

const resetForm = () => {
  formData.value = {
    title: '',
    description: '',
    status: 'pending',
    due_date: null
  }
}

const saveTask = async () => {
  if (!formData.value.title) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'Title is required',
      life: 3000
    })
    return
  }

  try {
    const payload = {
      ...formData.value,
      due_date: formData.value.due_date
        ? formData.value.due_date.toISOString()
        : null
    }

    await taskStore.updateTask(route.params.id, payload)
    
    // Refresh task data
    await fetchTask()
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Task updated successfully',
      life: 3000
    })

    showEditDialog.value = false
    resetForm()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: taskStore.error || 'Failed to update task',
      life: 3000
    })
  }
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

const handleAIBreakdownSuccess = (breakdown) => {
  toast.add({
    severity: 'success',
    summary: 'AI Breakdown Generated',
    detail: `Generated ${breakdown.subtasks.length} actionable subtasks`,
    life: 4000
  })
}

const handleEnhanceSuccess = (result) => {
  toast.add({
    severity: 'success',
    summary: 'Description Enhanced',
    detail: 'Your task description has been improved',
    life: 3000
  })
}

const handleAnalyzeSuccess = (result) => {
  toast.add({
    severity: 'success',
    summary: 'Priority Analyzed',
    detail: `Priority: ${result.priority.toUpperCase()}`,
    life: 3000
  })
}

const goBack = () => {
  router.back()
}

const fetchTask = async () => {
  loading.value = true
  error.value = null

  try {
    task.value = await taskStore.fetchTaskById(route.params.id)
  } catch (err) {
    error.value = 'Failed to load task details. Please try again.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchTask()
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

.w-full {
  width: 100%;
}

/* Dialog Form Styles */
.dialog-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  color: var(--text-color);
  font-weight: 600;
  margin-bottom: 0.75rem;
  font-size: 0.95rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

:deep(.p-dialog) {
  border-radius: var(--border-radius-lg);
  overflow: hidden;
}

:deep(.p-dialog .p-dialog-header) {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-600) 100%);
  border: none;
  padding: 1.5rem;
}

:deep(.p-dialog .p-dialog-header .p-dialog-title) {
  color: white;
  font-weight: 700;
  font-size: 1.25rem;
}

:deep(.p-dialog .p-dialog-header .p-dialog-header-close) {
  color: rgba(255, 255, 255, 0.8);
}

:deep(.p-dialog .p-dialog-header .p-dialog-header-close:hover) {
  color: white;
}

:deep(.p-dialog .p-dialog-content) {
  background: var(--surface-card);
  padding: 2rem;
}

:deep(.p-dialog .p-dialog-footer) {
  background: var(--surface-section);
  border-top: 1px solid var(--surface-border);
  padding: 1.5rem;
}

:deep(.p-inputtext,
.p-inputtextarea,
.p-dropdown,
.p-calendar) {
  background: var(--surface-ground);
  border: 1px solid var(--surface-border);
  color: var(--text-color);
  padding: 0.75rem;
  border-radius: var(--border-radius);
  width: 100%;
}

:deep(.p-inputtext:focus,
.p-inputtextarea:focus,
.p-dropdown:focus,
.p-calendar:focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 0.2rem rgba(var(--primary-color-rgb), 0.2);
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

  .form-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  :deep(.p-dialog) {
    width: 90vw !important;
  }

  :deep(.p-button) {
    width: 100%;
  }
}
</style>
