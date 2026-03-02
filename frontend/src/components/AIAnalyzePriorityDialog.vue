<template>
  <Dialog
    :visible="visible"
    modal
    header=" Analyze Task Priority"
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
        <p class="text-center">Analyzing task priority...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="ai-dialog-error">
      <Message severity="error" :closable="false">
        {{ error }}
      </Message>
    </div>

    <!-- Results State -->
    <div v-else-if="result && result.priority" class="ai-dialog-result">
      <div class="result-intro">
        <i class="pi pi-star-fill" style="color: var(--primary-color); font-size: 1.5rem"></i>
        <p>AI Priority Analysis:</p>
      </div>

      <div class="priority-card">
        <div class="priority-level">
          <span class="priority-label">Priority</span>
          <Tag
            :value="formatPriority(result.priority)"
            :severity="getPrioritySeverity(result.priority)"
            :rounded="true"
            style="font-size: 1.1rem; padding: 0.5rem 1rem"
          />
        </div>

        <div class="reasoning-section">
          <div class="reasoning-header">
            <i class="pi pi-info-circle"></i>
            <span>Reasoning</span>
          </div>
          <p class="reasoning-text">{{ result.reasoning }}</p>
        </div>
      </div>
    </div>

    <!-- Initial State -->
    <div v-else class="ai-dialog-initial">
      <p>Get AI-powered priority recommendations based on task details, description, and due date.</p>
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
          label="Analyze Priority"
          icon="pi pi-sparkles"
          @click="analyze"
          :loading="loading"
          :disabled="loading"
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
import Tag from 'primevue/tag'
import ProgressSpinner from 'primevue/progressspinner'

const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  },
  taskTitle: {
    type: String,
    required: true
  },
  taskDescription: {
    type: String,
    default: ''
  },
  taskDueDate: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['update:visible', 'analyzed'])

const loading = ref(false)
const error = ref(null)
const result = ref(null)

const handleClose = () => {
  emit('update:visible', false)
  setTimeout(() => {
    result.value = null
    error.value = null
  }, 300)
}

const analyze = async () => {
  loading.value = true
  error.value = null

  try {
    const { useTaskStore } = await import('@/stores/tasks')
    const taskStore = useTaskStore()

    const data = await taskStore.analyzeTaskPriority(
      props.taskTitle,
      props.taskDescription,
      props.taskDueDate
    )
    result.value = data
    emit('analyzed', data)
  } catch (err) {
    error.value = err.message || 'Failed to analyze priority. Please try again.'
  } finally {
    loading.value = false
  }
}

const formatPriority = (priority) => {
  const map = {
    low: 'Low',
    medium: 'Medium',
    high: 'High',
    critical: 'Critical'
  }
  return map[priority] || priority
}

const getPrioritySeverity = (priority) => {
  const severities = {
    low: 'info',
    medium: 'warning',
    high: 'danger',
    critical: 'danger'
  }
  return severities[priority] || 'info'
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

.justify-content-end {
  justify-content: flex-end;
}

.gap-2 {
  gap: 0.5rem;
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
  font-size: 1.1rem;
}

.priority-card {
  background: var(--surface-ground);
  border-radius: var(--border-radius);
  padding: 1.5rem;
  border: 1px solid var(--surface-border);
}

.priority-level {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--surface-border);
}

.priority-label {
  font-weight: 600;
  color: var(--text-color);
  font-size: 1rem;
}

.reasoning-section {
  margin-top: 1rem;
}

.reasoning-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  color: var(--text-color);
  font-weight: 600;
}

.reasoning-header i {
  color: var(--primary-color);
}

.reasoning-text {
  margin: 0;
  color: var(--text-color);
  line-height: 1.6;
  font-size: 0.95rem;
}
</style>
