import { ref } from 'vue'
import { defineStore } from 'pinia'
import { getUsers, getUser, createUser, updateUser, deleteUser } from '@/api/users'

export const useUsersStore = defineStore('users', () => {
  const users = ref([])
  const currentUser = ref(null)
  const loading = ref(false)

  async function fetchUsers() {
    loading.value = true
    try {
      const { data } = await getUsers()
      users.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchUser(id) {
    loading.value = true
    try {
      const { data } = await getUser(id)
      currentUser.value = data
    } finally {
      loading.value = false
    }
  }

  async function addUser(data) {
    const response = await createUser(data)
    return response.data
  }

  async function editUser(id, data) {
    const response = await updateUser(id, data)
    currentUser.value = response.data
    return response.data
  }

  async function removeUser(id) {
    await deleteUser(id)
    users.value = users.value.filter((u) => u.id !== id)
    currentUser.value = null
  }

  return { users, currentUser, loading, fetchUsers, fetchUser, addUser, editUser, removeUser }
})
