import { useState, useEffect } from 'react'
import axios from 'axios'

interface LabResultModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  labResult?: any
}

interface TestValue {
  parameter_name: string
  value: string
  reference_range: string
  unit: string
}

export default function LabResultModal({ isOpen, onClose, onSuccess, labResult }: LabResultModalProps) {
  const [formData, setFormData] = useState({
    patient_id: '',
    doctor_id: '',
    appointment_id: '',
    test_name: '',
    test_category: '',
    test_date: '',
    status: 'pending',
    notes: '',
    doctor_comments: ''
  })
  const [testValues, setTestValues] = useState<TestValue[]>([
    { parameter_name: '', value: '', reference_range: '', unit: '' }
  ])
  const [patients, setPatients] = useState<any[]>([])
  const [doctors, setDoctors] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      fetchPatients()
      fetchDoctors()
    }
  }, [isOpen])

  useEffect(() => {
    if (labResult) {
      setFormData({
        patient_id: labResult.patient_id || '',
        doctor_id: labResult.doctor_id || '',
        appointment_id: labResult.appointment_id || '',
        test_name: labResult.test_name || '',
        test_category: labResult.test_category || '',
        test_date: labResult.test_date ? labResult.test_date.slice(0, 10) : '',
        status: labResult.status || 'pending',
        notes: labResult.notes || '',
        doctor_comments: labResult.doctor_comments || ''
      })
      if (labResult.test_values && labResult.test_values.length > 0) {
        setTestValues(labResult.test_values)
      }
    } else {
      setFormData({
        patient_id: '',
        doctor_id: '',
        appointment_id: '',
        test_name: '',
        test_category: '',
        test_date: '',
        status: 'pending',
        notes: '',
        doctor_comments: ''
      })
      setTestValues([
        { parameter_name: '', value: '', reference_range: '', unit: '' }
      ])
    }
  }, [labResult])

  const fetchPatients = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get('http://localhost:8000/api/v1/patients/', {
        headers: { Authorization: `Bearer ${token}` },
        params: { page: 1, page_size: 100 }
      })
      const data = Array.isArray(response.data) ? response.data : response.data.items || []
      setPatients(data)
    } catch (err) {
      console.error('Failed to fetch patients:', err)
    }
  }

  const fetchDoctors = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get('http://localhost:8000/api/v1/users/', {
        headers: { Authorization: `Bearer ${token}` },
        params: { role: 'doctor' }
      })
      const data = Array.isArray(response.data) ? response.data : response.data.items || []
      setDoctors(data)
    } catch (err) {
      console.error('Failed to fetch doctors:', err)
    }
  }

  const addTestValue = () => {
    setTestValues([...testValues, { parameter_name: '', value: '', reference_range: '', unit: '' }])
  }

  const removeTestValue = (index: number) => {
    setTestValues(testValues.filter((_, i) => i !== index))
  }

  const updateTestValue = (index: number, field: keyof TestValue, value: string) => {
    const updated = [...testValues]
    updated[index][field] = value
    setTestValues(updated)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const token = localStorage.getItem('token')
      const url = labResult
        ? `http://localhost:8000/api/v1/lab-results/${labResult.id}`
        : 'http://localhost:8000/api/v1/lab-results/'

      const method = labResult ? 'put' : 'post'

      await axios[method](url, {
        ...formData,
        patient_id: parseInt(formData.patient_id),
        doctor_id: parseInt(formData.doctor_id),
        appointment_id: formData.appointment_id ? parseInt(formData.appointment_id) : null,
        test_values: testValues.filter(tv => tv.parameter_name.trim() !== '')
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })

      onSuccess()
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save lab result')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-gradient-to-r from-green-500 to-emerald-500 text-white p-6 rounded-t-2xl">
          <h2 className="text-2xl font-bold">{labResult ? 'Edit Lab Result' : 'Add Lab Result'}</h2>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl">
              {error}
            </div>
          )}

          {/* Basic Information */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Patient *</label>
                <select
                  required
                  value={formData.patient_id}
                  onChange={(e) => setFormData({ ...formData, patient_id: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="">Select Patient</option>
                  {patients.map((patient) => (
                    <option key={patient.id} value={patient.id}>
                      {patient.first_name} {patient.last_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Doctor *</label>
                <select
                  required
                  value={formData.doctor_id}
                  onChange={(e) => setFormData({ ...formData, doctor_id: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="">Select Doctor</option>
                  {doctors.map((doctor) => (
                    <option key={doctor.id} value={doctor.id}>
                      Dr. {doctor.username}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Test Name *</label>
                <input
                  type="text"
                  required
                  value={formData.test_name}
                  onChange={(e) => setFormData({ ...formData, test_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="e.g., Complete Blood Count"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Category *</label>
                <select
                  required
                  value={formData.test_category}
                  onChange={(e) => setFormData({ ...formData, test_category: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="">Select Category</option>
                  <option value="blood">Blood Test</option>
                  <option value="urine">Urine Test</option>
                  <option value="imaging">Imaging</option>
                  <option value="biopsy">Biopsy</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Test Date *</label>
                <input
                  type="date"
                  required
                  value={formData.test_date}
                  onChange={(e) => setFormData({ ...formData, test_date: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Status *</label>
                <select
                  required
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="pending">Pending</option>
                  <option value="completed">Completed</option>
                  <option value="reviewed">Reviewed</option>
                </select>
              </div>
            </div>
          </div>

          {/* Test Values */}
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Test Values</h3>
              <button
                type="button"
                onClick={addTestValue}
                className="bg-green-100 text-green-600 px-4 py-2 rounded-lg hover:bg-green-200 transition-colors text-sm font-medium"
              >
                + Add Test Value
              </button>
            </div>

            <div className="space-y-4">
              {testValues.map((tv, index) => (
                <div key={index} className="border border-gray-200 rounded-xl p-4 relative">
                  {testValues.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeTestValue(index)}
                      className="absolute top-2 right-2 text-red-500 hover:text-red-700"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Parameter Name *</label>
                      <input
                        type="text"
                        required
                        value={tv.parameter_name}
                        onChange={(e) => updateTestValue(index, 'parameter_name', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        placeholder="e.g., Hemoglobin"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Value *</label>
                      <input
                        type="text"
                        required
                        value={tv.value}
                        onChange={(e) => updateTestValue(index, 'value', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        placeholder="e.g., 14.5"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Reference Range</label>
                      <input
                        type="text"
                        value={tv.reference_range}
                        onChange={(e) => updateTestValue(index, 'reference_range', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        placeholder="e.g., 12-16"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Unit</label>
                      <input
                        type="text"
                        value={tv.unit}
                        onChange={(e) => updateTestValue(index, 'unit', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        placeholder="e.g., g/dL"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Notes */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Notes</label>
              <textarea
                rows={3}
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Lab technician notes"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Doctor Comments</label>
              <textarea
                rows={3}
                value={formData.doctor_comments}
                onChange={(e) => setFormData({ ...formData, doctor_comments: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Doctor's interpretation"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-all"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl hover:shadow-lg transition-all disabled:opacity-50"
            >
              {loading ? 'Saving...' : labResult ? 'Update Lab Result' : 'Add Lab Result'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

