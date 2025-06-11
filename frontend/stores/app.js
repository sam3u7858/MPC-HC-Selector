import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', () => {
  // State
  const sessionId = ref('')
  const clips = ref([])
  const currentTimestamp = ref('')
  const startTime = ref('')
  const endTime = ref('')
  const clipName = ref('')
  const basename = ref('default_basename')
  const outputFolder = ref('')
  const isDarkMode = ref(false)
  const isLoading = ref(false)
  const showFloatingMessage = ref(false)
  const floatingMessageText = ref('')

  // API configuration
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  // Computed
  const clipCount = computed(() => clips.value.length)
  const hasClips = computed(() => clips.value.length > 0)
  const canAddClip = computed(() => startTime.value && endTime.value)

  // Actions
  async function initialize() {
    // Load settings from localStorage
    loadSettings()
    
    // Create new session
    await createNewSession()
    
    // Check Flask backend connection
    await checkBackendHealth()
  }

  function loadSettings() {
    if (process.client) {
      const settings = localStorage.getItem('clipMarkerSettings')
      if (settings) {
        const parsed = JSON.parse(settings)
        isDarkMode.value = parsed.isDarkMode || false
        basename.value = parsed.basename || 'default_basename'
        outputFolder.value = parsed.outputFolder || ''
      }
    }
  }

  function saveSettings() {
    if (process.client) {
      const settings = {
        isDarkMode: isDarkMode.value,
        basename: basename.value,
        outputFolder: outputFolder.value
      }
      localStorage.setItem('clipMarkerSettings', JSON.stringify(settings))
    }
  }

  async function checkBackendHealth() {
    try {
      const response = await $fetch(`${apiBase}/api/health`)
      console.log('Backend health check:', response)
    } catch (error) {
      console.error('Backend health check failed:', error)
      showMessage('後端服務連接失敗')
    }
  }

  async function createNewSession() {
    try {
      isLoading.value = true
      const response = await $fetch(`${apiBase}/api/session/new`, {
        method: 'POST'
      })
      
      if (response.success) {
        sessionId.value = response.session_id
        clips.value = []
        showMessage('新會話已創建')
      }
    } catch (error) {
      console.error('Failed to create session:', error)
      showMessage('創建會話失敗')
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCurrentTimestamp() {
    try {
      const response = await $fetch(`${apiBase}/api/mpc/timestamp`)
      
      if (response.success) {
        currentTimestamp.value = response.data.current_position
        showMessage('已獲取當前時間戳記')
        return response.data
      } else {
        throw new Error(response.error)
      }
    } catch (error) {
      console.error('Failed to fetch timestamp:', error)
      showMessage('獲取時間戳記失敗')
      throw error
    }
  }

  async function fetchStartTime() {
    try {
      const data = await fetchCurrentTimestamp()
      startTime.value = data.current_position
      showMessage('開始時間已設定')
    } catch (error) {
      // Error already handled in fetchCurrentTimestamp
    }
  }

  async function fetchEndTime() {
    try {
      const data = await fetchCurrentTimestamp()
      endTime.value = data.current_position
      showMessage('結束時間已設定')
      
      // Validate times
      validateTimes()
    } catch (error) {
      // Error already handled in fetchCurrentTimestamp
    }
  }

  function validateTimes() {
    if (!startTime.value || !endTime.value) return

    try {
      const startSeconds = timeToSeconds(startTime.value)
      const endSeconds = timeToSeconds(endTime.value)

      if (endSeconds <= startSeconds) {
        const newEndSeconds = startSeconds + 1
        endTime.value = secondsToTime(newEndSeconds)
        showMessage('結束時間已自動調整')
      }
    } catch (error) {
      showMessage('時間格式錯誤')
    }
  }

  function timeToSeconds(timeStr) {
    const parts = timeStr.split(':').map(Number)
    return parts[0] * 3600 + parts[1] * 60 + parts[2]
  }

  function secondsToTime(seconds) {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  async function addClip(customName = null) {
    if (!canAddClip.value) {
      showMessage('請先設定開始和結束時間')
      return
    }

    try {
      isLoading.value = true
      
      const clipIndex = clips.value.length + 1
      let finalName
      if (customName) {
        finalName = `${basename.value}_${clipIndex}_${customName}`
      } else {
        finalName = `${basename.value}_${clipIndex}`
      }
      
      const clipData = {
        start_time: startTime.value,
        end_time: endTime.value,
        custom_name: finalName
      }

      const response = await $fetch(`${apiBase}/api/clips/${sessionId.value}`, {
        method: 'POST',
        body: clipData
      })

      if (response.success) {
        // Refresh clips list
        await loadSession()
        
        // Clear form
        startTime.value = ''
        endTime.value = ''
        clipName.value = ''
        
        showMessage('片段已新增')
      } else {
        throw new Error(response.error)
      }
    } catch (error) {
      console.error('Failed to add clip:', error)
      showMessage('新增片段失敗')
    } finally {
      isLoading.value = false
    }
  }

  async function removeClip(index) {
    try {
      isLoading.value = true
      
      const response = await $fetch(`${apiBase}/api/clips/${sessionId.value}/${index}`, {
        method: 'DELETE'
      })

      if (response.success) {
        await loadSession()
        showMessage('片段已刪除')
      } else {
        throw new Error(response.error)
      }
    } catch (error) {
      console.error('Failed to remove clip:', error)
      showMessage('刪除片段失敗')
    } finally {
      isLoading.value = false
    }
  }

  async function updateClip(index, newName) {
    try {
      isLoading.value = true
      
      const clipData = { ...clips.value[index], custom_name: newName }
      
      const response = await $fetch(`${apiBase}/api/clips/${sessionId.value}/${index}`, {
        method: 'PUT',
        body: clipData
      })

      if (response.success) {
        await loadSession()
        showMessage('片段已更新')
      } else {
        throw new Error(response.error)
      }
    } catch (error) {
      console.error('Failed to update clip:', error)
      showMessage('更新片段失敗')
    } finally {
      isLoading.value = false
    }
  }

  async function loadSession() {
    try {
      const response = await $fetch(`${apiBase}/api/session/${sessionId.value}`)
      
      if (response.success) {
        clips.value = response.data.clips
      }
    } catch (error) {
      console.error('Failed to load session:', error)
    }
  }

  async function exportClips() {
    if (!hasClips.value) {
      showMessage('沒有片段可匯出')
      return
    }

    try {
      isLoading.value = true
      
      const response = await $fetch(`${apiBase}/api/export/${sessionId.value}`, {
        method: 'POST',
        body: {
          output_path: outputFolder.value || '.'
        }
      })

      if (response.success) {
        showMessage(`片段已匯出: ${response.filename}`)
        return response.file_path
      } else {
        throw new Error(response.error)
      }
    } catch (error) {
      console.error('Failed to export clips:', error)
      showMessage('匯出失敗')
    } finally {
      isLoading.value = false
    }
  }

  async function startClipping() {
    if (!hasClips.value) {
      showMessage('沒有片段可剪輯')
      return
    }

    if (!outputFolder.value) {
      showMessage('請選擇輸出資料夾')
      return
    }

    try {
      // First export clips
      const jsonFile = await exportClips()
      if (!jsonFile) return

      // Start clipping process
      const response = await $fetch(`${apiBase}/api/clip-videos`, {
        method: 'POST',
        body: {
          json_file: jsonFile,
          output_directory: outputFolder.value
        }
      })

      if (response.success) {
        showMessage('影片剪輯已開始')
      } else {
        throw new Error(response.error)
      }
    } catch (error) {
      console.error('Failed to start clipping:', error)
      showMessage('開始剪輯失敗')
    }
  }

  function showMessage(message, duration = 2000) {
    floatingMessageText.value = message
    showFloatingMessage.value = true
    
    setTimeout(() => {
      showFloatingMessage.value = false
    }, duration)
  }

  function toggleDarkMode() {
    isDarkMode.value = !isDarkMode.value
    saveSettings()
  }

  function updateBasename(newBasename) {
    basename.value = newBasename
    saveSettings()
  }

  function updateOutputFolder(folder) {
    outputFolder.value = folder
    saveSettings()
  }

  // Dialog actions (to be implemented by components)
  async function showAddClipDialog() {
    // Validate start / end times already set
    if (!startTime.value || !endTime.value) {
      showMessage('請先設定開始與結束時間')
      return
    }

    let name = ''
    if (process.client) {
      try {
        name = window.prompt('請輸入片段名稱（可留空自動命名）', '') || ''
      } catch (err) {
        console.warn('prompt() not supported, fallback to auto-name')
      }
    }

    await addClip(name.trim() || null)
    if (!name) {
      showMessage('已新增片段（自動命名）\n稍後可雙擊列表修改名稱')
    } else {
      showMessage('片段已新增')
    }
  }

  function showOpenProjectDialog() {
    // This will be handled by the UI components
    console.log('Show open project dialog')
  }

  function saveProject() {
    exportClips()
  }

  function showSettingsDialog() {
    // This will be handled by the UI components
    console.log('Show settings dialog')
  }

  return {
    // State
    sessionId,
    clips,
    currentTimestamp,
    startTime,
    endTime,
    clipName,
    basename,
    outputFolder,
    isDarkMode,
    isLoading,
    showFloatingMessage,
    floatingMessageText,
    
    // Computed
    clipCount,
    hasClips,
    canAddClip,
    
    // Actions
    initialize,
    loadSettings,
    saveSettings,
    createNewSession,
    fetchCurrentTimestamp,
    fetchStartTime,
    fetchEndTime,
    validateTimes,
    addClip,
    removeClip,
    updateClip,
    loadSession,
    exportClips,
    startClipping,
    showMessage,
    toggleDarkMode,
    updateBasename,
    updateOutputFolder,
    showAddClipDialog,
    showOpenProjectDialog,
    saveProject,
    showSettingsDialog
  }
}) 