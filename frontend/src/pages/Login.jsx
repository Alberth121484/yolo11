import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { LogIn, Mail, Lock } from 'lucide-react'
import { FaGoogle, FaGithub, FaFacebook } from 'react-icons/fa'
import axios from 'axios'
import toast from 'react-hot-toast'

export default function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  
  const handleOAuthLogin = (provider) => {
    // Redirect to backend OAuth endpoint
    window.location.href = `http://localhost:8000/api/v1/auth/login/${provider}`
  }
  
  const handleEmailLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const response = await axios.post('http://localhost:8000/api/v1/auth/login/credentials', {
        email,
        password
      })
      
      localStorage.setItem('token', response.data.access_token)
      toast.success('¡Sesión iniciada correctamente!')
      navigate('/')
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al iniciar sesión')
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-2xl">
        {/* Logo and Title */}
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="bg-primary-600 p-3 rounded-full">
              <LogIn className="h-8 w-8 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-gray-900">YOLO11</h2>
          <p className="mt-2 text-sm text-gray-600">
            Sistema de Detección de Objetos con IA
          </p>
        </div>

        {/* Email/Password Form */}
        <form onSubmit={handleEmailLogin} className="mt-8 space-y-6">
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Correo Electrónico
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10 w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="admin@admin.com"
                />
              </div>
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Contraseña
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-10 w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="••••••••"
                />
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center px-4 py-3 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Iniciando sesión...
              </>
            ) : (
              <>
                <LogIn className="h-5 w-5 mr-2" />
                Iniciar Sesión
              </>
            )}
          </button>
        </form>

        {/* Divider */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-4 bg-white text-gray-500">O continúa con</span>
          </div>
        </div>

        {/* OAuth Buttons */}
        <div className="space-y-3">
          <p className="text-center text-sm text-gray-600 mb-4">
            Redes sociales
          </p>
          
          {/* Google */}
          <button
            onClick={() => handleOAuthLogin('google')}
            className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all"
          >
            <FaGoogle className="h-5 w-5 mr-3 text-red-500" />
            Continuar con Google
          </button>

          {/* GitHub */}
          <button
            onClick={() => handleOAuthLogin('github')}
            className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all"
          >
            <FaGithub className="h-5 w-5 mr-3 text-gray-900" />
            Continuar con GitHub
          </button>

          {/* Facebook */}
          <button
            onClick={() => handleOAuthLogin('facebook')}
            className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all"
          >
            <FaFacebook className="h-5 w-5 mr-3 text-blue-600" />
            Continuar con Facebook
          </button>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-xs text-gray-500">
            Al continuar, aceptas nuestros términos de servicio y política de privacidad
          </p>
        </div>
      </div>
    </div>
  )
}
