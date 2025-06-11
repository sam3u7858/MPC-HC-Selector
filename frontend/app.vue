<template>
  <div id="app" :data-theme="isDarkMode ? 'dark' : 'light'" class="min-h-screen bg-slate-50 dark:bg-slate-900 transition-colors duration-300 select-none">
    <NuxtPage />
    
    <!-- Floating Message Component -->
    <Transition name="fade">
      <div v-if="showFloatingMessage" class="floating-message">
        {{ floatingMessageText }}
      </div>
    </Transition>

    <!-- Name Clip Modal -->
    <div v-if="isNameModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-slate-800 p-6 rounded w-80 shadow-lg">
        <h3 class="text-lg font-medium mb-4 text-center">輸入片段名稱</h3>
        <input ref="nameInput" v-model="tempClipName" class="w-full border rounded px-3 py-2 mb-4 text-black" placeholder="留空 → 自動命名" @keyup.enter="confirmName" />
        <div class="flex justify-end space-x-2">
          <button class="px-3 py-1 bg-gray-300 rounded" @click="closeNameModal">取消</button>
          <button class="px-3 py-1 bg-blue-600 text-white rounded" @click="confirmName">確定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAppStore } from '~/stores/app'
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'

// Store
const appStore = useAppStore()

// Computed
const isDarkMode = computed(() => appStore.isDarkMode)
const showFloatingMessage = computed(() => appStore.showFloatingMessage)
const floatingMessageText = computed(() => appStore.floatingMessageText)

// modal state
const isNameModal = ref(false)
const tempClipName = ref('')
const nameInput = ref(null)

function openNameModal() {
  tempClipName.value = ''
  isNameModal.value = true
  nextTick(() => {
    nameInput.value?.focus()
  })
}
function closeNameModal() {
  isNameModal.value = false
}
async function confirmName() {
  const name = tempClipName.value.trim() || null
  isNameModal.value = false
  await appStore.addClip(name)
}

// Lifecycle
onMounted(() => {
  // Initialize app
  appStore.initialize()
  
  // Setup keyboard shortcuts
  setupKeyboardShortcuts()
  
  // Setup Electron menu listeners if in Electron environment
  if (process.client) {
    // Wait a bit for electronAPI to be available
    nextTick(() => {
      if (window.electronAPI) {
        setupElectronMenuListeners()
      } else {
        console.log('electronAPI not available, retrying...')
        setTimeout(() => {
          if (window.electronAPI) {
            setupElectronMenuListeners()
          }
        }, 100)
      }
    })
  }
})

function setupKeyboardShortcuts() {
  if (!process.client) return
  
  const handleKeydown = (event) => {
    // Ctrl+N or Cmd+N - New clip
    if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
      event.preventDefault()
      openNameModal()
    }
    
    // Ctrl+S or Cmd+S - Get start time
    if ((event.ctrlKey || event.metaKey) && event.key === 's') {
      event.preventDefault()
      appStore.fetchStartTime()
    }
    
    // Ctrl+D or Cmd+D - Get end time
    if ((event.ctrlKey || event.metaKey) && event.key === 'd') {
      event.preventDefault()
      appStore.fetchEndTime()
    }
    
    // Ctrl+E or Cmd+E - Export clips
    if ((event.ctrlKey || event.metaKey) && event.key === 'e') {
      event.preventDefault()
      appStore.exportClips()
    }
  }
  
  document.addEventListener('keydown', handleKeydown)
  
  // Cleanup on unmount
  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown)
  })
}

function setupElectronMenuListeners() {
  if (!window.electronAPI) {
    console.log('*** FRONTEND: electronAPI not available')
    return
  }
  
  console.log('*** FRONTEND: Setting up Electron listeners')
  
  // Handle menu actions
  window.electronAPI.onMenuAction((event, action) => {
    console.log('*** FRONTEND: Menu action received:', action)
    switch (action) {
      case 'menu-new-project':
        appStore.createNewSession()
        break
      case 'menu-open-project':
        appStore.showOpenProjectDialog()
        break
      case 'menu-save-project':
        appStore.saveProject()
        break
      case 'menu-export-clips':
        appStore.exportClips()
        break
      case 'menu-fetch-timestamp':
        appStore.fetchCurrentTimestamp()
        break
      case 'menu-add-clip':
        openNameModal()
        break
      case 'menu-settings':
        appStore.showSettingsDialog()
        break
      case 'name-clip':
        console.log('*** FRONTEND: Open name modal')
        openNameModal()
        break
      case 'quick-add-clip':
        console.log('*** FRONTEND: Quick add clip')
        appStore.addClip()
        break
    }
  })
  
  // Handle global shortcuts  
  console.log('*** FRONTEND: Setting up global shortcut listener')
  window.electronAPI.onGlobalShortcut((action) => {
    console.log('*** FRONTEND: Global shortcut event received with action:', action)
    
    // Show floating message for global shortcut activation
    const messages = {
      'get-start-time': '獲取開始時間 (全域快捷鍵)',
      'get-end-time': '獲取結束時間 (全域快捷鍵)',
      'name-clip': '命名並新增片段 (全域快捷鍵)',
      'quick-add-clip': '快速新增片段 (全域快捷鍵)',
      'export-clips': '匯出片段 (全域快捷鍵)'
    }
    
    if (messages[action]) {
      appStore.showMessage(messages[action])
    }
    
    // Execute the corresponding action
    console.log('*** FRONTEND: Executing action:', action)
    switch (action) {
      case 'get-start-time':
        console.log('*** FRONTEND: Calling fetchStartTime')
        appStore.fetchStartTime()
        break
      case 'get-end-time':
        console.log('*** FRONTEND: Calling fetchEndTime')
        appStore.fetchEndTime()
        break
      case 'name-clip':
        console.log('*** FRONTEND: Open name modal')
        openNameModal()
        break
      case 'quick-add-clip':
        console.log('*** FRONTEND: Quick add clip')
        appStore.addClip()
        break
      case 'export-clips':
        console.log('*** FRONTEND: Calling exportClips')
        appStore.exportClips()
        break
      default:
        console.log('*** FRONTEND: Unknown action:', action)
    }
  })
  
  console.log('*** FRONTEND: All Electron listeners set up successfully')
  
  // Cleanup on unmount
  onUnmounted(() => {
    console.log('*** FRONTEND: Cleaning up Electron listeners')
    if (window.electronAPI) {
      window.electronAPI.removeMenuListeners()
    }
  })
}

// Meta tags
useHead({
  title: 'Clip Marker',
  meta: [
    { name: 'description', content: 'Professional video clip marking tool with Electron and Nuxt3' }
  ]
})
</script>

<style>
html {
  font-family: 'Noto Sans TC', 'Microsoft JhengHei', Arial, sans-serif;
}

/* Disable text selection for better app-like experience */
.select-none {
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

/* Custom scrollbar for webkit browsers */
* {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f1f5f9;
}

[data-theme="dark"] * {
  scrollbar-color: #475569 #334155;
}
</style> 