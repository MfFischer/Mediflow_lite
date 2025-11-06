import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import type { NextPage } from 'next'
import Layout from '../components/Layout'
import { isAuthenticated } from '../utils/auth'
import api from '../utils/api'
import LabResultModal from '../components/LabResultModal'

interface LabResult {
  id: number
  patient_id: number
  patient_name?: string
  test_name: string
  test_type: string
  result_value: string
  reference_range?: string
  status: 'pending' | 'completed' | 'reviewed'
  notes?: string
  created_at: string
  completed_at?: string
}

const LabResults: NextPage = () => {
  const router = useRouter()
  const [labResults, setLabResults] = useState<LabResult[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all')
  const [showModal, setShowModal] = useState(false)
  const [selectedLabResult, setSelectedLabResult] = useState<LabResult | undefined>(undefined)

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login')
      return
    }
    loadLabResults()
  }, [filter])

  const loadLabResults = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/v1/lab-results/')
      let data = Array.isArray(response.data) ? response.data : []

      if (filter === 'pending') {
        data = data.filter((lab: LabResult) => lab.status === 'pending')
      } else if (filter === 'completed') {
        data = data.filter((lab: LabResult) => lab.status === 'completed' || lab.status === 'reviewed')
      }

      setLabResults(data)
    } catch (error) {
      console.error('Error loading lab results:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-700'
      case 'completed':
        return 'bg-green-100 text-green-700'
      case 'reviewed':
        return 'bg-blue-100 text-blue-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="text-center py-20">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600 mb-4"></div>
          <p className="text-gray-600 text-lg">Loading lab results...</p>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Lab Results</h1>
            <p className="text-gray-600">View and manage laboratory test results</p>
          </div>
          <button
            type="button"
            onClick={() => {
              setSelectedLabResult(undefined)
              setShowModal(true)
            }}
            className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-6 py-3 rounded-xl hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-200 flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>Add Result</span>
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="mb-6 flex space-x-2">
        <button
          type="button"
          onClick={() => setFilter('all')}
          className={`px-6 py-3 rounded-xl font-medium transition-all ${
            filter === 'all'
              ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg'
              : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
          }`}
        >
          All Results
        </button>
        <button
          type="button"
          onClick={() => setFilter('pending')}
          className={`px-6 py-3 rounded-xl font-medium transition-all ${
            filter === 'pending'
              ? 'bg-gradient-to-r from-yellow-500 to-orange-500 text-white shadow-lg'
              : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
          }`}
        >
          Pending
        </button>
        <button
          type="button"
          onClick={() => setFilter('completed')}
          className={`px-6 py-3 rounded-xl font-medium transition-all ${
            filter === 'completed'
              ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg'
              : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
          }`}
        >
          Completed
        </button>
      </div>

      {/* Lab Results Grid */}
      {labResults.length === 0 ? (
        <div className="bg-white rounded-2xl shadow-lg p-12 text-center border border-gray-100">
          <svg className="w-20 h-20 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No lab results found</h3>
          <p className="text-gray-600 mb-6">Lab results will appear here once tests are completed</p>
          <button
            type="button"
            onClick={() => alert('Add lab result - Coming soon!')}
            className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-6 py-3 rounded-xl hover:shadow-lg transition-all"
          >
            Add Lab Result
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {labResults.map((lab) => (
            <div
              key={lab.id}
              className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 border border-gray-100"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">{lab.test_name}</h3>
                  <p className="text-sm text-gray-600">Patient: {lab.patient_name || `ID ${lab.patient_id}`}</p>
                  <p className="text-xs text-gray-500 mt-1">{lab.test_type}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(lab.status)}`}>
                  {lab.status.charAt(0).toUpperCase() + lab.status.slice(1)}
                </span>
              </div>

              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 mb-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-gray-600 mb-1">Result Value</p>
                    <p className="text-2xl font-bold text-gray-900">{lab.result_value}</p>
                  </div>
                  {lab.reference_range && (
                    <div className="text-right">
                      <p className="text-xs text-gray-600 mb-1">Reference Range</p>
                      <p className="text-sm font-medium text-gray-700">{lab.reference_range}</p>
                    </div>
                  )}
                </div>
              </div>

              {lab.notes && (
                <div className="mb-4 p-3 bg-yellow-50 rounded-lg border border-yellow-100">
                  <p className="text-xs text-gray-600 mb-1">Notes</p>
                  <p className="text-sm text-gray-700">{lab.notes}</p>
                </div>
              )}

              <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                <span>Created: {new Date(lab.created_at).toLocaleDateString()}</span>
                {lab.completed_at && (
                  <span>Completed: {new Date(lab.completed_at).toLocaleDateString()}</span>
                )}
              </div>

              <div className="flex space-x-2 pt-4 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => alert('View details - Coming soon!')}
                  className="flex-1 bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-4 py-2 rounded-lg hover:shadow-lg transition-all text-sm font-medium"
                >
                  View Full Report
                </button>
                <button
                  type="button"
                  onClick={() => alert('Download PDF - Coming soon!')}
                  className="flex-1 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium flex items-center justify-center space-x-1"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span>PDF</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <LabResultModal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false)
          setSelectedLabResult(undefined)
        }}
        onSuccess={() => {
          loadLabResults()
        }}
        labResult={selectedLabResult}
      />
    </Layout>
  )
}

export default LabResults

