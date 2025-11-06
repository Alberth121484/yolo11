import { useState, useEffect } from 'react'
import { Save, Cloud, HardDrive, CheckCircle, AlertCircle, LogOut, User } from 'lucide-react'
import { FaGoogle, FaMicrosoft } from 'react-icons/fa'
import { useAuth } from '@/context/AuthContext'
import axios from 'axios'
import toast from 'react-hot-toast'

export default function SettingsNew() {
  const { user, logout } = useAuth()
  const [activeTab, setActiveTab] = useState('general')
  const [settings, setSettings] = useState({
    apiUrl: 'http://localhost:8000',
    defaultModel: 'yolo11n.pt',
    defaultConfidence: 0.25,
    defaultIou: 0.45,
  })
  
  const [storageConfig, setStorageConfig] = useState({
    type: 'local',
    credentials: {}
  })
  
  const [testingConnection, setTestingConnection] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState(null)

  useEffect(() => {
    loadSettings()
    loadStorageConfig()
  }, [])

  const loadSettings = () => {
    const saved = localStorage.getItem('settings')
    if (saved) {
      setSettings(JSON.parse(saved))
    }
  }

  const loadStorageConfig = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get('http://localhost:8000/api/v1/config/storage', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setStorageConfig(response.data)
    } catch (error) {
      console.error('Error loading storage config:', error)
    }
  }

  const handleSaveSettings = () => {
    localStorage.setItem('settings', JSON.stringify(settings))
    toast.success('Configuración guardada')
  }

  const handleSaveStorage = async () => {
    try {
      const token = localStorage.getItem('token')
      await axios.post('http://localhost:8000/api/v1/config/storage', storageConfig, {
        headers: { Authorization: `Bearer ${token}` }
      })
      toast.success('Configuración de almacenamiento guardada')
    } catch (error) {
      toast.error('Error al guardar configuración: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleTestConnection = async () => {
    setTestingConnection(true)
    setConnectionStatus(null)
    
    try {
      const token = localStorage.getItem('token')
      const response = await axios.post('http://localhost:8000/api/v1/config/storage/test', storageConfig, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      setConnectionStatus({
        success: true,
        message: `Conexión exitosa. ${response.data.files_count} archivos encontrados.`
      })
      toast.success('Conexión exitosa')
    } catch (error) {
      setConnectionStatus({
        success: false,
        message: error.response?.data?.detail || error.message
      })
      toast.error('Error de conexión')
    } finally {
      setTestingConnection(false)
    }
  }

  const handleOAuthConnect = (provider) => {
    // Open OAuth flow in popup or new window
    const width = 500
    const height = 600
    const left = window.screenX + (window.outerWidth - width) / 2
    const top = window.screenY + (window.outerHeight - height) / 2
    
    const authWindow = window.open(
      `http://localhost:8000/api/v1/auth/login/${provider}?connect=true`,
      'OAuth',
      `width=${width},height=${height},left=${left},top=${top}`
    )
    
    // Listen for OAuth callback
    const handleMessage = (event) => {
      if (event.origin !== window.location.origin) return
      
      if (event.data.type === 'oauth-success') {
        setStorageConfig({
          ...storageConfig,
          credentials: event.data.credentials
        })
        toast.success(`Conectado a ${provider}`)
        authWindow.close()
      }
    }
    
    window.addEventListener('message', handleMessage)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Configuración</h1>
          <p className="mt-2 text-gray-600">Ajusta la configuración del sistema</p>
        </div>
        {user && (
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">{user.name}</p>
              <p className="text-xs text-gray-500">{user.email}</p>
            </div>
            {user.avatar_url && (
              <img src={user.avatar_url} alt="Avatar" className="h-10 w-10 rounded-full" />
            )}
            <button onClick={logout} className="btn btn-secondary flex items-center">
              <LogOut className="h-4 w-4 mr-2" />
              Salir
            </button>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('general')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'general'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            General
          </button>
          <button
            onClick={() => setActiveTab('storage')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'storage'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Cloud className="h-4 w-4 inline mr-2" />
            Almacenamiento
          </button>
          <button
            onClick={() => setActiveTab('account')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'account'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <User className="h-4 w-4 inline mr-2" />
            Cuenta
          </button>
        </nav>
      </div>

      {/* General Settings */}
      {activeTab === 'general' && (
        <div className="card max-w-2xl">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Configuración General</h2>
          <div className="space-y-4">
            <div>
              <label className="label">URL de la API</label>
              <input
                type="text"
                value={settings.apiUrl}
                onChange={(e) => setSettings({ ...settings, apiUrl: e.target.value })}
                className="input"
              />
            </div>
            <div>
              <label className="label">Modelo por defecto</label>
              <select
                value={settings.defaultModel}
                onChange={(e) => setSettings({ ...settings, defaultModel: e.target.value })}
                className="input"
              >
                <option value="yolo11n.pt">YOLO11n</option>
                <option value="yolo11s.pt">YOLO11s</option>
                <option value="yolo11m.pt">YOLO11m</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Confidence por defecto</label>
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.05"
                  value={settings.defaultConfidence}
                  onChange={(e) => setSettings({ ...settings, defaultConfidence: parseFloat(e.target.value) })}
                  className="input"
                />
              </div>
              <div>
                <label className="label">IoU por defecto</label>
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.05"
                  value={settings.defaultIou}
                  onChange={(e) => setSettings({ ...settings, defaultIou: parseFloat(e.target.value) })}
                  className="input"
                />
              </div>
            </div>
          </div>
          <div className="mt-6">
            <button onClick={handleSaveSettings} className="btn btn-primary flex items-center">
              <Save className="h-5 w-5 mr-2" />
              Guardar Cambios
            </button>
          </div>
        </div>
      )}

      {/* Storage Settings */}
      {activeTab === 'storage' && (
        <div className="card max-w-3xl">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Configuración de Almacenamiento</h2>
          <p className="text-sm text-gray-600 mb-6">
            Configura dónde se almacenarán tus datasets e imágenes para entrenamiento
          </p>

          {/* Storage Type Selection */}
          <div className="space-y-4">
            <label className="label">Tipo de Almacenamiento</label>
            
            {/* Local Storage */}
            <div
              className={`relative flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                storageConfig.type === 'local'
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setStorageConfig({ type: 'local', credentials: {} })}
            >
              <input
                type="radio"
                name="storage"
                value="local"
                checked={storageConfig.type === 'local'}
                onChange={() => {}}
                className="sr-only"
              />
              <HardDrive className="h-8 w-8 text-gray-600 mr-4" />
              <div className="flex-1">
                <h3 className="font-medium text-gray-900">Almacenamiento Local</h3>
                <p className="text-sm text-gray-500">Guarda archivos en tu servidor local</p>
              </div>
              {storageConfig.type === 'local' && (
                <CheckCircle className="h-5 w-5 text-primary-600" />
              )}
            </div>

            {/* Google Drive */}
            <div
              className={`relative flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                storageConfig.type === 'google_drive'
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setStorageConfig({ ...storageConfig, type: 'google_drive' })}
            >
              <input
                type="radio"
                name="storage"
                value="google_drive"
                checked={storageConfig.type === 'google_drive'}
                onChange={() => {}}
                className="sr-only"
              />
              <FaGoogle className="h-8 w-8 text-blue-600 mr-4" />
              <div className="flex-1">
                <h3 className="font-medium text-gray-900">Google Drive</h3>
                <p className="text-sm text-gray-500">Sincroniza con tu cuenta de Google Drive</p>
              </div>
              {storageConfig.type === 'google_drive' && (
                <CheckCircle className="h-5 w-5 text-primary-600" />
              )}
            </div>

            {/* OneDrive */}
            <div
              className={`relative flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                storageConfig.type === 'onedrive'
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setStorageConfig({ ...storageConfig, type: 'onedrive' })}
            >
              <input
                type="radio"
                name="storage"
                value="onedrive"
                checked={storageConfig.type === 'onedrive'}
                onChange={() => {}}
                className="sr-only"
              />
              <FaMicrosoft className="h-8 w-8 text-blue-500 mr-4" />
              <div className="flex-1">
                <h3 className="font-medium text-gray-900">Microsoft OneDrive</h3>
                <p className="text-sm text-gray-500">Sincroniza con tu cuenta de OneDrive</p>
              </div>
              {storageConfig.type === 'onedrive' && (
                <CheckCircle className="h-5 w-5 text-primary-600" />
              )}
            </div>
          </div>

          {/* Cloud Storage Configuration */}
          {storageConfig.type !== 'local' && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-3">Configuración de Credenciales</h4>
              
              {!storageConfig.credentials?.access_token ? (
                <div className="text-center py-6">
                  <p className="text-sm text-gray-600 mb-4">
                    Conecta tu cuenta para acceder a tus archivos
                  </p>
                  <button
                    onClick={() => handleOAuthConnect(storageConfig.type === 'google_drive' ? 'google' : 'microsoft')}
                    className="btn btn-primary"
                  >
                    Conectar {storageConfig.type === 'google_drive' ? 'Google Drive' : 'OneDrive'}
                  </button>
                </div>
              ) : (
                <div className="flex items-center justify-between">
                  <div className="flex items-center text-green-600">
                    <CheckCircle className="h-5 w-5 mr-2" />
                    <span className="text-sm font-medium">Conectado</span>
                  </div>
                  <button
                    onClick={() => setStorageConfig({ ...storageConfig, credentials: {} })}
                    className="text-sm text-red-600 hover:text-red-800"
                  >
                    Desconectar
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Connection Test */}
          {connectionStatus && (
            <div className={`mt-4 p-4 rounded-lg flex items-start ${
              connectionStatus.success ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
            }`}>
              {connectionStatus.success ? (
                <CheckCircle className="h-5 w-5 mr-2 flex-shrink-0 mt-0.5" />
              ) : (
                <AlertCircle className="h-5 w-5 mr-2 flex-shrink-0 mt-0.5" />
              )}
              <p className="text-sm">{connectionStatus.message}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="mt-6 flex space-x-3">
            <button
              onClick={handleTestConnection}
              disabled={testingConnection || (storageConfig.type !== 'local' && !storageConfig.credentials?.access_token)}
              className="btn btn-secondary flex items-center"
            >
              {testingConnection ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
                  Probando...
                </>
              ) : (
                <>
                  <Cloud className="h-4 w-4 mr-2" />
                  Probar Conexión
                </>
              )}
            </button>
            <button
              onClick={handleSaveStorage}
              disabled={storageConfig.type !== 'local' && !storageConfig.credentials?.access_token}
              className="btn btn-primary flex items-center"
            >
              <Save className="h-5 w-5 mr-2" />
              Guardar Configuración
            </button>
          </div>
        </div>
      )}

      {/* Account Settings */}
      {activeTab === 'account' && (
        <div className="card max-w-2xl">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Información de Cuenta</h2>
          {user ? (
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                {user.avatar_url && (
                  <img src={user.avatar_url} alt="Avatar" className="h-16 w-16 rounded-full" />
                )}
                <div>
                  <h3 className="font-medium text-gray-900">{user.name}</h3>
                  <p className="text-sm text-gray-500">{user.email}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    Conectado con {user.provider}
                  </p>
                </div>
              </div>
              <div className="pt-4 border-t border-gray-200">
                <button onClick={logout} className="btn btn-secondary flex items-center text-red-600 hover:text-red-700">
                  <LogOut className="h-4 w-4 mr-2" />
                  Cerrar Sesión
                </button>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">No has iniciado sesión</p>
          )}
        </div>
      )}
    </div>
  )
}
