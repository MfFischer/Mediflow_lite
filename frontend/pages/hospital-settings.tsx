import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Layout from '../components/Layout'
import axios from 'axios'

export default function HospitalSettings() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [settingsId, setSettingsId] = useState<number | null>(null)
  
  const [formData, setFormData] = useState({
    hospital_name: '',
    hospital_address: '',
    hospital_phone: '',
    hospital_email: '',
    hospital_website: '',
    doh_license_number: '',
    tin: '',
    philhealth_accreditation: '',
    logo_url: '',
    invoice_prefix: 'INV',
    invoice_footer: '',
    authorized_signatory: '',
    signatory_title: ''
  })

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
      return
    }
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get('http://localhost:8000/api/v1/hospital-settings/', {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      setSettingsId(response.data.id)
      setFormData({
        hospital_name: response.data.hospital_name || '',
        hospital_address: response.data.hospital_address || '',
        hospital_phone: response.data.hospital_phone || '',
        hospital_email: response.data.hospital_email || '',
        hospital_website: response.data.hospital_website || '',
        doh_license_number: response.data.doh_license_number || '',
        tin: response.data.tin || '',
        philhealth_accreditation: response.data.philhealth_accreditation || '',
        logo_url: response.data.logo_url || '',
        invoice_prefix: response.data.invoice_prefix || 'INV',
        invoice_footer: response.data.invoice_footer || '',
        authorized_signatory: response.data.authorized_signatory || '',
        signatory_title: response.data.signatory_title || ''
      })
    } catch (err: any) {
      console.error('Failed to fetch settings:', err)
      setError('Failed to load hospital settings')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    setSuccess('')

    try {
      const token = localStorage.getItem('token')
      await axios.put(
        `http://localhost:8000/api/v1/hospital-settings/${settingsId}`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      )
      
      setSuccess('Hospital settings updated successfully!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err: any) {
      console.error('Failed to update settings:', err)
      setError(err.response?.data?.detail || 'Failed to update hospital settings')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-screen">
          <div className="text-xl text-gray-600">Loading...</div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Hospital Settings</h1>
          <p className="text-gray-600">Configure your hospital information for invoices and documents</p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-xl">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-lg p-8 space-y-8">
          {/* Hospital Information */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-lg text-sm mr-2">🏥</span>
              Hospital Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">Hospital Name *</label>
                <input
                  type="text"
                  required
                  value={formData.hospital_name}
                  onChange={(e) => setFormData({ ...formData, hospital_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Medical Center"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">Address</label>
                <textarea
                  value={formData.hospital_address}
                  onChange={(e) => setFormData({ ...formData, hospital_address: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                  placeholder="123 Medical Street, City, Province"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
                <input
                  type="text"
                  value={formData.hospital_phone}
                  onChange={(e) => setFormData({ ...formData, hospital_phone: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="+63 2 1234 5678"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                <input
                  type="email"
                  value={formData.hospital_email}
                  onChange={(e) => setFormData({ ...formData, hospital_email: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="info@hospital.com"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">Website</label>
                <input
                  type="url"
                  value={formData.hospital_website}
                  onChange={(e) => setFormData({ ...formData, hospital_website: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="https://www.hospital.com"
                />
              </div>
            </div>
          </div>

          {/* Legal Information */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <span className="bg-green-100 text-green-700 px-3 py-1 rounded-lg text-sm mr-2">🇵🇭</span>
              Legal Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">DOH License Number</label>
                <input
                  type="text"
                  value={formData.doh_license_number}
                  onChange={(e) => setFormData({ ...formData, doh_license_number: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="DOH-12345"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">TIN</label>
                <input
                  type="text"
                  value={formData.tin}
                  onChange={(e) => setFormData({ ...formData, tin: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="123-456-789-000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">PhilHealth Accreditation</label>
                <input
                  type="text"
                  value={formData.philhealth_accreditation}
                  onChange={(e) => setFormData({ ...formData, philhealth_accreditation: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="PH-12345"
                />
              </div>
            </div>
          </div>

          {/* Invoice Settings */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded-lg text-sm mr-2">📄</span>
              Invoice Settings
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Invoice Prefix</label>
                <input
                  type="text"
                  value={formData.invoice_prefix}
                  onChange={(e) => setFormData({ ...formData, invoice_prefix: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="INV"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Authorized Signatory</label>
                <input
                  type="text"
                  value={formData.authorized_signatory}
                  onChange={(e) => setFormData({ ...formData, authorized_signatory: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Dr. Juan Dela Cruz"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Signatory Title</label>
                <input
                  type="text"
                  value={formData.signatory_title}
                  onChange={(e) => setFormData({ ...formData, signatory_title: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Hospital Administrator"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Logo URL</label>
                <input
                  type="url"
                  value={formData.logo_url}
                  onChange={(e) => setFormData({ ...formData, logo_url: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="https://example.com/logo.png"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">Invoice Footer</label>
                <textarea
                  value={formData.invoice_footer}
                  onChange={(e) => setFormData({ ...formData, invoice_footer: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  rows={3}
                  placeholder="Payment terms, bank details, etc."
                />
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="px-8 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl hover:from-blue-700 hover:to-cyan-700 transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </form>
      </div>
    </Layout>
  )
}

