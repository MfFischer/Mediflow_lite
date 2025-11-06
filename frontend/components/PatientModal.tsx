import { useState, useEffect } from 'react'
import axios from 'axios'

interface PatientModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  patient?: any
}

export default function PatientModal({ isOpen, onClose, onSuccess, patient }: PatientModalProps) {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    date_of_birth: '',
    gender: 'male',
    email: '',
    phone_number: '',
    address: '',
    ssn: '',
    insurance_number: '',
    medical_history: '',
    // Philippine Insurance
    philhealth_number: '',
    philhealth_member_type: '',
    hmo_provider: '',
    hmo_card_number: '',
    hmo_coverage_limit: '',
    hmo_validity_date: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (patient) {
      setFormData({
        first_name: patient.first_name || '',
        last_name: patient.last_name || '',
        date_of_birth: patient.date_of_birth || '',
        gender: patient.gender || 'male',
        email: patient.email || '',
        phone_number: patient.phone_number || '',
        address: patient.address || '',
        ssn: patient.ssn || '',
        insurance_number: patient.insurance_number || '',
        medical_history: patient.medical_history || '',
        philhealth_number: patient.philhealth_number || '',
        philhealth_member_type: patient.philhealth_member_type || '',
        hmo_provider: patient.hmo_provider || '',
        hmo_card_number: patient.hmo_card_number || '',
        hmo_coverage_limit: patient.hmo_coverage_limit || '',
        hmo_validity_date: patient.hmo_validity_date || ''
      })
    } else {
      setFormData({
        first_name: '',
        last_name: '',
        date_of_birth: '',
        gender: 'male',
        email: '',
        phone_number: '',
        address: '',
        ssn: '',
        insurance_number: '',
        medical_history: '',
        philhealth_number: '',
        philhealth_member_type: '',
        hmo_provider: '',
        hmo_card_number: '',
        hmo_coverage_limit: '',
        hmo_validity_date: ''
      })
    }
  }, [patient])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const token = localStorage.getItem('token')
      const url = patient
        ? `http://localhost:8000/api/v1/patients/${patient.id}`
        : 'http://localhost:8000/api/v1/patients/'

      const method = patient ? 'put' : 'post'

      await axios[method](url, formData, {
        headers: { Authorization: `Bearer ${token}` }
      })

      onSuccess()
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save patient')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-gradient-to-r from-indigo-500 to-purple-600 text-white p-6 rounded-t-2xl">
          <h2 className="text-2xl font-bold">{patient ? 'Edit Patient' : 'Add New Patient'}</h2>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">First Name *</label>
              <input
                type="text"
                required
                value={formData.first_name}
                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Last Name *</label>
              <input
                type="text"
                required
                value={formData.last_name}
                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Date of Birth *</label>
              <input
                type="date"
                required
                value={formData.date_of_birth}
                onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Gender *</label>
              <select
                required
                value={formData.gender}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
              <input
                type="tel"
                value={formData.phone_number}
                onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Address</label>
              <input
                type="text"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">SSN</label>
              <input
                type="text"
                value={formData.ssn}
                onChange={(e) => setFormData({ ...formData, ssn: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Insurance Number</label>
              <input
                type="text"
                value={formData.insurance_number}
                onChange={(e) => setFormData({ ...formData, insurance_number: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Medical History</label>
              <textarea
                rows={3}
                value={formData.medical_history}
                onChange={(e) => setFormData({ ...formData, medical_history: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Philippine Insurance Information */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <span className="bg-green-100 text-green-700 px-3 py-1 rounded-lg text-sm mr-2">🇵🇭</span>
              Philippine Insurance Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">PhilHealth Number</label>
                <input
                  type="text"
                  value={formData.philhealth_number}
                  onChange={(e) => setFormData({ ...formData, philhealth_number: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="12-digit PhilHealth number"
                  maxLength={20}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Member Type</label>
                <select
                  value={formData.philhealth_member_type}
                  onChange={(e) => setFormData({ ...formData, philhealth_member_type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="">Select Type</option>
                  <option value="Member">Member</option>
                  <option value="Dependent">Dependent</option>
                  <option value="Senior Citizen">Senior Citizen</option>
                  <option value="PWD">PWD (Person with Disability)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">HMO Provider</label>
                <select
                  value={formData.hmo_provider}
                  onChange={(e) => setFormData({ ...formData, hmo_provider: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="">Select HMO</option>
                  <option value="Maxicare">Maxicare</option>
                  <option value="Medicard">Medicard</option>
                  <option value="Intellicare">Intellicare</option>
                  <option value="Cocolife">Cocolife</option>
                  <option value="PhilCare">PhilCare</option>
                  <option value="Avega">Avega</option>
                  <option value="Carewell">Carewell</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">HMO Card Number</label>
                <input
                  type="text"
                  value={formData.hmo_card_number}
                  onChange={(e) => setFormData({ ...formData, hmo_card_number: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="HMO card number"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">HMO Coverage Limit</label>
                <input
                  type="text"
                  value={formData.hmo_coverage_limit}
                  onChange={(e) => setFormData({ ...formData, hmo_coverage_limit: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="e.g., ₱100,000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">HMO Validity Date</label>
                <input
                  type="date"
                  value={formData.hmo_validity_date}
                  onChange={(e) => setFormData({ ...formData, hmo_validity_date: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
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
              className="px-6 py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all disabled:opacity-50"
            >
              {loading ? 'Saving...' : patient ? 'Update Patient' : 'Add Patient'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

