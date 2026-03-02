<template>
  <Dialog
    :visible="visible"
    modal
    :header="dialogTitle"
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
        <p class="text-center">{{ loadingMessage }}</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="ai-dialog-error">
      <Message severity="error" :closable="false">
        {{ error }}
      </Message>
    </div>

    <!-- Results State -->
    <div v-else-if="result && result.subtasks" class="ai-dialog-result">
      <div class="result-intro">
        <i class="pi pi-check-circle" style="color: var(--primary-color); font-size: 1.5rem"></i>
        <p>Here's a breakdown of your task into actionable steps:</p>
      </div>

      <div class="subtasks-list">
        <div
          v-for="(subtask, index) in result.subtasks"
          :key="index"
          class="subtask-item"
        >
          <div class="subtask-number">{{ index + 1 }}</div>
          <div class="subtask-text">{{ subtask }}</div>
        </div>
      </div>

      <div v-if="result.notes" class="result-notes">
        <div class="notes-header">
          <i class="pi pi-info-circle"></i>
          <span>Additional Notes</span>
        </div>
        <p>{{ result.notes }}</p>
      </div>
    </div>

    <!-- Initial State -->
    <div v-else class="ai-dialog-initial">
      <p>Generate AI-powered subtasks to break down this task into smaller, actionable steps.</p>
      
      <div class="field">
        <label for="numSteps">Number of subtasks</label>
        <Slider
          v-model="numSteps"
          :min="3"
          :max="10"
          :step="1"
          class="w-full"
        />
        <div class="flex justify-content-between mt-2">
          <small>{{ numSteps }} steps</small>
          <small class="text-color-secondary">3-10 steps recommended</small>
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
          label="Generate Breakdown"
          icon="pi pi-sparkles"
          @click="generateBreakdown"
          :loading="loading"
          :disabled="loading"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import Slider from 'primevue/slider'

const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  },
  taskId: {
    type: Number,
    required: true
  },
  taskTitle: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:visible', 'success'])

// State
const loading = ref(false)
const error = ref(null)
const result = ref(null)
const numSteps = ref(5)

// Computed
const dialogTitle = computed(() => {
  if (result.value) return 'Task Breakdown Complete'
  if (loading.value) return 'Generating Breakdown...'
  return ' AI Task Breakdown'
})

const loadingMessage = computed(() => {
  return 'Analyzing your task and generating actionable subtasks...'
})

// Methods
const generateBreakdown = async () => {
  loading.value = true
  error.value = null
  
  try {
    const { useTaskStore } = await import('@/stores/tasks')
    const taskStore = useTaskStore()
    
    const data = await taskStore.breakdownTask(props.taskId, numSteps.value)
    result.value = data
    
    emit('success', data)
  } catch (err) {
    error.value = err.message || 'Failed to generate task breakdown. Please try again.'
    console.error('AI breakdown error:', err)
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  emit('update:visible', false)
  
  // Reset state after dialog closes
  setTimeout(() => {
    loading.value = false
    error.value = null
    result.value = null
    numSteps.value = 5
  }, 300)
}

// Watch for visibility changes to reset on open
watch(() => props.visible, (newVal) => {
  if (newVal) {
    loading.value = false
    error.value = null
    result.value = null
    numSteps.value = 5
  }
})
</script>

<style scoped>
.ai-dialog-loading {
  padding: 2rem;
  text-align: center;
}

.ai-dialog-loading p {
  color: var(--text-color-secondary);
  margin: 0;
}

.ai-dialog-error {
  padding: 1rem 0;
}

.ai-dialog-initial {
  padding: 1rem 0;
}

.ai-dialog-initial p {
  margin-bottom: 1.5rem;
  color: var(--text-color-secondary);
}

.ai-dialog-result {
  padding: 1rem 0;
}

.result-intro {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--primary-50);
  border-radius: var(--border-radius);
  border-left: 4px solid var(--primary-color);
}

.result-intro p {
  margin: 0;
  color: var(--text-color);
  font-weight: 500;
}

.subtasks-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.subtask-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background: var(--surface-ground);
  border-radius: var(--border-radius);
  transition: all 0.2s;
}

.subtask-item:hover {
  background: var(--surface-hover);
  transform: translateX(4px);
}

.subtask-number {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  font-weight: 600;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.subtask-text {
  flex: 1;
  padding-top: 0.25rem;
  color: var(--text-color);
  line-height: 1.6;
}

.result-notes {
  padding: 1rem;
  background: var(--surface-card);
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius);
  margin-top: 1rem;
}

.notes-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  color: var(--primary-color);
  font-weight: 600;
  font-size: 0.875rem;
}

.result-notes p {
  margin: 0;
  color: var(--text-color-secondary);
  line-height: 1.6;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
}

/* Responsive */
@media (max-width: 640px) {
  .subtask-item {
    padding: 0.75rem;
  }
  
  .subtask-number {
    min-width: 28px;
    height: 28px;
    font-size: 0.8rem;
  }
}
</style>
