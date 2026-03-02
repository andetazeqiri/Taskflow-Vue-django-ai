<template>
  <div class="tasks-container">
    <!-- Hero/Navigation Section -->
    <div class="tasks-hero">
      <div class="hero-content">
        <div>
          <h1 class="hero-title">Tasks</h1>
          <p class="hero-subtitle">Manage and organize your tasks efficiently</p>
        </div>
        <div class="hero-buttons">
          <Button
            label="Generate Suggestions"
            icon="pi pi-lightbulb"
            @click="showSuggestionsDialog = true"
            severity="warning"
            outlined
            size="large"
          />
          <Button
            label="Create Task"
            icon="pi pi-plus"
            @click="showCreateDialog = true"
            severity="success"
            size="large"
          />
        </div>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="tasks-content">
      <!-- Filter Controls -->
      <div class="filters-section">
        <div class="filters-grid">
          <div class="filter-item">
            <label for="searchFilter" class="filter-label">
              <i class="pi pi-search"></i> Search
            </label>
            <InputText
              id="searchFilter"
              v-model="filters.search"
              placeholder="Search tasks..."
              class="w-full"
            />
          </div>

          <div class="filter-item">
            <label for="statusFilter" class="filter-label">
              <i class="pi pi-filter"></i> Status
            </label>
            <Dropdown
              id="statusFilter"
              v-model="filters.status"
              :options="[
                { label: 'All Statuses', value: '' },
                ...statusOptions
              ]"
              optionLabel="label"
              optionValue="value"
              placeholder="Filter by status"
              class="w-full"
            />
          </div>

          <div class="filter-item">
            <label for="orderingFilter" class="filter-label">
              <i class="pi pi-sort-alt"></i> Sort By
            </label>
            <Dropdown
              id="orderingFilter"
              v-model="filters.ordering"
              :options="[
                { label: 'Newest First', value: '-created_at' },
                { label: 'Oldest First', value: 'created_at' },
                { label: 'Title (A-Z)', value: 'title' },
                { label: 'Title (Z-A)', value: '-title' },
                { label: 'Due Date (Earliest)', value: 'due_date' },
                { label: 'Due Date (Latest)', value: '-due_date' },
                { label: 'Status', value: 'status' }
              ]"
              optionLabel="label"
              optionValue="value"
              class="w-full"
            />
          </div>

          <div class="filter-item filter-actions">
            <Button
              label="Clear Filters"
              icon="pi pi-filter-slash"
              @click="clearFilters"
              severity="secondary"
              outlined
              class="w-full"
            />
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="taskStore.loading" class="flex justify-center py-8">
        <ProgressSpinner />
      </div>

      <!-- Error State -->
      <div v-else-if="taskStore.error" class="mb-4">
        <Message severity="error" :closable="true">
          {{ taskStore.error }}
        </Message>
      </div>

      <!-- Empty State -->
      <div v-else-if="taskStore.tasks.length === 0" class="empty-state">
        <i class="pi pi-inbox text-6xl mb-4" />
        <p class="empty-state-text">No tasks yet. Create one to get started!</p>
      </div>

      <!-- DataTable -->
      <DataTable
        v-else
        :value="taskStore.tasks"
        responsiveLayout="scroll"
        striped-rows
        :paginator="true"
        :rows="10"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        :rowsPerPageOptions="[5, 10, 20]"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} tasks"
        class="p-datatable-striped"
      >
        <Column field="title" header="Title" style="width: 30%">
          <template #body="{ data }">
            <Button
              :label="data.title"
              @click="navigateToTask(data.id)"
              text
              class="text-left justify-content-start"
              severity="info"
            />
          </template>
        </Column>
        <Column field="description" header="Description" style="width: 30%"></Column>
        <Column field="status" header="Status" style="width: 15%">
          <template #body="{ data }">
            <Dropdown
              :model-value="data.status"
              :options="statusOptions"
              optionLabel="label"
              optionValue="value"
              @change="(e) => handleInlineStatusUpdate(data.id, e.value)"
              :loading="updatingTaskId === data.id"
              class="w-full"
            >
              <template #value="{ value }">
                <Tag
                  :value="value"
                  :severity="getStatusSeverity(value)"
                  :rounded="true"
                />
              </template>
            </Dropdown>
          </template>
        </Column>
        <Column field="due_date" header="Due Date" style="width: 15%">
          <template #body="{ data }">
            {{ formatDate(data.due_date) }}
          </template>
        </Column>
        <Column style="width: 10%; text-align: center">
          <template #body="{ data }">
            <Button
              icon="pi pi-sparkles"
              rounded
              severity="success"
              text
              @click="openAIDialog(data)"
              v-tooltip.top="'AI Assist'"
              class="mr-2"
            />
            <Button
              icon="pi pi-pencil"
              rounded
              severity="info"
              text
              @click="openEditDialog(data)"
              v-tooltip.top="'Edit'"
              class="mr-2"
            />
            <Button
              icon="pi pi-trash"
              rounded
              severity="danger"
              text
              @click="confirmDelete(data)"
            />
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Create/Edit Dialog -->
    <Dialog
      v-model:visible="showCreateDialog"
      :header="isEditMode ? 'Edit Task' : 'Create Task'"
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
            <label for="dueDate" class="form-label">Due Date</label>
            <Calendar
              id="dueDate"
              v-model="formData.due_date"
              :min-date="getTodayDate()"
              show-time
              date-format="yy-mm-dd"
              placeholder="Select due date"
            />
          </div>
        </div>
      </div>

      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times"
          @click="showCreateDialog = false" 
          severity="secondary"
          text
        />
        <Button
          :label="isEditMode ? 'Update' : 'Create'"
          icon="pi pi-check"
          @click="saveTask"
          :loading="taskStore.loading"
          severity="success"
        />
      </template>
    </Dialog>

    <!-- AI Breakdown Dialog -->
    <AIBreakdownDialog
      v-model:visible="showAIDialog"
      :task-id="selectedTaskForAI?.id"
      :task-title="selectedTaskForAI?.title"
      @success="handleAIBreakdownSuccess"
    />

    <!-- AI Generate Suggestions Dialog -->
    <AIGenerateSuggestionsDialog
      v-model:visible="showSuggestionsDialog"
      @task-created="handleTaskCreatedFromSuggestion"
    />

    <!-- Confirm Delete Dialog -->
    <ConfirmDialog
      group="postion"
      :style="{ width: '50vw' }"
      @confirm="deleteTask"
    ></ConfirmDialog>

    <!-- Toast for feedback -->
    <Toast position="bottom-right" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { useTaskStore } from '@/stores/tasks'

import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import ConfirmDialog from 'primevue/confirmdialog'
import Toast from 'primevue/toast'
import Tag from 'primevue/tag'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Dropdown from 'primevue/dropdown'
import Calendar from 'primevue/calendar'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import Tooltip from 'primevue/tooltip'
import AIBreakdownDialog from '@/components/AIBreakdownDialog.vue'
import AIGenerateSuggestionsDialog from '@/components/AIGenerateSuggestionsDialog.vue'

const vTooltip = Tooltip

const router = useRouter()
const route = useRoute()
const toast = useToast()
const confirm = useConfirm()
const taskStore = useTaskStore()

const showCreateDialog = ref(false)
const isEditMode = ref(false)
const showAIDialog = ref(false)
const showSuggestionsDialog = ref(false)
const selectedTaskForAI = ref(null)
const selectedTaskId = ref(null)
const updatingTaskId = ref(null)

// Filters state
const filters = ref({
  search: '',
  status: '',
  ordering: '-created_at'
})

const statusOptions = [
  { label: 'Pending', value: 'pending' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Completed', value: 'completed' },
  { label: 'Cancelled', value: 'cancelled' }
]

// Get today's date at midnight for min-date validation
const getTodayDate = () => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return today
}

const formData = ref({
  title: '',
  description: '',
  status: 'pending',
  due_date: null
})

const resetForm = () => {
  formData.value = {
    title: '',
    description: '',
    status: 'pending',
    due_date: null
  }
  isEditMode.value = false
  selectedTaskId.value = null
}

const openEditDialog = (task) => {
  isEditMode.value = true
  selectedTaskId.value = task.id
  formData.value = {
    title: task.title,
    description: task.description,
    status: task.status,
    due_date: task.due_date ? new Date(task.due_date) : null
  }
  showCreateDialog.value = true
}

const openAIDialog = (task) => {
  selectedTaskForAI.value = task
  showAIDialog.value = true
}

const handleAIBreakdownSuccess = (breakdown) => {
  toast.add({
    severity: 'success',
    summary: 'AI Breakdown Generated',
    detail: `Generated ${breakdown.subtasks.length} actionable subtasks for "${selectedTaskForAI.value?.title}"`,
    life: 4000
  })
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

  // Validate due date is not in the past
  if (formData.value.due_date) {
    const selectedDate = new Date(formData.value.due_date)
    selectedDate.setHours(0, 0, 0, 0)
    const today = getTodayDate()
    
    if (selectedDate < today) {
      toast.add({
        severity: 'error',
        summary: 'Validation Error',
        detail: 'Due date cannot be in the past',
        life: 3000
      })
      return
    }
  }

  try {
    const payload = {
      ...formData.value,
      due_date: formData.value.due_date
        ? formData.value.due_date.toISOString()
        : null
    }

    if (isEditMode.value) {
      await taskStore.updateTask(selectedTaskId.value, payload)
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Task updated successfully',
        life: 3000
      })
    } else {
      await taskStore.createTask(payload)
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Task created successfully',
        life: 3000
      })
    }

    showCreateDialog.value = false
    resetForm()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: taskStore.error || 'Failed to save task',
      life: 3000
    })
  }
}

const confirmDelete = (task) => {
  confirm.require({
    group: 'postion',
    message: `Are you sure you want to delete "${task.title}"?`,
    header: 'Confirm Delete',
    icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      try {
        await taskStore.deleteTask(task.id)
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Task deleted successfully',
          life: 3000
        })
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete task',
          life: 3000
        })
      }
    }
  })
}

const handleInlineStatusUpdate = async (taskId, newStatus) => {
  updatingTaskId.value = taskId
  
  try {
    await taskStore.updateTaskStatus(taskId, newStatus)
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Task status updated',
      life: 2000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: taskStore.error || 'Failed to update task status',
      life: 3000
    })
  } finally {
    updatingTaskId.value = null
  }
}

const handleTaskCreatedFromSuggestion = (task) => {
  // Task is already added to the store from the suggestion dialog
  showSuggestionsDialog.value = false
  toast.add({
    severity: 'success',
    summary: 'Task Created',
    detail: `Task created: ${task.title}`,
    life: 3000
  })
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

const navigateToTask = (taskId) => {
  router.push({ name: 'taskDetail', params: { id: taskId } })
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}


const initFiltersFromQuery = () => {
  filters.value.search = route.query.search || ''
  filters.value.status = route.query.status || ''
  filters.value.ordering = route.query.ordering || '-created_at'
}

const fetchTasksWithFilters = async () => {
  const params = {}
  
  if (filters.value.search) {
    params.search = filters.value.search
  }
  if (filters.value.status) {
    params.status = filters.value.status
  }
  if (filters.value.ordering) {
    params.ordering = filters.value.ordering
  }
  
  await taskStore.fetchTasks(params)
}

const updateURLFromFilters = () => {
  const query = {}
  
  if (filters.value.search) {
    query.search = filters.value.search
  }
  if (filters.value.status) {
    query.status = filters.value.status
  }
  if (filters.value.ordering !== '-created_at') {
    query.ordering = filters.value.ordering
  }
  
  router.push({ query })
}

const clearFilters = () => {
  filters.value.search = ''
  filters.value.status = ''
  filters.value.ordering = '-created_at'
}

watch(filters, () => {
  updateURLFromFilters()
  fetchTasksWithFilters()
}, { deep: true })


watch(() => route.query, () => {
  initFiltersFromQuery()
  fetchTasksWithFilters()
})

onMounted(() => {
  initFiltersFromQuery()
  fetchTasksWithFilters()
})
</script>

<style scoped>
.tasks-container {
  min-height: 100vh;
  background: var(--surface-ground);
}

/* Hero Section */
.tasks-hero {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-600) 100%);
  padding: 3rem 2rem;
  color: white;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.hero-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.hero-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0;
  color: white;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0.5rem 0 0 0;
}

.hero-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

/* Content Area */
.tasks-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

/* Filters Section */
.filters-section {
  background: var(--surface-card);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid var(--surface-border);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  align-items: end;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-label {
  color: var(--text-color);
  font-weight: 600;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-label i {
  color: var(--primary-color);
}

.filter-actions {
  display: flex;
  align-items: flex-end;
}


/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  color: var(--text-color-secondary);
}

.empty-state i {
  color: var(--primary-color);
  opacity: 0.5;
}

.empty-state-text {
  font-size: 1.125rem;
  margin: 1rem 0 0 0;
}

/* DataTable Customization */
:deep(.p-datatable) {
  background: var(--surface-card);
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background: var(--surface-section);
  color: var(--text-color);
  border-color: var(--surface-border);
  font-weight: 600;
  padding: 1rem;
}

:deep(.p-datatable .p-datatable-tbody > tr) {
  border-color: var(--surface-border);
}

:deep(.p-datatable .p-datatable-tbody > tr:hover) {
  background: var(--surface-50);
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 1rem;
  color: var(--text-color);
}

:deep(.p-paginator) {
  background: var(--surface-section);
  border-top: 1px solid var(--surface-border);
  padding: 1rem;
}

:deep(.p-paginator-current) {
  color: var(--text-color-secondary);
}

/* Inline Status Dropdown */
:deep(.p-datatable .p-datatable-tbody > tr > td .p-dropdown) {
  width: 100%;
  background: transparent;
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius);
  transition: all 0.2s ease;
}

:deep(.p-datatable .p-datatable-tbody > tr > td .p-dropdown:hover) {
  border-color: var(--primary-color);
  background: var(--surface-ground);
}

:deep(.p-datatable .p-datatable-tbody > tr > td .p-dropdown-trigger) {
  color: var(--text-color-secondary);
  padding: 0.5rem;
}

:deep(.p-datatable .p-datatable-tbody > tr > td .p-dropdown.p-focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 0.2rem rgba(var(--primary-color-rgb), 0.2);
}

/* Dialog Customization */
:deep(.p-dialog) {
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
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
  transition: color 0.2s;
}

:deep(.p-dialog .p-dialog-header .p-dialog-header-close:hover) {
  color: white;
}

:deep(.p-dialog .p-dialog-content) {
  background: var(--surface-card);
  padding: 2rem;
  color: var(--text-color);
}

:deep(.p-dialog .p-dialog-footer) {
  background: var(--surface-section);
  border-top: 1px solid var(--surface-border);
  padding: 1.5rem;
  gap: 0.75rem;
  display: flex;
  justify-content: flex-end;
}

/* Input Labels and Organization */
:deep(.p-dialog label) {
  color: var(--text-color);
  font-weight: 600;
  margin-bottom: 0.75rem;
  display: block;
  font-size: 0.95rem;
}

:deep(.p-dialog .p-field-label) {
  color: var(--text-color);
}

:deep(.p-inputtext,
.p-inputtextarea) {
  background: var(--surface-ground);
  border: 1px solid var(--surface-border);
  color: var(--text-color);
  padding: 0.75rem;
  border-radius: var(--border-radius);
}

:deep(.p-inputtext:focus,
.p-inputtextarea:focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 0.2rem rgba(var(--primary-color-rgb), 0.2);
}

:deep(.p-dropdown,
.p-calendar) {
  background: var(--surface-ground);
  border: 1px solid var(--surface-border);
  color: var(--text-color);
  border-radius: var(--border-radius);
}

:deep(.p-dropdown:focus,
.p-calendar:focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 0.2rem rgba(var(--primary-color-rgb), 0.2);
}

/* Tag Styling */
:deep(.p-tag) {
  padding: 0.5rem 0.75rem;
  border-radius: var(--border-radius);
  font-size: 0.875rem;
  font-weight: 500;
}

/* Message Styling */
:deep(.p-message) {
  background: var(--surface-50);
  border-left: 4px solid var(--primary-color);
  border-radius: var(--border-radius);
  padding: 1rem;
}

:deep(.p-message-error) {
  background: rgba(var(--red-500-rgb), 0.1);
  border-left-color: var(--red-500);
}

:deep(.p-message .p-message-text) {
  color: var(--text-color);
}

/* Button Styles in Dialog */
:deep(.p-dialog .p-button) {
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius);
  font-weight: 500;
}

/* Form Organization */
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

:deep(.p-inputtext,
.p-inputtextarea,
.p-dropdown,
.p-calendar) {
  padding: 0.75rem;
  width: 100%;
  font-size: 0.95rem;
}

:deep(.p-dropdown-trigger,
.p-calendar-trigger) {
  color: var(--text-color-secondary);
}

/* Flex Utilities */
.flex {
  display: flex;
}

.flex-col {
  flex-direction: column;
}

.gap-4 {
  gap: 1rem;
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

.mb-2 {
  margin-bottom: 0.5rem;
}

.mr-2 {
  margin-right: 0.5rem;
}

.w-full {
  width: 100%;
}

@media (max-width: 768px) {
  .hero-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-title {
    font-size: 2rem;
  }

  .tasks-hero {
    padding: 2rem 1rem;
  }

  .tasks-content {
    padding: 1rem;
  }

  .filters-section {
    padding: 1rem;
  }

  .filters-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  :deep(.p-dialog) {
    width: 90vw !important;
  }

  :deep(.p-datatable) {
    font-size: 0.875rem;
  }

  :deep(.p-datatable .p-datatable-thead > tr > th,
  .p-datatable .p-datatable-tbody > tr > td) {
    padding: 0.75rem 0.5rem;
  }
}
</style>
