import api from '../utils/api'

export interface Patient {
  id: number
  first_name: string
  last_name: string
  date_of_birth: string
  email: string
  phone_number: string
}

export interface PatientCreate {
  first_name: string
  last_name: string
  date_of_birth: string
  email: string
  phone_number: string
}

export interface PatientUpdate {
  first_name?: string
  last_name?: string
  date_of_birth?: string
  email?: string
  phone_number?: string
}

export interface PatientListResponse {
  total: number
  page: number
  page_size: number
  patients: Patient[]
}

export const patientService = {
  async list(page: number = 1, pageSize: number = 20, search?: string): Promise<PatientListResponse> {
    const params: any = { page, page_size: pageSize }
    if (search) {
      params.search = search
    }
    const response = await api.get<PatientListResponse>('/api/v1/patients/', { params })
    return response.data
  },

  async get(id: number): Promise<Patient> {
    const response = await api.get<Patient>(`/api/v1/patients/${id}`)
    return response.data
  },

  async create(data: PatientCreate): Promise<Patient> {
    const response = await api.post<Patient>('/api/v1/patients/', data)
    return response.data
  },

  async update(id: number, data: PatientUpdate): Promise<Patient> {
    const response = await api.put<Patient>(`/api/v1/patients/${id}`, data)
    return response.data
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/api/v1/patients/${id}`)
  },
}

