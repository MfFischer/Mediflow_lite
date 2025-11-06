import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import type { NextPage } from 'next'
import Layout from '../components/Layout'
import { isAuthenticated } from '../utils/auth'
import api from '../utils/api'
import PrescriptionModal from '../components/PrescriptionModal'

interface Prescription {
  id: number
  patient_id: number
  patient_name?: string
  doctor_id: number
  doctor_name?: string
  medication_name: string
  dosage: string
  frequency: string
  duration: string
  instructions?: string
  dispensed: boolean
  created_at: string
}

const Prescriptions: NextPage = () => {
  const router = useRouter()
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'pending' | 'dispensed'>('all')
  const [showModal, setShowModal] = useState(false)
  const [selectedPrescription, setSelectedPrescription] = useState<Prescription | undefined>(undefined)

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login')
      return
    }
    loadPrescriptions()
  }, [filter])

  const loadPrescriptions = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/v1/prescriptions/')
      let data = Array.isArray(response.data) ? response.data : []

      if (filter === 'pending') {
        data = data.filter((rx: Prescription) => !rx.dispensed)
      } else if (filter === 'dispensed') {
        data = data.filter((rx: Prescription) => rx.dispensed)
      }

      setPrescriptions(data)
    } catch (error) {
      console.error('Error loading prescriptions:', error)
    } finally {
      setLoading(false)
    }
  }

  const generatePDF = async (prescriptionId: number) => {
    try {
      const response = await api.get(`/api/v1/prescriptions/${prescriptionId}/pdf`, {
        responseType: 'blob'
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `prescription_${prescriptionId}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Error generating PDF:', error)
      alert('PDF generation coming soon!')
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="text-center py-20">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600 mb-4"></div>
          <p className="text-gray-600 text-lg">Loading prescriptions...</p>
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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">E-Prescriptions</h1>
            <p className="text-gray-600">Manage and generate digital prescriptions</p>
          </div>
          <button
            type="button"
            onClick={() => {
              setSelectedPrescription(undefined)
              setShowModal(true)
            }}
            className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-6 py-3 rounded-xl hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-200 flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>New Prescription</span>
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
          All Prescriptions
        </button>
        <button
          type="button"
          onClick={() => setFilter('pending')}
          className={`px-6 py-3 rounded-xl font-medium transition-all ${
            filter === 'pending'
              ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white shadow-lg'
              : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
          }`}
        >
          Pending
        </button>
        <button
          type="button"
          onClick={() => setFilter('dispensed')}
          className={`px-6 py-3 rounded-xl font-medium transition-all ${
            filter === 'dispensed'
              ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg'
              : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
          }`}
        >
          Dispensed
        </button>
      </div>

      {/* Prescriptions Grid */}
      {prescriptions.length === 0 ? (
        <div className="bg-white rounded-2xl shadow-lg p-12 text-center border border-gray-100">
          <svg className="w-20 h-20 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No prescriptions found</h3>
          <p className="text-gray-600 mb-6">Get started by creating your first prescription</p>
          <button
            type="button"
            onClick={() => {
              setSelectedPrescription(undefined)
              setShowModal(true)
            }}
            className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-6 py-3 rounded-xl hover:shadow-lg transition-all"
          >
            Create Prescription
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {prescriptions.map((rx) => (
            <div
              key={rx.id}
              className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 border border-gray-100"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">{rx.medication_name}</h3>
                  <p className="text-sm text-gray-600">Patient: {rx.patient_name || `ID ${rx.patient_id}`}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  rx.dispensed
                    ? 'bg-green-100 text-green-700'
                    : 'bg-orange-100 text-orange-700'
                }`}>
                  {rx.dispensed ? 'Dispensed' : 'Pending'}
                </span>
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex items-center text-sm">
                  <span className="text-gray-500 w-24">Dosage:</span>
                  <span className="text-gray-900 font-medium">{rx.dosage}</span>
                </div>
                <div className="flex items-center text-sm">
                  <span className="text-gray-500 w-24">Frequency:</span>
                  <span className="text-gray-900 font-medium">{rx.frequency}</span>
                </div>
                <div className="flex items-center text-sm">
                  <span className="text-gray-500 w-24">Duration:</span>
                  <span className="text-gray-900 font-medium">{rx.duration}</span>
                </div>
                {rx.instructions && (
                  <div className="text-sm mt-3 p-3 bg-blue-50 rounded-lg">
                    <span className="text-gray-700">{rx.instructions}</span>
                  </div>
                )}
              </div>

              <div className="flex space-x-2 pt-4 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => generatePDF(rx.id)}
                  className="flex-1 bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-4 py-2 rounded-lg hover:shadow-lg transition-all text-sm font-medium flex items-center justify-center space-x-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span>Download PDF</span>
                </button>
                <button
                  type="button"
                  onClick={() => alert('View details - Coming soon!')}
                  className="flex-1 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
                >
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <PrescriptionModal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false)
          setSelectedPrescription(undefined)
        }}
        onSuccess={() => {
          loadPrescriptions()
        }}
        prescription={selectedPrescription}
      />
    </Layout>
  )
}

export default Prescriptions

