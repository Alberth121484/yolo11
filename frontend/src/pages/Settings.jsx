import { useState } from 'react'
import { Save } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Settings() {
  const [settings, setSettings] = useState({
    apiUrl: 'http://localhost:8000',
    defaultModel: 'yolo11n.pt',
    defaultConfidence: 0.25,
    defaultIou: 0.45,
  })

  const handleSave = () => {
    localStorage.setItem('settings', JSON.stringify(settings))
    toast.success('Configuración guardada')
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Configuración</h1>
        <p className="mt-2 text-gray-600">Ajusta la configuración del sistema</p>
      </div>

      <div className="card max-w-2xl">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">General</h2>
        <div className="space-y-4">
          <div>
            <label className="label">URL de la API</label>
            <input type="text" value={settings.apiUrl} onChange={(e) => setSettings({ ...settings, apiUrl: e.target.value })} className="input" />
          </div>
          <div>
            <label className="label">Modelo por defecto</label>
            <select value={settings.defaultModel} onChange={(e) => setSettings({ ...settings, defaultModel: e.target.value })} className="input">
              <option value="yolo11n.pt">YOLO11n</option>
              <option value="yolo11s.pt">YOLO11s</option>
              <option value="yolo11m.pt">YOLO11m</option>
            </select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Confidence por defecto</label>
              <input type="number" min="0" max="1" step="0.05" value={settings.defaultConfidence} onChange={(e) => setSettings({ ...settings, defaultConfidence: parseFloat(e.target.value) })} className="input" />
            </div>
            <div>
              <label className="label">IoU por defecto</label>
              <input type="number" min="0" max="1" step="0.05" value={settings.defaultIou} onChange={(e) => setSettings({ ...settings, defaultIou: parseFloat(e.target.value) })} className="input" />
            </div>
          </div>
        </div>
        <div className="mt-6">
          <button onClick={handleSave} className="btn btn-primary flex items-center">
            <Save className="h-5 w-5 mr-2" />
            Guardar Cambios
          </button>
        </div>
      </div>
    </div>
  )
}
