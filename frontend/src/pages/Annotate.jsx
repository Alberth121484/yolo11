import { useState, useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Save, SkipForward, ArrowLeft, Trash2, Tag } from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api/v1'

export default function Annotate() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const datasetName = searchParams.get('dataset')
  
  const canvasRef = useRef(null)
  const imageRef = useRef(null)
  const [images, setImages] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [currentImage, setCurrentImage] = useState(null)
  const [boxes, setBoxes] = useState([])
  const [isDrawing, setIsDrawing] = useState(false)
  const [startPos, setStartPos] = useState(null)
  const [currentBox, setCurrentBox] = useState(null)
  const [datasetInfo, setDatasetInfo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [scale, setScale] = useState(1)
  const [offset, setOffset] = useState({ x: 0, y: 0 })

  useEffect(() => {
    console.log('Annotate component mounted, dataset:', datasetName)
    if (!datasetName) {
      console.error('No dataset name provided')
      toast.error('No dataset specified')
      navigate('/datasets')
      return
    }
    loadAnnotationData()
  }, [datasetName])

  useEffect(() => {
    if (images.length > 0 && currentIndex < images.length) {
      loadImage(images[currentIndex])
    }
  }, [currentIndex, images])

  const loadAnnotationData = async () => {
    try {
      setLoading(true)
      console.log('Loading annotation data for dataset:', datasetName)
      const { data } = await axios.get(
        `${API_BASE}/datasets/${datasetName}/annotation/images`
      )
      console.log('Annotation data received:', data)
      setDatasetInfo(data)
      setImages(data.images)
      
      // Find first unannotated image
      const firstUnannotated = data.images.findIndex(img => !img.has_annotation)
      if (firstUnannotated !== -1) {
        setCurrentIndex(firstUnannotated)
      }
      
      console.log(`Loaded ${data.images.length} images, ${data.annotated} annotated`)
    } catch (error) {
      console.error('Failed to load annotation data:', error)
      console.error('Error details:', error.response?.data || error.message)
      toast.error(`Failed to load images: ${error.response?.data?.detail || error.message}`)
      navigate('/datasets')
    } finally {
      setLoading(false)
    }
  }

  const loadImage = (imageData) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.src = `http://localhost:8000${imageData.path}`
    
    console.log('Loading image:', img.src)
    
    img.onload = () => {
      setCurrentImage(img)
      setBoxes([])
      
      // Calculate scale to fit canvas
      const canvas = canvasRef.current
      if (canvas) {
        const maxWidth = canvas.width
        const maxHeight = canvas.height
        const scaleX = maxWidth / img.width
        const scaleY = maxHeight / img.height
        const newScale = Math.min(scaleX, scaleY, 1)
        setScale(newScale)
        
        // Center image
        const scaledWidth = img.width * newScale
        const scaledHeight = img.height * newScale
        setOffset({
          x: (maxWidth - scaledWidth) / 2,
          y: (maxHeight - scaledHeight) / 2
        })
        
        drawCanvas()
      }
    }
    
    img.onerror = () => {
      toast.error(`Failed to load image: ${imageData.filename}`)
    }
  }

  const drawCanvas = () => {
    const canvas = canvasRef.current
    if (!canvas || !currentImage) return
    
    const ctx = canvas.getContext('2d')
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    // Draw image
    ctx.drawImage(
      currentImage,
      offset.x,
      offset.y,
      currentImage.width * scale,
      currentImage.height * scale
    )
    
    // Draw existing boxes
    boxes.forEach((box, index) => {
      ctx.strokeStyle = '#10b981'
      ctx.lineWidth = 2
      ctx.strokeRect(
        offset.x + box.x * scale,
        offset.y + box.y * scale,
        box.width * scale,
        box.height * scale
      )
      
      // Draw label
      ctx.fillStyle = '#10b981'
      ctx.fillRect(
        offset.x + box.x * scale,
        offset.y + box.y * scale - 20,
        60,
        20
      )
      ctx.fillStyle = '#fff'
      ctx.font = '12px sans-serif'
      ctx.fillText(
        `Class ${box.class_id}`,
        offset.x + box.x * scale + 5,
        offset.y + box.y * scale - 6
      )
    })
    
    // Draw current box being drawn
    if (currentBox) {
      ctx.strokeStyle = '#3b82f6'
      ctx.lineWidth = 2
      ctx.setLineDash([5, 5])
      ctx.strokeRect(
        offset.x + currentBox.x * scale,
        offset.y + currentBox.y * scale,
        currentBox.width * scale,
        currentBox.height * scale
      )
      ctx.setLineDash([])
    }
  }

  useEffect(() => {
    drawCanvas()
  }, [currentImage, boxes, currentBox, scale, offset])

  const handleMouseDown = (e) => {
    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    const x = (e.clientX - rect.left - offset.x) / scale
    const y = (e.clientY - rect.top - offset.y) / scale
    
    // Check if within image bounds
    if (x >= 0 && x <= currentImage.width && y >= 0 && y <= currentImage.height) {
      setIsDrawing(true)
      setStartPos({ x, y })
    }
  }

  const handleMouseMove = (e) => {
    if (!isDrawing || !startPos || !currentImage) return
    
    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    const x = (e.clientX - rect.left - offset.x) / scale
    const y = (e.clientY - rect.top - offset.y) / scale
    
    // Clamp to image bounds
    const clampedX = Math.max(0, Math.min(x, currentImage.width))
    const clampedY = Math.max(0, Math.min(y, currentImage.height))
    
    const boxX = Math.min(startPos.x, clampedX)
    const boxY = Math.min(startPos.y, clampedY)
    const boxWidth = Math.abs(clampedX - startPos.x)
    const boxHeight = Math.abs(clampedY - startPos.y)
    
    setCurrentBox({
      x: boxX,
      y: boxY,
      width: boxWidth,
      height: boxHeight,
      class_id: 0
    })
  }

  const handleMouseUp = () => {
    if (currentBox && currentBox.width > 10 && currentBox.height > 10) {
      setBoxes([...boxes, currentBox])
      console.log('Added box:', currentBox)
    }
    setIsDrawing(false)
    setStartPos(null)
    setCurrentBox(null)
  }

  const handleSave = async () => {
    if (boxes.length === 0) {
      toast.error('Please draw at least one bounding box')
      return
    }
    
    try {
      // Convert boxes to YOLO format (normalized 0-1)
      const yoloBoxes = boxes.map(box => ({
        class_id: box.class_id,
        x_center: (box.x + box.width / 2) / currentImage.width,
        y_center: (box.y + box.height / 2) / currentImage.height,
        width: box.width / currentImage.width,
        height: box.height / currentImage.height
      }))
      
      const formData = new FormData()
      formData.append('filename', images[currentIndex].filename)
      formData.append('split', 'train')
      formData.append('annotations', JSON.stringify(yoloBoxes))
      
      const response = await axios.post(
        `${API_BASE}/datasets/${datasetName}/annotation/save`,
        formData
      )
      
      toast.success(
        `✓ Guardado ${boxes.length} anotación(es) en train/val/test`,
        { duration: 3000 }
      )
      
      // Mark as annotated and move to next
      const updatedImages = [...images]
      updatedImages[currentIndex].has_annotation = true
      setImages(updatedImages)
      
      handleNext()
    } catch (error) {
      console.error('Failed to save annotation:', error)
      toast.error('Failed to save annotation')
    }
  }

  const handleNext = () => {
    if (currentIndex < images.length - 1) {
      setCurrentIndex(currentIndex + 1)
      setBoxes([])
    } else {
      toast.success('All images annotated!')
    }
  }

  const handleSkip = () => {
    handleNext()
  }

  const handleClearBoxes = () => {
    setBoxes([])
    toast.success('Cleared all boxes')
  }

  const handleDeleteBox = (index) => {
    setBoxes(boxes.filter((_, i) => i !== index))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading images...</p>
        </div>
      </div>
    )
  }

  if (!images || images.length === 0) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-gray-600">No images found in this dataset</p>
          <button onClick={() => navigate('/datasets')} className="btn btn-primary mt-4">
            Back to Datasets
          </button>
        </div>
      </div>
    )
  }

  const progress = ((images.filter(img => img.has_annotation).length / images.length) * 100).toFixed(0)

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/datasets')}
              className="text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Annotate Dataset</h1>
              <p className="text-sm text-gray-600">
                {datasetName} - Image {currentIndex + 1} of {images.length}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="text-right mr-4">
              <div className="text-sm text-gray-600">Progress</div>
              <div className="text-lg font-bold text-primary-600">{progress}%</div>
            </div>
            <button onClick={handleClearBoxes} className="btn btn-secondary" disabled={boxes.length === 0}>
              <Trash2 className="h-4 w-4 mr-2" />
              Clear All
            </button>
            <button onClick={handleSkip} className="btn btn-secondary">
              <SkipForward className="h-4 w-4 mr-2" />
              Skip
            </button>
            <button onClick={handleSave} className="btn btn-primary" disabled={boxes.length === 0}>
              <Save className="h-4 w-4 mr-2" />
              Save & Next
            </button>
          </div>
        </div>
        
        {/* Progress bar */}
        <div className="mt-4">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Canvas area */}
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="bg-white rounded-lg shadow-lg p-4">
            <div className="mb-3">
              <p className="text-sm text-gray-600">
                <Tag className="h-4 w-4 inline mr-1" />
                Click and drag to draw bounding boxes around objects
              </p>
            </div>
            <canvas
              ref={canvasRef}
              width={800}
              height={600}
              className="border-2 border-gray-300 rounded cursor-crosshair"
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={() => {
                if (isDrawing) handleMouseUp()
              }}
            />
          </div>
        </div>

        {/* Sidebar */}
        <div className="w-80 bg-white border-l border-gray-200 p-4 overflow-y-auto">
          <h3 className="font-semibold text-gray-900 mb-3">Current Image</h3>
          <div className="bg-gray-50 rounded p-3 mb-4">
            <p className="text-sm text-gray-700 font-mono break-all">
              {images[currentIndex]?.filename}
            </p>
            <p className="text-xs text-gray-500 mt-2">
              {images[currentIndex]?.has_annotation ? '✓ Annotated' : '○ Not annotated'}
            </p>
          </div>

          <h3 className="font-semibold text-gray-900 mb-3">
            Bounding Boxes ({boxes.length})
          </h3>
          {boxes.length === 0 ? (
            <p className="text-sm text-gray-500">No boxes yet. Draw on the canvas.</p>
          ) : (
            <div className="space-y-2">
              {boxes.map((box, index) => (
                <div key={index} className="flex items-center justify-between bg-gray-50 rounded p-2">
                  <div className="text-sm">
                    <div className="font-medium">Box {index + 1}</div>
                    <div className="text-xs text-gray-500">Class {box.class_id}</div>
                  </div>
                  <button
                    onClick={() => handleDeleteBox(index)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-3">Image List</h3>
            <div className="space-y-1 max-h-96 overflow-y-auto">
              {images.map((img, idx) => (
                <button
                  key={idx}
                  onClick={() => setCurrentIndex(idx)}
                  className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                    idx === currentIndex
                      ? 'bg-primary-100 text-primary-700 font-medium'
                      : img.has_annotation
                      ? 'bg-green-50 text-green-700 hover:bg-green-100'
                      : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="truncate">{img.filename}</span>
                    {img.has_annotation && <span className="text-green-600">✓</span>}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
