<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { updateProfile, changePassword } from '@/api/auth'

const authStore = useAuthStore()

const profileForm = ref({ first_name: '', last_name: '' })
const profileError = ref('')
const profileSuccess = ref('')
const profileSaving = ref(false)

const passwordForm = ref({ old_password: '', new_password: '', confirm_password: '' })
const passwordError = ref('')
const passwordSuccess = ref('')
const passwordSaving = ref(false)

onMounted(() => {
  if (authStore.user) {
    profileForm.value = {
      first_name: authStore.user.first_name,
      last_name: authStore.user.last_name,
    }
  }
})

async function handleProfileSave() {
  profileError.value = ''
  profileSuccess.value = ''
  profileSaving.value = true
  try {
    await updateProfile(profileForm.value)
    await authStore.fetchProfile()
    profileSuccess.value = 'Profile updated successfully.'
  } catch (err) {
    const data = err.response?.data
    if (data) {
      const messages = Object.values(data).flat()
      profileError.value = messages.join(' ')
    } else {
      profileError.value = 'Failed to update profile.'
    }
  } finally {
    profileSaving.value = false
  }
}

async function handlePasswordChange() {
  passwordError.value = ''
  passwordSuccess.value = ''

  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    passwordError.value = 'New passwords do not match.'
    return
  }

  passwordSaving.value = true
  try {
    await changePassword(passwordForm.value.old_password, passwordForm.value.new_password)
    passwordSuccess.value = 'Password changed successfully.'
    passwordForm.value = { old_password: '', new_password: '', confirm_password: '' }
  } catch (err) {
    const data = err.response?.data
    if (data) {
      const messages = Object.values(data).flat().flat()
      passwordError.value = messages.join(' ')
    } else {
      passwordError.value = 'Failed to change password.'
    }
  } finally {
    passwordSaving.value = false
  }
}
</script>

<template>
  <main class="p-8 max-w-lg mx-auto">
    <h1 class="text-xl font-bold mb-1">Settings</h1>
    <p class="text-gray-500 text-sm mb-6">
      <router-link to="/dashboard" class="text-blue-500 hover:text-blue-600 no-underline">Dashboard</router-link>
      <span class="mx-2 text-gray-300">/</span>
      Manage your account
    </p>

    <div class="flex flex-col gap-6">
      <div class="bg-white p-8 rounded-lg shadow">
        <h2 class="m-0 mb-2 text-lg">Profile Information</h2>
        <p class="text-gray-500 text-sm m-0 mb-6 pb-4 border-b border-gray-200">
          {{ authStore.user?.email }}
          <span class="inline-block px-2 py-0.5 ml-2 bg-blue-50 text-blue-600 rounded-full text-xs capitalize">
            {{ authStore.user?.role }}
          </span>
        </p>

        <form @submit.prevent="handleProfileSave">
          <div class="flex gap-4">
            <div class="flex-1 mb-4">
              <label for="first_name" class="block mb-1 font-medium text-sm">First Name</label>
              <input
                id="first_name"
                v-model="profileForm.first_name"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded text-base box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
              />
            </div>
            <div class="flex-1 mb-4">
              <label for="last_name" class="block mb-1 font-medium text-sm">Last Name</label>
              <input
                id="last_name"
                v-model="profileForm.last_name"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded text-base box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
              />
            </div>
          </div>

          <p v-if="profileError" class="text-red-600 text-sm my-2">{{ profileError }}</p>
          <p v-if="profileSuccess" class="text-green-600 text-sm my-2">{{ profileSuccess }}</p>

          <button
            type="submit"
            :disabled="profileSaving"
            class="w-full py-2.5 bg-blue-500 text-white rounded text-base cursor-pointer mt-2 hover:bg-blue-600 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {{ profileSaving ? 'Saving...' : 'Save Profile' }}
          </button>
        </form>
      </div>

      <div class="bg-white p-8 rounded-lg shadow">
        <h2 class="m-0 mb-2 text-lg">Change Password</h2>

        <form @submit.prevent="handlePasswordChange">
          <div class="mb-4">
            <label for="old_password" class="block mb-1 font-medium text-sm">Current Password</label>
            <input
              id="old_password"
              v-model="passwordForm.old_password"
              type="password"
              required
              autocomplete="current-password"
              class="w-full px-3 py-2 border border-gray-300 rounded text-base box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
            />
          </div>

          <div class="mb-4">
            <label for="new_password" class="block mb-1 font-medium text-sm">New Password</label>
            <input
              id="new_password"
              v-model="passwordForm.new_password"
              type="password"
              required
              autocomplete="new-password"
              class="w-full px-3 py-2 border border-gray-300 rounded text-base box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
            />
            <small class="block mt-1 text-gray-400 text-xs">
              Min 8 characters, with uppercase, lowercase, digit, and special character.
            </small>
          </div>

          <div class="mb-4">
            <label for="confirm_password" class="block mb-1 font-medium text-sm">Confirm New Password</label>
            <input
              id="confirm_password"
              v-model="passwordForm.confirm_password"
              type="password"
              required
              autocomplete="new-password"
              class="w-full px-3 py-2 border border-gray-300 rounded text-base box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
            />
          </div>

          <p v-if="passwordError" class="text-red-600 text-sm my-2">{{ passwordError }}</p>
          <p v-if="passwordSuccess" class="text-green-600 text-sm my-2">{{ passwordSuccess }}</p>

          <button
            type="submit"
            :disabled="passwordSaving"
            class="w-full py-2.5 bg-blue-500 text-white rounded text-base cursor-pointer mt-2 hover:bg-blue-600 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {{ passwordSaving ? 'Changing...' : 'Change Password' }}
          </button>
        </form>
      </div>
    </div>
  </main>
</template>
