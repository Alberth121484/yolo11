import { useState, useCallback, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Image as ImageIcon, Loader, Download, Trash2 } from 'lucide-react'
import { inferenceAPI, modelAPI } from '@/lib/api'
import { formatDuration, parseError, isValidImageFile } from '@/lib/utils'
import toast from 'react-hot-toast'

export default function Inference() {
  const [images, setImages] = useState([])
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [models, setModels] = useState([])
  const [config, setConfig] = useState({
    model_name: 'yolo11n.pt',
    confidence: 0.25,
    iou: 0.45,
    max_det: 300,
    imgsz: 640,
  })

  useEffect(() => {
    loadModels()
  }, [])

  const loadModels = async () => {
    try {
      const { data } = await modelAPI.list()
      setModels(data)
    } catch (error) {
      console.error('Error loading models:', error)
    }
  }

  const onDrop = useCallback((acceptedFiles) => {
    const validFiles = acceptedFiles.filter(isValidImageFile)
    
    if (validFiles.length !== acceptedFiles.length) {
      toast.error('Algunos archivos no son imágenes válidas')
    }

    const newImages = validFiles.map((file) => ({
      file,
      preview: URL.createObjectURL(file),
      id: Math.random().toString(36).substr(2, 9),
    }))

    setImages((prev) => [...prev, ...newImages])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.bmp', '.webp'],
    },
    multiple: true,
  })

  const removeImage = (id) => {
    setImages((prev) => prev.filter((img) => img.id !== id))
    setResults((prev) => prev.filter((res) => res.id !== id))
  }

  const handleInference = async () => {
    if (images.length === 0) {
      toast.error('Por favor, sube al menos una imagen')
      return
    }

    setLoading(true)
    const newResults = []

    try {
      // Process images one by one or in batch
      if (images.length === 1) {
        // Single image
        const formData = new FormData()
        formData.append('file', images[0].file)
        formData.append('model_name', config.model_name)
        formData.append('confidence', config.confidence)
        formData.append('iou', config.iou)
        formData.append('max_det', config.max_det)
        formData.append('imgsz', config.imgsz)

        const { data } = await inferenceAPI.predictSingle(formData)
        newResults.push({ ...data, id: images[0].id })
      } else {
        // Batch processing
        const formData = new FormData()
        images.forEach((img) => {
          formData.append('files', img.file)
        })
        formData.append('model_name', config.model_name)
        formData.append('confidence', config.confidence)
        formData.append('iou', config.iou)
        formData.append('max_det', config.max_det)
        formData.append('imgsz', config.imgsz)

        const { data } = await inferenceAPI.predictBatch(formData)
        
        data.results.forEach((result, index) => {
          newResults.push({ ...result, id: images[index].id })
        })
      }

      setResults(newResults)
      toast.success(`Procesadas ${newResults.length} imágenes con éxito`)
    } catch (error) {
      toast.error(parseError(error))
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const clearAll = () => {
    images.forEach((img) => URL.revokeObjectURL(img.preview))
    setImages([])
    setResults([])
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Inferencia</h1>
        <p className="mt-2 text-gray-600">
          Detecta objetos en imágenes usando modelos YOLO11
        </p>
      </div>

      {/* Configuration */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Configuración
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <div>
            <label className="label">Modelo</label>
            <select
              value={config.model_name}
              onChange={(e) => setConfig({ ...config, model_name: e.target.value })}
              className="input"
            >
              <optgroup label="🏋️ Modelos Pre-entrenados">
                <option value="yolo11n.pt">YOLO11n (nano)</option>
                <option value="yolo11s.pt">YOLO11s (small)</option>
                <option value="yolo11m.pt">YOLO11m (medium)</option>
                <option value="yolo11l.pt">YOLO11l (large)</option>
                <option value="yolo11x.pt">YOLO11x (xlarge)</option>
              </optgroup>
              {models.length > 0 && (
                <optgroup label="🎯 Modelos Entrenados (tus modelos)">
                  {models.map((model) => (
                    <option key={model.name} value={model.name}>
                      {model.name} ({model.num_classes} clases)
                    </option>
                  ))}
                </optgroup>
              )}
            </select>
            {models.length > 0 && (
              <p className="text-xs text-green-600 mt-1">
                ✓ {models.length} modelo{models.length > 1 ? 's' : ''} personalizado{models.length > 1 ? 's' : ''} disponible{models.length > 1 ? 's' : ''}
              </p>
            )}
          </div>
          <div>
            <label className="label">Confidence</label>
            <input
              type="number"
              min="0"
              max="1"
              step="0.05"
              value={config.confidence}
              onChange={(e) =>
                setConfig({ ...config, confidence: parseFloat(e.target.value) })
              }
              className="input"
            />
          </div>
          <div>
            <label className="label">IoU</label>
            <input
              type="number"
              min="0"
              max="1"
              step="0.05"
              value={config.iou}
              onChange={(e) =>
                setConfig({ ...config, iou: parseFloat(e.target.value) })
              }
              className="input"
            />
          </div>
          <div>
            <label className="label">Max Detections</label>
            <input
              type="number"
              min="1"
              max="1000"
              value={config.max_det}
              onChange={(e) =>
                setConfig({ ...config, max_det: parseInt(e.target.value) })
              }
              className="input"
            />
          </div>
          <div>
            <label className="label">Image Size</label>
            <select
              value={config.imgsz}
              onChange={(e) =>
                setConfig({ ...config, imgsz: parseInt(e.target.value) })
              }
              className="input"
            >
              <option value="320">320</option>
              <option value="640">640</option>
              <option value="1280">1280</option>
            </select>
          </div>
        </div>
      </div>

      {/* Upload Area */}
      <div className="card">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-300 hover:border-primary-400'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-4 text-lg font-medium text-gray-900">
            {isDragActive
              ? 'Suelta las imágenes aquí'
              : 'Arrastra imágenes aquí o haz clic para seleccionar'}
          </p>
          <p className="mt-2 text-sm text-gray-500">
            JPG, PNG, BMP, WEBP hasta 10MB
          </p>
        </div>

        {images.length > 0 && (
          <div className="mt-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-900">
                {images.length} {images.length === 1 ? 'imagen' : 'imágenes'} cargadas
              </h3>
              <button
                onClick={clearAll}
                className="text-sm text-red-600 hover:text-red-700 flex items-center"
              >
                <Trash2 className="h-4 w-4 mr-1" />
                Limpiar todo
              </button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {images.map((img) => (
                <div key={img.id} className="relative group">
                  <img
                    src={img.preview}
                    alt="Preview"
                    className="w-full h-32 object-cover rounded-lg"
                  />
                  <button
                    onClick={() => removeImage(img.id)}
                    className="absolute top-2 right-2 bg-red-500 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {images.length > 0 && (
          <div className="mt-6 flex justify-end">
            <button
              onClick={handleInference}
              disabled={loading}
              className="btn btn-primary flex items-center"
            >
              {loading ? (
                <>
                  <Loader className="animate-spin h-5 w-5 mr-2" />
                  Procesando...
                </>
              ) : (
                <>
                  <ImageIcon className="h-5 w-5 mr-2" />
                  Detectar Objetos
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Resultados
          </h2>
          <div className="space-y-6">
            {results.map((result, index) => (
              <div key={result.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-medium text-gray-900">
                      Imagen {index + 1}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">
                      {result.detections.length} objetos detectados en{' '}
                      {formatDuration(result.inference_time)}
                    </p>
                  </div>
                  {result.result_path && (
                    <button className="btn btn-secondary text-sm flex items-center">
                      <Download className="h-4 w-4 mr-1" />
                      Descargar
                    </button>
                  )}
                </div>

                {result.detections.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                            Clase
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                            Confianza
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                            Posición
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {result.detections.map((det, idx) => (
                          <tr key={idx}>
                            <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900">
                              {det.class_name}
                            </td>
                            <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                              {(det.confidence * 100).toFixed(1)}%
                            </td>
                            <td className="px-4 py-2 text-sm text-gray-500">
                              x: {det.bbox.x1.toFixed(0)}, y: {det.bbox.y1.toFixed(0)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-center text-gray-500 py-4">
                    No se detectaron objetos en esta imagen
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
