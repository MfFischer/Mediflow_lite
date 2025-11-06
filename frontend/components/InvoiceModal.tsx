import { useState, useEffect } from 'react'
import axios from 'axios'

interface InvoiceModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  invoice?: any
}

interface InvoiceItem {
  description: string
  category: string
  quantity: number
  unit_price: number
  doctor_name?: string
  doctor_license?: string
}

export default function InvoiceModal({ isOpen, onClose, onSuccess, invoice }: InvoiceModalProps) {
  const [formData, setFormData] = useState({
    patient_id: '',
    appointment_id: '',
    due_date: '',
    tax_rate: 0,
    discount_amount: 0,
    philhealth_coverage: 0,
    hmo_coverage: 0,
    senior_pwd_discount: 0,
    notes: '',
    status: 'pending'
  })
  const [items, setItems] = useState<InvoiceItem[]>([
    { description: '', category: 'other', quantity: 1, unit_price: 0 }
  ])
  const [patients, setPatients] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      fetchPatients()
    }
  }, [isOpen])

  useEffect(() => {
    if (invoice) {
      setFormData({
        patient_id: invoice.patient_id || '',
        appointment_id: invoice.appointment_id || '',
        due_date: invoice.due_date ? invoice.due_date.slice(0, 10) : '',
        tax_rate: invoice.tax_rate || 0,
        discount_amount: invoice.discount_amount || 0,
        notes: invoice.notes || '',
        status: invoice.status || 'pending'
      })
      if (invoice.items && invoice.items.length > 0) {
        setItems(invoice.items.map((item: any) => ({
          description: item.description,
          quantity: item.quantity,
          unit_price: parseFloat(item.unit_price)
        })))
      }
    } else {
      setFormData({
        patient_id: '',
        appointment_id: '',
        due_date: '',
        tax_rate: 0,
        discount_amount: 0,
        notes: '',
        status: 'pending'
      })
      setItems([
        { description: '', quantity: 1, unit_price: 0 }
      ])
    }
  }, [invoice])

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

  const addItem = () => {
    setItems([...items, { description: '', category: 'other', quantity: 1, unit_price: 0 }])
  }

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index))
  }

  const updateItem = (index: number, field: keyof InvoiceItem, value: string | number) => {
    const updated = [...items]
    updated[index][field] = value as never
    setItems(updated)
  }

  const calculateSubtotal = () => {
    return items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0)
  }

  const calculateTax = () => {
    return calculateSubtotal() * (formData.tax_rate / 100)
  }

  const calculateTotal = () => {
    return calculateSubtotal() + calculateTax() - formData.discount_amount
  }

  const calculatePatientBalance = () => {
    const total = calculateTotal()
    return total - formData.philhealth_coverage - formData.hmo_coverage - formData.senior_pwd_discount
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const token = localStorage.getItem('token')
      const url = invoice
        ? `http://localhost:8000/api/v1/billing/${invoice.id}`
        : 'http://localhost:8000/api/v1/billing/'

      const method = invoice ? 'put' : 'post'

      await axios[method](url, {
        ...formData,
        patient_id: parseInt(formData.patient_id),
        appointment_id: formData.appointment_id ? parseInt(formData.appointment_id) : null,
        items: items.filter(item => item.description.trim() !== '')
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })

      onSuccess()
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save invoice')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-gradient-to-r from-blue-500 to-cyan-500 text-white p-6 rounded-t-2xl">
          <h2 className="text-2xl font-bold">{invoice ? 'Edit Invoice' : 'Create Invoice'}</h2>
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
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                <label className="block text-sm font-medium text-gray-700 mb-2">Due Date *</label>
                <input
                  type="date"
                  required
                  value={formData.due_date}
                  onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Status *</label>
                <select
                  required
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="pending">Pending</option>
                  <option value="paid">Paid</option>
                  <option value="overdue">Overdue</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>
            </div>
          </div>

          {/* Invoice Items */}
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Invoice Items</h3>
              <button
                type="button"
                onClick={addItem}
                className="bg-blue-100 text-blue-600 px-4 py-2 rounded-lg hover:bg-blue-200 transition-colors text-sm font-medium"
              >
                + Add Item
              </button>
            </div>

            <div className="space-y-4">
              {items.map((item, index) => (
                <div key={index} className="border border-gray-200 rounded-xl p-4 relative">
                  {items.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeItem(index)}
                      className="absolute top-2 right-2 text-red-500 hover:text-red-700"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Category *</label>
                      <select
                        required
                        value={item.category}
                        onChange={(e) => updateItem(index, 'category', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="professional_fee">Professional Fee</option>
                        <option value="laboratory">Laboratory</option>
                        <option value="medication">Medication</option>
                        <option value="room_charge">Room Charge</option>
                        <option value="procedure">Procedure</option>
                        <option value="supplies">Supplies</option>
                        <option value="other">Other</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Description *</label>
                      <input
                        type="text"
                        required
                        value={item.description}
                        onChange={(e) => updateItem(index, 'description', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="e.g., Consultation fee"
                      />
                    </div>
                  </div>

                  {item.category === 'professional_fee' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Doctor Name</label>
                        <input
                          type="text"
                          value={item.doctor_name || ''}
                          onChange={(e) => updateItem(index, 'doctor_name', e.target.value)}
                          className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="Dr. Juan Dela Cruz"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">PRC License Number</label>
                        <input
                          type="text"
                          value={item.doctor_license || ''}
                          onChange={(e) => updateItem(index, 'doctor_license', e.target.value)}
                          className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="PRC License #"
                        />
                      </div>
                    </div>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Quantity *</label>
                      <input
                        type="number"
                        required
                        min="1"
                        value={item.quantity}
                        onChange={(e) => updateItem(index, 'quantity', parseInt(e.target.value))}
                        className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Unit Price (₱) *</label>
                      <input
                        type="number"
                        required
                        min="0"
                        step="0.01"
                        value={item.unit_price}
                        onChange={(e) => updateItem(index, 'unit_price', parseFloat(e.target.value))}
                        className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Amount</label>
                      <div className="w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-xl text-gray-700 font-semibold">
                        ₱{(item.quantity * item.unit_price).toFixed(2)}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Calculations */}
          <div className="bg-gray-50 rounded-xl p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Tax Rate (%)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.01"
                  value={formData.tax_rate}
                  onChange={(e) => setFormData({ ...formData, tax_rate: parseFloat(e.target.value) || 0 })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Discount (₱)</label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.discount_amount}
                  onChange={(e) => setFormData({ ...formData, discount_amount: parseFloat(e.target.value) || 0 })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Philippine Insurance Coverage */}
            <div className="border-t border-gray-300 pt-4 mb-4">
              <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-xs mr-2">🇵🇭</span>
                Insurance Coverage
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">PhilHealth (₱)</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.philhealth_coverage}
                    onChange={(e) => setFormData({ ...formData, philhealth_coverage: parseFloat(e.target.value) || 0 })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="PhilHealth coverage"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">HMO Coverage (₱)</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.hmo_coverage}
                    onChange={(e) => setFormData({ ...formData, hmo_coverage: parseFloat(e.target.value) || 0 })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="HMO coverage"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Senior/PWD Discount (₱)</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.senior_pwd_discount}
                    onChange={(e) => setFormData({ ...formData, senior_pwd_discount: parseFloat(e.target.value) || 0 })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="20% discount"
                  />
                </div>
              </div>
            </div>

            <div className="space-y-2 text-right">
              <div className="flex justify-between text-gray-700">
                <span>Subtotal:</span>
                <span className="font-semibold">₱{calculateSubtotal().toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-gray-700">
                <span>Tax ({formData.tax_rate}%):</span>
                <span className="font-semibold">₱{calculateTax().toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-gray-700">
                <span>Discount:</span>
                <span className="font-semibold">-₱{formData.discount_amount.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-green-700 bg-green-50 px-3 py-2 rounded-lg">
                <span>PhilHealth Coverage:</span>
                <span className="font-semibold">-₱{formData.philhealth_coverage.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-green-700 bg-green-50 px-3 py-2 rounded-lg">
                <span>HMO Coverage:</span>
                <span className="font-semibold">-₱{formData.hmo_coverage.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-green-700 bg-green-50 px-3 py-2 rounded-lg">
                <span>Senior/PWD Discount:</span>
                <span className="font-semibold">-₱{formData.senior_pwd_discount.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-xl font-bold text-blue-900 pt-2 border-t-2 border-blue-300 bg-blue-50 px-3 py-2 rounded-lg">
                <span>Patient Balance:</span>
                <span>₱{calculatePatientBalance().toFixed(2)}</span>
              </div>
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Notes</label>
            <textarea
              rows={3}
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Payment terms, special instructions, etc."
            />
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
              className="px-6 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-xl hover:shadow-lg transition-all disabled:opacity-50"
            >
              {loading ? 'Saving...' : invoice ? 'Update Invoice' : 'Create Invoice'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

