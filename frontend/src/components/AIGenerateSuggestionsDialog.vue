<template>
  <Dialog
    :visible="visible"
    modal
    header=" Generate Task Suggestions"
    :style="{ width: '600px' }"
    :closable="!loading"
    @update:visible="handleClose"
  >
    <!-- Loading State -->
    <div v-if="loading" class="ai-dialog-loading">
      <div class="flex flex-column align-items-center gap-3">
        <ProgressSpinner
          style="width: 50px; height: 50px"
          strokeWidth="4"
          animationDuration="1s"
        />
        <p class="text-center">Generating task suggestions...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="ai-dialog-error">
      <Message severity="error" :closable="false">
        {{ error }}
      </Message>
    </div>

    <!-- Results State -->
    <div v-else-if="result && result.suggestions" class="ai-dialog-result">
      <div class="result-intro">
        <i class="pi pi-check-circle" style="color: var(--primary-color); font-size: 1.5rem"></i>
        <p>Here are AI-generated task suggestions for your project:</p>
      </div>

      <div class="suggestions-list">
        <div
          v-for="(suggestion, index) in result.suggestions"
          :key="index"
          class="suggestion-item"
        >
          <div class="suggestion-number">{{ index + 1 }}</div>
          <div class="suggestion-content">
            <p class="suggestion-text">{{ suggestion }}</p>
            <Button
              icon="pi pi-plus"
              @click="createTaskFromSuggestion(suggestion)"
              severity="success"
              rounded
              text
              size="small"
              label="Add as Task"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Initial State -->
    <div v-else class="ai-dialog-initial">
      <p>Provide a project description or context to generate AI-powered task suggestions.</p>

      <div class="field">
        <label for="context">Project Description</label>
        <Textarea
          id="context"
          v-model="context"
          placeholder="E.g., Build a mobile app for task management with user authentication..."
          rows="4"
          class="w-full"
        />
      </div>

      <div class="field">
        <label for="numSuggestions">Number of Suggestions</label>
        <Slider
          v-model="numSuggestions"
          :min="1"
          :max="10"
          :step="1"
          class="w-full"
        />
        <div class="flex justify-content-between mt-2">
          <small>{{ numSuggestions }} suggestions</small>
          <small class="text-color-secondary">1-10 suggestions</small>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <template #footer>
      <div class="flex justify-content-end gap-2">
        <Button
          v-if="!result"
          label="Cancel"
          severity="secondary"
          @click="handleClose"
          :disabled="loading"
          text
        />
        <Button
          v-if="result"
          label="Close"
          @click="handleClose"
          autofocus
        />
        <Button
          v-if="!result"
          label="Generate Suggestions"
          icon="pi pi-sparkles"
          @click="generate"
          :loading="loading"
          :disabled="loading || !context.trim()"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import Textarea from 'primevue/textarea'
import Slider from 'primevue/slider'
import { useToast } from 'primevue/usetoast'

const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['update:visible', 'task-created'])

const toast = useToast()
const loading = ref(false)
const error = ref(null)
const result = ref(null)
const context = ref('')
const numSuggestions = ref(3)

const handleClose = () => {
  emit('update:visible', false)
  setTimeout(() => {
    result.value = null
    error.value = null
  }, 300)
}

const generate = async () => {
  if (!context.value.trim()) {
    error.value = 'Please enter a project description'
    return
  }

  loading.value = true
  error.value = null

  try {
    const { useTaskStore } = await import('@/stores/tasks')
    const taskStore = useTaskStore()

    const data = await taskStore.generateTaskSuggestions(
      context.value,
      numSuggestions.value
    )
    result.value = data
  } catch (err) {
    error.value = err.message || 'Failed to generate suggestions. Please try again.'
  } finally {
    loading.value = false
  }
}

const createTaskFromSuggestion = async (suggestion) => {
  try {
    const { useTaskStore } = await import('@/stores/tasks')
    const taskStore = useTaskStore()

    const newTask = await taskStore.createTask({
      title: suggestion,
      description: '',
      status: 'pending'
    })

    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: `Task "${suggestion}" created successfully`,
      life: 3000
    })

    emit('task-created', newTask)
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to create task',
      life: 3000
    })
  }
}
</script>

<style scoped>
.ai-dialog-loading,
.ai-dialog-initial,
.ai-dialog-result {
  padding: 0 0.5rem;
}

.flex {
  display: flex;
}

.flex-column {
  flex-direction: column;
}

.align-items-center {
  align-items: center;
}

.gap-3 {
  gap: 1rem;
}

.text-center {
  text-align: center;
}

.justify-content-between {
  justify-content: space-between;
}

.justify-content-end {
  justify-content: flex-end;
}

.gap-2 {
  gap: 0.5rem;
}

.w-full {
  width: 100%;
}

.mt-2 {
  margin-top: 0.5rem;
}

.field {
  margin-bottom: 1.5rem;
}

.field label {
  color: var(--text-color);
  font-weight: 600;
  margin-bottom: 0.5rem;
  display: block;
  font-size: 0.95rem;
}

.text-color-secondary {
  color: var(--text-color-secondary);
}

.result-intro {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.result-intro p {
  margin: 0;
  color: var(--text-color);
  font-weight: 500;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.suggestion-item {
  display: flex;
  gap: 1rem;
  background: var(--surface-ground);
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius);
  padding: 1rem;
  align-items: flex-start;
}

.suggestion-number {
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.suggestion-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.suggestion-text {
  margin: 0;
  color: var(--text-color);
  line-height: 1.5;
}

:deep(.p-button.p-button-sm) {
  margin-top: 0.5rem;
}
</style>
