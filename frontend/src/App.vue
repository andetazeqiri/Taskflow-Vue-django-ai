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
  border-bottom: 1px solid var(--color-border);
  background: white;
}

.wrapper {
  max-width: 1400px;
  margin: 0 auto;
}

nav {
  display: flex;
  gap: 1rem;
  align-items: center;
}

nav a {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  text-decoration: none;
  transition: background-color 0.2s;
}

nav a:hover {
  background-color: var(--color-background-soft);
}

nav a.router-link-exact-active {
  color: var(--color-button-bg);
  font-weight: 600;
}

main {
  min-height: calc(100vh - 70px);
}
</style>
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style>
