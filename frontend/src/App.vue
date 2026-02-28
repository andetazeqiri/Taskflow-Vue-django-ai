<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import Button from 'primevue/button'

const authStore = useAuthStore()
</script>

<template>
  <div>
    <header v-if="authStore.isAuthenticated">
      <div class="wrapper">
        <div class="flex justify-between items-center w-full px-6 py-4">
          <h1 class="text-2xl font-bold">Taskflow</h1>
          <nav class="flex gap-4 items-center">
            <RouterLink to="/">Home</RouterLink>
            <RouterLink to="/tasks">Tasks</RouterLink>
            <RouterLink to="/about">About</RouterLink>
            <Button
              label="Logout"
              icon="pi pi-sign-out"
              @click="authStore.logout()"
              class="p-button-text"
              severity="secondary"
            />
          </nav>
        </div>
      </div>
    </header>

    <main>
      <Toast />
      <ConfirmDialog group="postion" />
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
header {
  background: var(--surface-card);
  border-bottom: 1px solid var(--surface-border);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
}

.wrapper {
  max-width: 1400px;
  margin: 0 auto;
}

.flex {
  display: flex;
}

.justify-between {
  justify-content: space-between;
}

.items-center {
  align-items: center;
}

.w-full {
  width: 100%;
}

.px-6 {
  padding-left: 1.5rem;
  padding-right: 1.5rem;
}

.py-4 {
  padding-top: 1rem;
  padding-bottom: 1rem;
}

.gap-4 {
  gap: 1rem;
}

header h1 {
  color: var(--primary-color);
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
}

.text-2xl {
  font-size: 1.5rem;
  line-height: 2rem;
}

.font-bold {
  font-weight: 700;
}

nav {
  display: flex;
  gap: 1rem;
  align-items: center;
}

nav a {
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius);
  text-decoration: none;
  color: var(--text-color);
  transition: all 0.2s ease;
  font-weight: 500;
}

nav a:hover {
  background-color: var(--surface-ground);
  color: var(--primary-color);
}

nav a.router-link-exact-active {
  color: var(--primary-color);
  background-color: var(--primary-50);
  font-weight: 600;
}

:deep(.p-button-text) {
  color: var(--text-color);
}

:deep(.p-button-text:hover) {
  background: var(--surface-ground);
}

main {
  min-height: calc(100vh - 70px);
}
</style>

