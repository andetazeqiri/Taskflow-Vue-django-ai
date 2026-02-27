<template>
  <div class="tasks-container p-6">
    <div class="mb-4">
      <h1 class="text-3xl font-bold mb-4">Tasks</h1>
      <Button
        label="New Task"
        icon="pi pi-plus"
        @click="showCreateDialog = true"
        class="p-button-success"
      />
    </div>

    <!-- Loading State -->
    <div v-if="taskStore.loading" class="flex justify-center py-8">
      <ProgressSpinner />
    </div>

    <!-- Error State -->
    <div v-else-if="taskStore.error" class="mb-4">
      <Message severity="error" :text="taskStore.error" closable />
    </div>

    <!-- Empty State -->
    <div v-else-if="taskStore.tasks.length === 0" class="text-center py-8">
      <p class="text-gray-500 text-lg">No tasks yet. Create one to get started!</p>
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
      <Column field="title" header="Title" style="width: 30%"></Column>
      <Column field="description" header="Description" style="width: 30%"></Column>
      <Column field="status" header="Status" style="width: 15%">
        <template #body="{ data }">
          <Tag
            :value="data.status"
            :severity="getStatusSeverity(data.status)"
            :rounded="true"
          />
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
            icon="pi pi-pencil"
            rounded
            severity="info"
            text
            @click="openEditDialog(data)"
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

    <!-- Create/Edit Dialog -->
    <Dialog
      v-model:visible="showCreateDialog"
      :header="isEditMode ? 'Edit Task' : 'Create Task'"
      :modal="true"
      :style="{ width: '50vw' }"
      @hide="resetForm"
    >
      <div class="flex flex-col gap-4">
        <div>
          <label for="title" class="block mb-2">Title *</label>
          <InputText
            id="title"
            v-model="formData.title"
            placeholder="Enter task title"
            class="w-full"
          />
        </div>

        <div>
          <label for="description" class="block mb-2">Description</label>
          <Textarea
            id="description"
            v-model="formData.description"
            placeholder="Enter task description"
            class="w-full"
            rows="4"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="status" class="block mb-2">Status *</label>
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

          <div>
            <label for="dueDate" class="block mb-2">Due Date</label>
            <Calendar
              id="dueDate"
              v-model="formData.due_date"
              show-time
              date-format="yy-mm-dd"
              placeholder="Select due date"
            />
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Cancel" @click="showCreateDialog = false" class="p-button-text" />
        <Button
          :label="isEditMode ? 'Update' : 'Create'"
          @click="saveTask"
          :loading="taskStore.loading"
        />
      </template>
    </Dialog>

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
import { ref, onMounted, computed } from 'vue'
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

const toast = useToast()
const confirm = useConfirm()
const taskStore = useTaskStore()

const showCreateDialog = ref(false)
const isEditMode = ref(false)
const selectedTaskId = ref(null)

const statusOptions = [
  { label: 'Pending', value: 'pending' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Completed', value: 'completed' },
  { label: 'Cancelled', value: 'cancelled' }
]

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
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

onMounted(() => {
  taskStore.fetchTasks()
})
</script>

<style scoped>
.tasks-container {
  max-width: 1400px;
  margin: 0 auto;
}
</style>
