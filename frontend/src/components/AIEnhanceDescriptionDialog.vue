<template>
  <Dialog
    :visible="visible"
    modal
    header=" Enhance Task Description"
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
        <p class="text-center">Enhancing your task description with AI...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="ai-dialog-error">
      <Message severity="error" :closable="false">
        {{ error }}
      </Message>
    </div>

    <!-- Results State -->
    <div v-else-if="result && result.enhanced_description" class="ai-dialog-result">
      <div class="result-intro">
        <i class="pi pi-check-circle" style="color: var(--primary-color); font-size: 1.5rem"></i>
        <p>Here's an enhanced version of your task description:</p>
      </div>

      <div class="enhanced-container">
        <div class="enhanced-box">
          <p>{{ result.enhanced_description }}</p>
        </div>
      </div>

      <div class="action-buttons">
        <Button
          label="Copy to Clipboard"
          icon="pi pi-copy"
          @click="copyToClipboard"
          outlined
          class="w-full"
        />
      </div>
    </div>

    <!-- Initial State -->
    <div v-else class="ai-dialog-initial">
      <p>Get AI-powered suggestions to improve and expand your task description with more clarity and detail.</p>
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
          label="Enhance Description"
          icon="pi pi-sparkles"
          @click="enhance"
          :loading="loading"
          :disabled="loading"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import { useToast } from 'primevue/usetoast'

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
  }
})

const emit = defineEmits(['update:visible', 'enhanced'])

const toast = useToast()
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

const enhance = async () => {
  loading.value = true
  error.value = null

  try {
    const { useTaskStore } = await import('@/stores/tasks')
    const taskStore = useTaskStore()

    const data = await taskStore.enhanceTaskDescription(
      props.taskTitle,
      props.taskDescription
    )
    result.value = data
    emit('enhanced', data)
  } catch (err) {
    error.value = err.message || 'Failed to enhance description. Please try again.'
  } finally {
    loading.value = false
  }
}

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(result.value.enhanced_description)
    toast.add({
      severity: 'success',
      summary: 'Copied',
      detail: 'Enhanced description copied to clipboard',
      life: 2000
    })
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to copy to clipboard',
      life: 2000
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

.justify-content-end {
  justify-content: flex-end;
}

.gap-2 {
  gap: 0.5rem;
}

.w-full {
  width: 100%;
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

.enhanced-container {
  margin-bottom: 1.5rem;
}

.enhanced-box {
  background: var(--surface-ground);
  border-radius: var(--border-radius);
  padding: 1.5rem;
  border: 1px solid var(--surface-border);
  line-height: 1.6;
  color: var(--text-color);
  white-space: pre-wrap;
  word-wrap: break-word;
}

.enhanced-box p {
  margin: 0;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}
</style>
