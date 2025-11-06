import { useState } from 'react'
import axios from 'axios'

export default function TestAPI() {
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)

  const testUsersAPI = async () => {
    setLoading(true)
    setResult('')
    
    try {
      const token = localStorage.getItem('access_token')
      console.log('Token:', token ? `${token.substring(0, 20)}...` : 'NO TOKEN')
      
      const response = await axios.get('http://localhost:8000/api/v1/users/', {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      setResult(JSON.stringify(response.data, null, 2))
    } catch (error: any) {
      console.error('Error:', error)
      setResult(`ERROR: ${error.message}\nStatus: ${error.response?.status}\nData: ${JSON.stringify(error.response?.data, null, 2)}`)
    } finally {
      setLoading(false)
    }
  }

  const testAuth = async () => {
    setLoading(true)
    setResult('')
    
    try {
      const token = localStorage.getItem('access_token')
      console.log('Token:', token ? `${token.substring(0, 20)}...` : 'NO TOKEN')
      
      const response = await axios.get('http://localhost:8000/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      setResult(JSON.stringify(response.data, null, 2))
    } catch (error: any) {
      console.error('Error:', error)
      setResult(`ERROR: ${error.message}\nStatus: ${error.response?.status}\nData: ${JSON.stringify(error.response?.data, null, 2)}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">API Test Page</h1>
        
        <div className="bg-white rounded-lg shadow p-6 mb-4">
          <h2 className="text-xl font-semibold mb-4">Test Endpoints</h2>
          
          <div className="space-y-4">
            <button
              onClick={testAuth}
              disabled={loading}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 mr-4"
            >
              Test /auth/me
            </button>
            
            <button
              onClick={testUsersAPI}
              disabled={loading}
              className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:bg-gray-400"
            >
              Test /users/
            </button>
          </div>
        </div>
        
        {result && (
          <div className="bg-gray-900 text-green-400 rounded-lg p-6 font-mono text-sm overflow-auto">
            <pre>{result}</pre>
          </div>
        )}
      </div>
    </div>
  )
}

