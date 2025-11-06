import { useState, useEffect, useRef } from 'react'
import { Play, RefreshCw, Trash2, Eye } from 'lucide-react'
import { trainingAPI, datasetAPI } from '@/lib/api'
import { formatDate, getStatusColor, parseError, calculateProgress } from '@/lib/utils'
import toast from 'react-hot-toast'

export default function Training() {
  const [datasets, setDatasets] = useState([])
  const [trainings, setTrainings] = useState([])
  const [loading, setLoading] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)
  
  // Usar ref para rastrear si ya se hizo la carga inicial
  const isInitialLoadComplete = useRef(false)
  const pollingIntervalRef = useRef(null)
  
  // Cargar jobs completados desde localStorage
  const [completedJobs, setCompletedJobs] = useState(() => {
    const saved = localStorage.getItem('completedTrainingJobs')
    return saved ? new Set(JSON.parse(saved)) : new Set()
  })
  const [config, setConfig] = useState({
    dataset_name: '',
    model_size: 'n',
    epochs: 100,
    batch_size: 16,
    imgsz: 640,
    lr0: 0.01,
    patience: 50,
    pretrained: true,
  })

  useEffect(() => {
    console.log('Training page mounted - Loading initial data...')
    
    // Hacer la carga inicial UNA SOLA VEZ
    loadData().then(() => {
      console.log('Initial load complete')
      isInitialLoadComplete.current = true
    })
    
    return () => {
      console.log('Training page unmounted - Cleaning up')
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
        pollingIntervalRef.current = null
      }
      isInitialLoadComplete.current = false
    }
  }, []) // Array vacío - solo se ejecuta UNA VEZ al montar

  const loadData = async () => {
    try {
      const [datasetsRes, trainingsRes] = await Promise.all([
        datasetAPI.list(),
        trainingAPI.listJobs({ limit: 50 }),
      ])
      setDatasets(datasetsRes.data)
      setTrainings(trainingsRes.data)
      
      // Inicializar completedJobs con los entrenamientos ya completados
      // Esto previene notificaciones de entrenamientos antiguos
      const initialCompleted = new Set(completedJobs)
      trainingsRes.data.forEach(job => {
        if (job.status === 'completed') {
          initialCompleted.add(job.job_id)
        }
      })
      setCompletedJobs(initialCompleted)
      localStorage.setItem('completedTrainingJobs', JSON.stringify([...initialCompleted]))
      
      console.log('Initial load: marked', initialCompleted.size, 'jobs as already seen')
    } catch (error) {
      console.error(error)
    }
  }

  const loadTrainings = async () => {
    try {
      const { data } = await trainingAPI.listJobs({ limit: 50 })
      
      // Detectar entrenamientos recién completados SOLO durante esta sesión
      data.forEach(job => {
        if (job.status === 'completed' && !completedJobs.has(job.job_id)) {
          // Agregar a completedJobs y guardar en localStorage
          const newCompleted = new Set(completedJobs).add(job.job_id)
          setCompletedJobs(newCompleted)
          localStorage.setItem('completedTrainingJobs', JSON.stringify([...newCompleted]))
          
          // Mostrar notificación SOLO para entrenamientos que se completaron durante esta sesión
          console.log('Training completed during session:', job.job_id)
          toast.success(
            `✅ Entrenamiento completado!\nModelo: ${job.model_name || 'best.pt'}\nmAP: ${job.best_map.toFixed(3)}`,
            { duration: 8000, icon: '🎉' }
          )
        }
      })
      
      setTrainings(data)
      
      // Verificar si hay entrenamientos activos y gestionar el polling
      const hasActiveTrainings = data.some(
        t => t.status === 'running' || t.status === 'pending'
      )
      
      if (hasActiveTrainings && !pollingIntervalRef.current) {
        // Iniciar polling si hay entrenamientos activos y no está activo
        console.log('🔄 Starting polling - Active trainings detected')
        pollingIntervalRef.current = setInterval(() => {
          loadTrainings()
        }, 2000)
      } else if (!hasActiveTrainings && pollingIntervalRef.current) {
        // Detener polling si no hay entrenamientos activos
        console.log('⏸️ Stopping polling - No active trainings')
        clearInterval(pollingIntervalRef.current)
        pollingIntervalRef.current = null
      }
    } catch (error) {
      console.error(error)
    }
  }

  const handleStartTraining = async () => {
    if (!config.dataset_name) {
      toast.error('Por favor selecciona un dataset')
      return
    }

    console.log('User initiated training with config:', config)
    setLoading(true)
    try {
      const result = await trainingAPI.startTraining(config)
      console.log('Training started successfully:', result)
      toast.success('Entrenamiento iniciado - El progreso se mostrará en tiempo real')
      setShowCreateModal(false)
      
      // Recargar inmediatamente para mostrar el nuevo job
      await loadTrainings()
    } catch (error) {
      console.error('Failed to start training:', error)
      toast.error(parseError(error))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Entrenamiento</h1>
          <p className="mt-2 text-gray-600">Entrena modelos con tus datasets</p>
        </div>
        <button onClick={() => setShowCreateModal(true)} className="btn btn-primary flex items-center">
          <Play className="h-5 w-5 mr-2" />
          Nuevo Entrenamiento
        </button>
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Entrenamientos</h2>
          <div className="flex items-center space-x-2">
            <button 
              onClick={loadTrainings} 
              className="text-sm text-gray-600 hover:text-gray-900 flex items-center px-3 py-1 rounded hover:bg-gray-100"
            >
              <RefreshCw className="h-4 w-4 mr-1" />
              Actualizar
            </button>
            {completedJobs.size > 0 && (
              <button
                onClick={() => {
                  localStorage.removeItem('completedTrainingJobs')
                  setCompletedJobs(new Set())
                  toast.success('Historial de notificaciones limpiado')
                }}
                className="text-xs text-gray-500 hover:text-gray-700 px-2 py-1 rounded hover:bg-gray-100"
                title="Limpiar historial de notificaciones"
              >
                🔔 Reset
              </button>
            )}
          </div>
        </div>

        {trainings.filter((t) => t.status === 'running' || t.status === 'pending').length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">🔄 Entrenamientos Activos</h3>
            <div className="space-y-4">
              {trainings
                .filter((t) => t.status === 'running' || t.status === 'pending')
                .map((job) => {
                  const progress = calculateProgress(job.current_epoch, job.epochs)
                  const metrics = job.current_metrics || {}
                  return (
                    <div key={job.job_id} className="border-2 border-primary-200 rounded-lg p-4 bg-gradient-to-r from-blue-50 to-white">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center">
                            <h3 className="font-semibold text-gray-900">{job.dataset_name}</h3>
                            <span className="ml-2 text-sm text-gray-500">(yolo11{job.model_size})</span>
                            <span className="ml-3 px-3 py-1 text-xs font-bold rounded-full bg-green-100 text-green-700 animate-pulse">
                              🔄 Entrenando...
                            </span>
                          </div>
                          <div className="flex items-center mt-2 space-x-4 text-sm flex-wrap">
                            <span className="text-gray-700 font-medium">
                              📊 Epoch {job.current_epoch}/{job.epochs}
                            </span>
                            <span className="text-gray-400">•</span>
                            <span className="text-green-600 font-semibold">
                              mAP: {job.best_map.toFixed(3)}
                            </span>
                            {metrics.precision !== undefined && (
                              <>
                                <span className="text-gray-400">•</span>
                                <span className="text-blue-600">Precision: {metrics.precision.toFixed(3)}</span>
                              </>
                            )}
                            {metrics.recall !== undefined && (
                              <>
                                <span className="text-gray-400">•</span>
                                <span className="text-purple-600">Recall: {metrics.recall.toFixed(3)}</span>
                              </>
                            )}
                          </div>
                        </div>
                        <button
                          onClick={() => {
                            if(confirm('¿Cancelar entrenamiento?')) {
                              trainingAPI.cancelJob(job.job_id).then(() => {
                                toast.success('Entrenamiento cancelado')
                                loadTrainings()
                              })
                            }
                          }}
                          className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg"
                          title="Cancelar"
                        >
                          <Trash2 className="h-5 w-5" />
                        </button>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-gray-600 font-medium">Progreso</span>
                          <span className="font-bold text-primary-600 text-sm">{progress.toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-4 shadow-inner overflow-hidden">
                          <div
                            className="bg-gradient-to-r from-primary-500 via-primary-600 to-primary-700 h-4 rounded-full transition-all duration-500 flex items-center justify-center"
                            style={{ width: `${progress}%` }}
                          >
                            {progress > 15 && (
                              <span className="text-[10px] text-white font-bold px-2">
                                {job.current_epoch}/{job.epochs} epochs
                              </span>
                            )}
                          </div>
                        </div>
                        {job.current_epoch > 0 && (
                          <div className="text-xs text-gray-500 flex items-center justify-between">
                            <span>⏱️ Actualizando en tiempo real...</span>
                            <span className="text-green-600 font-medium">✓ Epoch {job.current_epoch} completado</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )
                })}
            </div>
          </div>
        )}

        {trainings.length === 0 ? (
          <p className="text-center text-gray-500 py-8">No hay entrenamientos registrados</p>
        ) : (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-3">📋 Historial Completo</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dataset</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tamaño</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Progreso</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">mAP</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Modelo</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {trainings.map((job) => (
                    <tr key={job.job_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">{job.dataset_name}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">yolo11{job.model_size}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        <div className="flex items-center">
                          <span className="mr-2">{job.current_epoch}/{job.epochs}</span>
                          {job.status === 'running' && (
                            <div className="w-16 bg-gray-200 rounded-full h-1.5">
                              <div 
                                className="bg-primary-600 h-1.5 rounded-full" 
                                style={{ width: `${calculateProgress(job.current_epoch, job.epochs)}%` }}
                              />
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <span className="font-semibold text-green-600">{job.best_map.toFixed(3)}</span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(job.status)}`}>
                          {job.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-xs">
                        {job.status === 'completed' && job.model_name ? (
                          <div className="font-mono text-primary-600 bg-primary-50 px-2 py-1 rounded border border-primary-200">
                            📦 {job.model_name}
                          </div>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
            <h2 className="text-2xl font-bold mb-6">Nuevo Entrenamiento</h2>
            <div className="space-y-4">
              <div>
                <label className="label">Dataset</label>
                <select value={config.dataset_name} onChange={(e) => setConfig({ ...config, dataset_name: e.target.value })} className="input">
                  <option value="">Selecciona</option>
                  {datasets.map((ds) => (
                    <option key={ds.name} value={ds.name}>{ds.name}</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Tamaño</label>
                  <select value={config.model_size} onChange={(e) => setConfig({ ...config, model_size: e.target.value })} className="input">
                    <option value="n">Nano</option>
                    <option value="s">Small</option>
                    <option value="m">Medium</option>
                  </select>
                </div>
                <div>
                  <label className="label">Epochs</label>
                  <input type="number" value={config.epochs} onChange={(e) => setConfig({ ...config, epochs: parseInt(e.target.value) })} className="input" />
                </div>
              </div>
            </div>
            <div className="mt-6 flex justify-end space-x-3">
              <button onClick={() => setShowCreateModal(false)} className="btn btn-secondary">Cancelar</button>
              <button onClick={handleStartTraining} disabled={loading} className="btn btn-primary">
                {loading ? 'Iniciando...' : 'Iniciar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
