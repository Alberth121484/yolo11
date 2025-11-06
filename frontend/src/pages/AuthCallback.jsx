import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import toast from 'react-hot-toast'

export default function AuthCallback() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  
  useEffect(() => {
    const token = searchParams.get('token')
    const error = searchParams.get('message')
    
    if (error) {
      toast.error(`Error de autenticación: ${error}`)
      navigate('/login')
      return
    }
    
    if (token) {
      // Save token to localStorage
      localStorage.setItem('token', token)
      toast.success('¡Sesión iniciada correctamente!')
      navigate('/')
    } else {
      toast.error('No se recibió token de autenticación')
      navigate('/login')
    }
  }, [searchParams, navigate])
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Completando autenticación...</p>
      </div>
    </div>
  )
}
