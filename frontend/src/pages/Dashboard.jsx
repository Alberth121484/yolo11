import { useEffect, useState } from 'react'
import { Activity, Image, Brain, Database, TrendingUp, Clock } from 'lucide-react'
import { healthAPI, modelAPI, datasetAPI, trainingAPI } from '@/lib/api'
import { formatDate } from '@/lib/utils'
import toast from 'react-hot-toast'

export default function Dashboard() {
  const [stats, setStats] = useState({
    models: 0,
    datasets: 0,
    trainings: 0,
    activeTrainings: 0,
  })
  const [systemInfo, setSystemInfo] = useState(null)
  const [recentTrainings, setRecentTrainings] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)

      // Load system info
      const { data: info } = await healthAPI.info()
      setSystemInfo(info)

      // Load stats
      const [modelsRes, datasetsRes, trainingsRes] = await Promise.all([
        modelAPI.list(),
        datasetAPI.list(),
        trainingAPI.listJobs({ limit: 10 }),
      ])

      const activeTrainings = trainingsRes.data.filter(
        (t) => t.status === 'running' || t.status === 'pending'
      ).length

      setStats({
        models: modelsRes.data.length,
        datasets: datasetsRes.data.length,
        trainings: trainingsRes.data.length,
        activeTrainings,
      })

      setRecentTrainings(trainingsRes.data.slice(0, 5))
    } catch (error) {
      toast.error('Error al cargar datos del dashboard')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    {
      name: 'Modelos',
      value: stats.models,
      icon: Brain,
      color: 'bg-blue-500',
      change: '+2 esta semana',
    },
    {
      name: 'Datasets',
      value: stats.datasets,
      icon: Database,
      color: 'bg-green-500',
      change: '+1 este mes',
    },
    {
      name: 'Entrenamientos',
      value: stats.trainings,
      icon: TrendingUp,
      color: 'bg-purple-500',
      change: `${stats.activeTrainings} activos`,
    },
    {
      name: 'Detecciones',
      value: '1,234',
      icon: Image,
      color: 'bg-orange-500',
      change: '+120 hoy',
    },
  ]

  const getStatusBadge = (status) => {
    const colors = {
      completed: 'bg-green-100 text-green-800',
      running: 'bg-blue-100 text-blue-800',
      failed: 'bg-red-100 text-red-800',
      pending: 'bg-yellow-100 text-yellow-800',
      cancelled: 'bg-gray-100 text-gray-800',
    }
    return colors[status] || colors.pending
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Sistema de Detección de Objetos con YOLO11
        </p>
      </div>

      {/* System Status */}
      {systemInfo && (
        <div className="card">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Activity className="h-5 w-5 text-green-600 mr-2" />
              <span className="text-sm font-medium text-gray-700">
                Sistema Operacional
              </span>
            </div>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <span>Versión: {systemInfo.version}</span>
              <span>
                {systemInfo.system?.cuda_available
                  ? '🚀 CUDA Disponible'
                  : '💻 CPU Mode'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">{stat.value}</p>
                <p className="mt-1 text-sm text-gray-500">{stat.change}</p>
              </div>
              <div className={`${stat.color} p-3 rounded-lg`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Trainings */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Entrenamientos Recientes
          </h2>
          <Clock className="h-5 w-5 text-gray-400" />
        </div>
        
        {recentTrainings.length === 0 ? (
          <p className="text-center text-gray-500 py-8">
            No hay entrenamientos recientes
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Job ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Dataset
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Modelo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Progreso
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Fecha
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentTrainings.map((training) => (
                  <tr key={training.job_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {training.job_id.substring(0, 20)}...
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {training.dataset_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      yolo11{training.model_size}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {training.current_epoch}/{training.epochs}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadge(
                          training.status
                        )}`}
                      >
                        {training.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(training.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <button
          onClick={() => (window.location.href = '/inference')}
          className="card hover:shadow-md transition-shadow cursor-pointer"
        >
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-primary-100">
              <Image className="h-6 w-6 text-primary-600" />
            </div>
            <h3 className="mt-4 text-lg font-medium text-gray-900">
              Nueva Inferencia
            </h3>
            <p className="mt-2 text-sm text-gray-500">
              Detecta objetos en imágenes
            </p>
          </div>
        </button>

        <button
          onClick={() => (window.location.href = '/training')}
          className="card hover:shadow-md transition-shadow cursor-pointer"
        >
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
              <Brain className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="mt-4 text-lg font-medium text-gray-900">
              Entrenar Modelo
            </h3>
            <p className="mt-2 text-sm text-gray-500">
              Entrena un nuevo modelo personalizado
            </p>
          </div>
        </button>

        <button
          onClick={() => (window.location.href = '/datasets')}
          className="card hover:shadow-md transition-shadow cursor-pointer"
        >
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-purple-100">
              <Database className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="mt-4 text-lg font-medium text-gray-900">
              Crear Dataset
            </h3>
            <p className="mt-2 text-sm text-gray-500">
              Crea y administra datasets
            </p>
          </div>
        </button>
      </div>
    </div>
  )
}
