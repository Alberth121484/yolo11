import { useState, useEffect } from 'react'
import { Download, Trash2, Upload } from 'lucide-react'
import { modelAPI } from '@/lib/api'
import { formatDate, formatFileSize, parseError } from '@/lib/utils'
import toast from 'react-hot-toast'

export default function Models() {
  const [models, setModels] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadModels()
  }, [])

  const loadModels = async () => {
    try {
      const { data } = await modelAPI.list()
      setModels(data)
    } catch (error) {
      toast.error('Error al cargar modelos')
    }
  }

  const handleDelete = async (name) => {
    if (!confirm(`¿Eliminar modelo "${name}"?`)) return

    try {
      await modelAPI.delete(name)
      toast.success('Modelo eliminado')
      loadModels()
    } catch (error) {
      toast.error(parseError(error))
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Modelos</h1>
        <p className="mt-2 text-gray-600">Gestiona tus modelos entrenados</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {models.map((model) => (
          <div key={model.name} className="card">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">{model.name}</h3>
                <p className="text-sm text-gray-500 mt-1">
                  {model.num_classes} clases • {formatFileSize(model.file_size_mb * 1024 * 1024)}
                </p>
              </div>
              <button onClick={() => handleDelete(model.name)} className="text-red-600 hover:text-red-800">
                <Trash2 className="h-5 w-5" />
              </button>
            </div>
            <div className="mt-4">
              <p className="text-xs text-gray-500">{formatDate(model.created_at)}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
