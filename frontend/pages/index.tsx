import { useEffect } from 'react'
import { useRouter } from 'next/router'
import type { NextPage } from 'next'
import { isAuthenticated } from '../utils/auth'

const Home: NextPage = () => {
  const router = useRouter()

  useEffect(() => {
    // Check if user is authenticated
    if (isAuthenticated()) {
      // Redirect to dashboard if logged in
      router.push('/dashboard')
    } else {
      // Redirect to login if not logged in
      router.push('/login')
    }
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto mb-4"></div>
        <h1 className="text-2xl font-semibold text-gray-700">Loading MediFlow Lite...</h1>
        <p className="text-gray-500 mt-2">Redirecting you to the application</p>
      </div>
    </div>
  )
}

export default Home
