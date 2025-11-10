import { useEffect } from 'react'
import { useRouter } from 'next/router'
import type { NextPage } from 'next'
import Layout from '../components/Layout'
import AIChat from '../components/AIChat'
import { isAuthenticated } from '../utils/auth'

const AIAssistant: NextPage = () => {
  const router = useRouter()

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login')
      return
    }
  }, [])

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">🤖 AI Assistant</h1>
          <p className="text-gray-600">
            Ask questions about patients, doctors, appointments, and financials. Works online and offline!
          </p>
        </div>
        <AIChat />
      </div>
    </Layout>
  )
}

export default AIAssistant

