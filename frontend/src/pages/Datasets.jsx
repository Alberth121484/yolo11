import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Trash2, Upload, Eye, Tag } from 'lucide-react'
import { datasetAPI } from '@/lib/api'
import { formatDate, parseError } from '@/lib/utils'
import toast from 'react-hot-toast'

export default function Datasets() {
  const navigate = useNavigate()
  const [datasets, setDatasets] = useState([])
  const [loading, setLoading] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newDataset, setNewDataset] = useState({
    name: '',
    class_names: '',
    description: '',
  })

  useEffect(() => {
    loadDatasets()
  }, [])

  const loadDatasets = async () => {
    try {
      const { data } = await datasetAPI.list()
      setDatasets(data)
    } catch (error) {
      toast.error('Error al cargar datasets')
    }
  }

  const handleCreateDataset = async () => {
    if (!newDataset.name || !newDataset.class_names) {
      toast.error('Nombre y clases son requeridos')
      return
    }

    setLoading(true)
    try {
      const classNames = newDataset.class_names.split(',').map((c) => c.trim())
      await datasetAPI.create({
        name: newDataset.name,
        class_names: classNames,
        description: newDataset.description,
      })
      toast.success('Dataset creado')
      setShowCreateModal(false)
      setNewDataset({ name: '', class_names: '', description: '' })
      loadDatasets()
    } catch (error) {
      toast.error(parseError(error))
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteDataset = async (name) => {
    if (!confirm(`¿Eliminar dataset "${name}"?`)) return

    try {
      await datasetAPI.delete(name)
      toast.success('Dataset eliminado')
      loadDatasets()
    } catch (error) {
      toast.error(parseError(error))
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Datasets</h1>
          <p className="mt-2 text-gray-600">Gestiona tus datasets de entrenamiento</p>
        </div>
        <button onClick={() => setShowCreateModal(true)} className="btn btn-primary flex items-center">
          <Plus className="h-5 w-5 mr-2" />
          Crear Dataset
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {datasets.map((dataset) => (
          <div key={dataset.name} className="card">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">{dataset.name}</h3>
                <p className="text-sm text-gray-500 mt-1">{dataset.num_classes} clases</p>
              </div>
              <button onClick={() => handleDeleteDataset(dataset.name)} className="text-red-600 hover:text-red-800">
                <Trash2 className="h-5 w-5" />
              </button>
            </div>
            <div className="mt-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Train:</span>
                <span className="font-medium">{dataset.num_images_train} imágenes</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Val:</span>
                <span className="font-medium">{dataset.num_images_val} imágenes</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Test:</span>
                <span className="font-medium">{dataset.num_images_test} imágenes</span>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200 flex items-center justify-between">
              <p className="text-xs text-gray-500">{formatDate(dataset.created_at)}</p>
              <button
                onClick={() => navigate(`/annotate?dataset=${dataset.name}`)}
                className="flex items-center text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                <Tag className="h-4 w-4 mr-1" />
                Annotate
              </button>
            </div>
          </div>
        ))}
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold mb-6">Crear Dataset</h2>
            <div className="space-y-4">
              <div>
                <label className="label">Nombre</label>
                <input type="text" value={newDataset.name} onChange={(e) => setNewDataset({ ...newDataset, name: e.target.value })} className="input" placeholder="mi_dataset" />
              </div>
              <div>
                <label className="label">Clases (separadas por comas)</label>
                <input type="text" value={newDataset.class_names} onChange={(e) => setNewDataset({ ...newDataset, class_names: e.target.value })} className="input" placeholder="perro, gato, pajaro" />
              </div>
              <div>
                <label className="label">Descripción</label>
                <textarea value={newDataset.description} onChange={(e) => setNewDataset({ ...newDataset, description: e.target.value })} className="input" rows="3" placeholder="Descripción opcional" />
              </div>
            </div>
            <div className="mt-6 flex justify-end space-x-3">
              <button onClick={() => setShowCreateModal(false)} className="btn btn-secondary">Cancelar</button>
              <button onClick={handleCreateDataset} disabled={loading} className="btn btn-primary">
                {loading ? 'Creando...' : 'Crear'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
