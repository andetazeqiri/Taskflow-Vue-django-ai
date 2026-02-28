<template>
  <div class="login-container">
    <div class="login-card">
      <div class="text-center mb-6">
        <h1 class="text-4xl font-bold mb-2">Taskflow</h1>
        <p class="text-gray-600">Task Management System</p>
      </div>

      <!-- Error Message -->
      <Message v-if="authStore.error" severity="error" :closable="false" class="mb-4">
        {{ authStore.error }}
      </Message>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="space-y-6">
        <FloatLabel>
          <InputText
            id="username"
            v-model="formData.username"
            class="w-full"
            :disabled="authStore.loading"
            autocomplete="username"
          />
          <label for="username">Username</label>
        </FloatLabel>

        <FloatLabel>
          <Password
            id="password"
            v-model="formData.password"
            class="w-full"
            :feedback="false"
            :disabled="authStore.loading"
            toggleMask
            autocomplete="current-password"
          />
          <label for="password">Password</label>
        </FloatLabel>

        <Button
          type="submit"
          label="Login"
          icon="pi pi-sign-in"
          class="w-full"
          :loading="authStore.loading"
          :disabled="authStore.loading"
        >
          <template #loadingicon>
            <i class="pi pi-spin pi-spinner" />
          </template>
        </Button>
      </form>

      <!-- Register Link -->
      <div class="text-center mt-6">
        <p class="text-sm text-gray-600">
          Don't have an account?
          <button
            type="button"
            @click="showRegister = true"
            class="text-blue-600 hover:underline font-medium"
            :disabled="authStore.loading"
          >
            Register
          </button>
        </p>
      </div>
    </div>

    <!-- Register Dialog -->
    <Dialog
      v-model:visible="showRegister"
      header="Create Account"
      :modal="true"
      :style="{ width: '450px' }"
      :closable="!authStore.loading"
      :dismissableMask="!authStore.loading"
    >
      <Message v-if="authStore.error" severity="error" :closable="false" class="mb-4">
        {{ authStore.error }}
      </Message>

      <form @submit.prevent="handleRegister" class="space-y-6">
        <FloatLabel>
          <InputText
            id="reg-username"
            v-model="registerData.username"
            class="w-full"
            :disabled="authStore.loading"
            autocomplete="username"
          />
          <label for="reg-username">Username</label>
        </FloatLabel>

        <FloatLabel>
          <InputText
            id="reg-email"
            v-model="registerData.email"
            type="email"
            class="w-full"
            :disabled="authStore.loading"
            autocomplete="email"
          />
          <label for="reg-email">Email</label>
        </FloatLabel>

        <FloatLabel>
          <Password
            id="reg-password"
            v-model="registerData.password"
            class="w-full"
            toggleMask
            :disabled="authStore.loading"
            autocomplete="new-password"
          />
          <label for="reg-password">Password</label>
        </FloatLabel>

        <Button
          type="submit"
          label="Register"
          icon="pi pi-user-plus"
          class="w-full"
          :loading="authStore.loading"
          :disabled="authStore.loading"
        >
          <template #loadingicon>
            <i class="pi pi-spin pi-spinner" />
          </template>
        </Button>
      </form>

      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times"
          @click="showRegister = false" 
          text 
          :disabled="authStore.loading"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'primevue/usetoast'

import FloatLabel from 'primevue/floatlabel'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import Dialog from 'primevue/dialog'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const showRegister = ref(false)

const formData = ref({
  username: '',
  password: ''
})

const registerData = ref({
  username: '',
  email: '',
  password: ''
})

const handleLogin = async () => {
  if (!formData.value.username || !formData.value.password) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'Please enter username and password',
      life: 3000
    })
    return
  }

  const success = await authStore.login(formData.value.username, formData.value.password)
  if (success) {
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Logged in successfully',
      life: 3000
    })
    router.push('/tasks')
  } else {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: authStore.error,
      life: 3000
    })
  }
}

const handleRegister = async () => {
  if (!registerData.value.username || !registerData.value.email || !registerData.value.password) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'All fields are required',
      life: 3000
    })
    return
  }

  const success = await authStore.register(
    registerData.value.username,
    registerData.value.password,
    registerData.value.email
  )

  if (success) {
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Registered successfully. You can now login.',
      life: 3000
    })
    showRegister.value = false
    registerData.value = { username: '', email: '', password: '' }
  } else {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: authStore.error,
      life: 3000
    })
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-600) 100%);
  padding: 1rem;
}

.login-card {
  background: var(--surface-card);
  border-radius: var(--border-radius-lg);
  padding: 2.5rem;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  border: 1px solid var(--surface-border);
}

.login-card h1 {
  color: var(--text-color);
  margin: 0;
}

.login-card p {
  color: var(--text-color-secondary);
  margin: 0.5rem 0 0 0;
}

.text-center {
  text-align: center;
}

.mb-6 {
  margin-bottom: 1.5rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mt-6 {
  margin-top: 1.5rem;
}

.text-4xl {
  font-size: 2.25rem;
  line-height: 2.5rem;
}

.text-sm {
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.font-bold {
  font-weight: 700;
}

.font-medium {
  font-weight: 500;
}

.w-full {
  width: 100%;
}

.text-blue-600 {
  color: var(--primary-color);
}

.text-blue-600:hover {
  color: var(--primary-700);
}

.hover\:underline:hover {
  text-decoration: underline;
}

.space-y-6 > * + * {
  margin-top: 1.5rem;
}

.space-y-4 > * + * {
  margin-top: 1rem;
}

/* Float Label styling */
:deep(.p-floatlabel > label) {
  color: var(--text-color-secondary);
  font-weight: var(--font-weight-medium);
}

:deep(.p-floatlabel > .p-inputtext:focus ~ label,
.p-floatlabel > .p-password:focus ~ label,
.p-floatlabel > .p-inputtext.ng-filled ~ label,
.p-floatlabel > .p-password.ng-filled ~ label) {
  color: var(--primary-color);
}

/* Input styling */
:deep(.p-inputtext,
.p-password > input) {
  background: var(--surface-ground);
  border-color: var(--surface-border);
  color: var(--text-color);
  padding: 0.75rem;
  border-radius: var(--border-radius);
}

:deep(.p-inputtext:focus,
.p-password > input:focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 0.2rem rgba(var(--primary-color-rgb), 0.2);
}

/* Button styling */
:deep(.p-button) {
  padding: 0.875rem 1rem;
  font-weight: var(--font-weight-medium);
  border-radius: var(--border-radius);
}

/* Message styling */
:deep(.p-message) {
  background: var(--surface-50);
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius);
}

:deep(.p-message.p-message-error) {
  background: rgba(var(--red-500-rgb), 0.1);
  border-color: var(--red-500);
}

:deep(.p-message.p-message-error .p-message-text) {
  color: var(--red-700);
}

/* Dialog styling */
:deep(.p-dialog .p-dialog-header) {
  background: var(--surface-card);
  border-bottom: 1px solid var(--surface-border);
  padding: 1.5rem;
}

:deep(.p-dialog .p-dialog-content) {
  background: var(--surface-card);
  padding: 1.5rem;
}

:deep(.p-dialog .p-dialog-footer) {
  background: var(--surface-card);
  border-top: 1px solid var(--surface-border);
  padding: 1.5rem;
}

@media (max-width: 640px) {
  .login-card {
    padding: 2rem;
    max-width: 100%;
  }

  .text-4xl {
    font-size: 1.875rem;
    line-height: 2.25rem;
  }
}
</style>

