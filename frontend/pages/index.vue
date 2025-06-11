<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <header class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-slate-800 dark:text-white">
              Clip Marker
            </h1>
            <p class="text-slate-600 dark:text-slate-400 mt-1">
              專業影片片段標記工具 - Electron 版本
            </p>
          </div>
          
          <div class="flex items-center space-x-4">
            <!-- Session Info -->
            <div class="text-sm text-slate-600 dark:text-slate-400">
              會話 ID: {{ appStore.sessionId.slice(-8) }}
            </div>
            
            <!-- Dark Mode Toggle -->
            <button
              @click="appStore.toggleDarkMode()"
              class="p-2 rounded-lg bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors"
            >
              <svg v-if="appStore.isDarkMode" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd" />
              </svg>
              <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left Column: Controls -->
        <div class="lg:col-span-1 space-y-6">
          <!-- Timestamp Input -->
          <div class="card p-6">
            <h2 class="text-lg font-semibold text-slate-800 dark:text-white mb-4">
              時間戳記設定
            </h2>
            
            <div class="space-y-4">
              <!-- Start Time -->
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  開始時間
                </label>
                <div class="flex space-x-2">
                  <input
                    v-model="appStore.startTime"
                    type="text"
                    placeholder="HH:MM:SS"
                    class="input-field flex-1"
                    @blur="appStore.validateTimes()"
                  />
                  <button
                    @click="appStore.fetchStartTime()"
                    class="btn-primary px-3 py-2 text-sm"
                    :disabled="appStore.isLoading"
                  >
                    獲取
                  </button>
                </div>
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  快捷鍵: Ctrl+S
                </p>
              </div>

              <!-- End Time -->
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  結束時間
                </label>
                <div class="flex space-x-2">
                  <input
                    v-model="appStore.endTime"
                    type="text"
                    placeholder="HH:MM:SS"
                    class="input-field flex-1"
                    @blur="appStore.validateTimes()"
                  />
                  <button
                    @click="appStore.fetchEndTime()"
                    class="btn-primary px-3 py-2 text-sm"
                    :disabled="appStore.isLoading"
                  >
                    獲取
                  </button>
                </div>
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  快捷鍵: Ctrl+D
                </p>
              </div>

              <!-- Clip Name -->
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  片段名稱 (可選)
                </label>
                <input
                  v-model="appStore.clipName"
                  type="text"
                  placeholder="自訂片段名稱"
                  class="input-field"
                />
              </div>

              <!-- Add Clip Button -->
              <button
                @click="handleAddClip()"
                :disabled="!appStore.canAddClip || appStore.isLoading"
                class="btn-primary w-full"
              >
                <span v-if="appStore.isLoading">處理中...</span>
                <span v-else>新增片段 (+++)</span>
              </button>
              <p class="text-xs text-slate-500 dark:text-slate-400 text-center">
                快捷鍵: Ctrl+N
              </p>
            </div>
          </div>

          <!-- Settings -->
          <div class="card p-6">
            <h2 class="text-lg font-semibold text-slate-800 dark:text-white mb-4">
              設定
            </h2>
            
            <div class="space-y-4">
              <!-- Basename -->
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  基礎名稱
                </label>
                <input
                  v-model="appStore.basename"
                  type="text"
                  class="input-field"
                  @input="appStore.updateBasename(appStore.basename)"
                />
              </div>

              <!-- Output Folder -->
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  輸出資料夾
                </label>
                <div class="flex space-x-2">
                  <input
                    v-model="appStore.outputFolder"
                    type="text"
                    placeholder="選擇輸出資料夾"
                    class="input-field flex-1"
                    readonly
                  />
                  <button
                    @click="selectOutputFolder()"
                    class="btn-secondary px-3 py-2 text-sm"
                  >
                    瀏覽
                  </button>
                </div>
              </div>

              <!-- Export & Clip Buttons -->
              <div class="space-y-2">
                <button
                  @click="appStore.exportClips()"
                  :disabled="!appStore.hasClips || appStore.isLoading"
                  class="btn-secondary w-full"
                >
                  匯出片段清單
                </button>
                
                <button
                  @click="appStore.startClipping()"
                  :disabled="!appStore.hasClips || !appStore.outputFolder || appStore.isLoading"
                  class="btn-primary w-full"
                >
                  開始剪輯影片
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Clips List -->
        <div class="lg:col-span-2">
          <div class="card p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-slate-800 dark:text-white">
                片段清單
                <span class="text-sm font-normal text-slate-500 dark:text-slate-400">
                  ({{ appStore.clipCount }} 個片段)
                </span>
              </h2>
              
              <button
                @click="appStore.createNewSession()"
                class="btn-secondary text-sm"
                :disabled="appStore.isLoading"
              >
                清除全部
              </button>
            </div>

            <!-- Clips List -->
            <div v-if="appStore.hasClips" class="space-y-3 max-h-96 overflow-y-auto">
              <div
                v-for="(clip, index) in appStore.clips"
                :key="index"
                class="bg-slate-50 dark:bg-slate-700 rounded-lg p-4 border border-slate-200 dark:border-slate-600"
              >
                <div class="flex items-center justify-between">
                  <div class="flex-1">
                    <h3 class="font-medium text-slate-800 dark:text-white">
                      {{ clip.custom_name }}
                    </h3>
                    <p class="text-sm text-slate-600 dark:text-slate-400">
                      {{ clip.start_time }} - {{ clip.end_time }}
                    </p>
                    <p v-if="clip.path" class="text-xs text-slate-500 dark:text-slate-500 mt-1 truncate">
                      {{ clip.path }}
                    </p>
                  </div>
                  
                  <div class="flex items-center space-x-2 ml-4">
                    <button
                      @click="editClip(index)"
                      class="p-2 text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                      title="編輯名稱"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    
                    <button
                      @click="removeClip(index)"
                      class="p-2 text-slate-600 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                      title="刪除片段"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-else class="text-center py-12">
              <svg class="w-16 h-16 text-slate-400 dark:text-slate-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2h4a1 1 0 110 2h-1v12a2 2 0 01-2 2H6a2 2 0 01-2-2V6H3a1 1 0 110-2h4zM6 6v12h12V6H6z" />
              </svg>
              <h3 class="text-lg font-medium text-slate-800 dark:text-white mb-2">
                尚未新增任何片段
              </h3>
              <p class="text-slate-600 dark:text-slate-400">
                請先設定開始和結束時間，然後點擊「新增片段」按鈕
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Status Bar -->
      <div class="mt-8 flex items-center justify-between text-sm text-slate-600 dark:text-slate-400">
        <div class="flex items-center space-x-4">
          <span>MPC-HC 連接狀態: 
            <span class="text-green-600 dark:text-green-400">已連接</span>
          </span>
          <span>Flask 後端: 
            <span class="text-green-600 dark:text-green-400">運行中</span>
          </span>
        </div>
        
        <div>
          Nuxt3 + Electron + Flask 架構 v1.0.0
        </div>
      </div>
    </div>

    <!-- Add Clip Dialog -->
    <div
      v-if="showAddDialog"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="showAddDialog = false"
    >
      <div
        class="bg-white dark:bg-slate-800 rounded-lg p-6 w-96 max-w-full mx-4"
        @click.stop
      >
        <h3 class="text-lg font-semibold text-slate-800 dark:text-white mb-4">
          新增片段
        </h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              片段名稱
            </label>
            <input
              v-model="customClipName"
              type="text"
              placeholder="輸入自訂名稱"
              class="input-field"
              @keyup.enter="confirmAddClip()"
            />
          </div>
        </div>
        
        <div class="flex justify-end space-x-3 mt-6">
          <button
            @click="showAddDialog = false"
            class="btn-secondary"
          >
            取消
          </button>
          <button
            @click="confirmAddClip()"
            class="btn-primary"
          >
            確認新增
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAppStore } from '~/stores/app'

// Store
const appStore = useAppStore()

// Local state
const showAddDialog = ref(false)
const customClipName = ref('')

// Lifecycle
onMounted(() => {
  // App already initialized in app.vue
})

// Methods
function handleAddClip() {
  if (!appStore.canAddClip) {
    appStore.showMessage('請先設定開始和結束時間')
    return
  }
  
  showAddDialog.value = true
  customClipName.value = ''
}

function confirmAddClip() {
  appStore.addClip(customClipName.value || null)
  showAddDialog.value = false
  customClipName.value = ''
}

function editClip(index) {
  const clip = appStore.clips[index]
  const newName = prompt('輸入新的片段名稱:', clip.custom_name)
  
  if (newName && newName !== clip.custom_name) {
    appStore.updateClip(index, newName)
  }
}

function removeClip(index) {
  if (confirm('確定要刪除這個片段嗎？')) {
    appStore.removeClip(index)
  }
}

async function selectOutputFolder() {
  if (process.client && window.electronAPI) {
    try {
      const result = await window.electronAPI.showOpenDialog({
        properties: ['openDirectory'],
        title: '選擇輸出資料夾'
      })
      
      if (!result.canceled && result.filePaths.length > 0) {
        appStore.updateOutputFolder(result.filePaths[0])
      }
    } catch (error) {
      console.error('Failed to select folder:', error)
      appStore.showMessage('選擇資料夾失敗')
    }
  } else {
    // Fallback for web version
    appStore.showMessage('請手動輸入資料夾路徑')
  }
}

// Meta
useHead({
  title: 'Clip Marker - 影片片段標記工具'
})
</script>

<style scoped>
/* Component specific styles */
.clip-item {
  transition: all 0.2s ease;
}

.clip-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

[data-theme="dark"] .clip-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
</style> 