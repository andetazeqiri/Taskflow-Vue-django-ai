<template>
  <div class="login-container">
    <div class="login-card">
      <div class="text-center mb-6">
        <h1 class="text-4xl font-bold mb-2">Taskflow</h1>
        <p class="text-gray-600">Task Management System</p>
      </div>

      <!-- Error Alert -->
      <Message v-if="authStore.error" severity="error" :text="authStore.error" closable class="mb-4" />

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label for="username" class="block text-sm font-medium mb-2">Username</label>
          <InputText
            id="username"
            v-model="formData.username"
            placeholder="Enter your username"
            class="w-full"
            :disabled="authStore.loading"
          />
        </div>

        <div>
          <label for="password" class="block text-sm font-medium mb-2">Password</label>
          <Password
            id="password"
            v-model="formData.password"
            placeholder="Enter your password"
            class="w-full"
            :feedback="false"
            :disabled="authStore.loading"
          />
        </div>

        <Button
          type="submit"
          label="Login"
          class="w-full"
          :loading="authStore.loading"
        />
      </form>

      <!-- Register Link -->
      <div class="text-center mt-6">
        <p class="text-sm text-gray-600">
          Don't have an account?
          <button
            type="button"
            @click="showRegister = true"
            class="text-blue-600 hover:underline font-medium"
          >
            Register
          </button>
        </p>
      </div>
    </div>

    <!-- Register Dialog -->
    <Dialog
      v-model:visible="showRegister"
      header="Register"
      :modal="true"
      :style="{ width: '400px' }"
    >
      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label for="reg-username" class="block text-sm font-medium mb-2">Username</label>
          <InputText
            id="reg-username"
            v-model="registerData.username"
            placeholder="Choose a username"
            class="w-full"
          />
        </div>

        <div>
          <label for="reg-email" class="block text-sm font-medium mb-2">Email</label>
          <InputText
            id="reg-email"
            v-model="registerData.email"
            type="email"
            placeholder="Enter your email"
            class="w-full"
          />
        </div>

        <div>
          <label for="reg-password" class="block text-sm font-medium mb-2">Password</label>
          <Password
            id="reg-password"
            v-model="registerData.password"
            placeholder="Create a password"
            class="w-full"
            :feedback="false"
          />
        </div>

        <Button
          type="submit"
          label="Register"
          class="w-full"
          :loading="authStore.loading"
        />
      </form>

      <template #footer>
        <Button label="Cancel" @click="showRegister = false" class="p-button-text" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'primevue/usetoast'

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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}
</style>
