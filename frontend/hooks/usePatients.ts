import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../utils/api'
import { parseApiError, logError } from '../utils/errorHandler'

export interface Patient {
  id: number
  first_name: string
  last_name: string
  date_of_birth: string
  gender?: string
  email: string
  phone_number: string
  address?: string
  philhealth_number?: string
  hmo_provider?: string
  created_at: string
  updated_at: string
}

export interface PatientsResponse {
  patients: Patient[]
  total: number
  page: number
  page_size: number
}

export interface PatientFilters {
  page?: number
  page_size?: number
  search?: string
}

/**
 * Fetch patients with pagination and search
 */
export function usePatients(filters: PatientFilters = {}) {
  return useQuery({
    queryKey: ['patients', filters],
    queryFn: async () => {
      const response = await api.get<PatientsResponse>('/api/v1/patients/', {
        params: filters,
      })
      return response.data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
    onError: (error) => {
      logError(error, { context: 'usePatients', filters })
    },
  })
}

/**
 * Fetch single patient by ID
 */
export function usePatient(patientId: number | null) {
  return useQuery({
    queryKey: ['patient', patientId],
    queryFn: async () => {
      if (!patientId) throw new Error('Patient ID is required')
      const response = await api.get<Patient>(`/api/v1/patients/${patientId}`)
      return response.data
    },
    enabled: !!patientId,
    staleTime: 5 * 60 * 1000,
    onError: (error) => {
      logError(error, { context: 'usePatient', patientId })
    },
  })
}

/**
 * Create new patient
 */
export function useCreatePatient() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (patientData: Partial<Patient>) => {
      const response = await api.post<Patient>('/api/v1/patients/', patientData)
      return response.data
    },
    onSuccess: () => {
      // Invalidate patients list to refetch
      queryClient.invalidateQueries({ queryKey: ['patients'] })
    },
    onError: (error) => {
      logError(error, { context: 'useCreatePatient' })
    },
  })
}

/**
 * Update existing patient
 */
export function useUpdatePatient() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<Patient> }) => {
      const response = await api.put<Patient>(`/api/v1/patients/${id}`, data)
      return response.data
    },
    onSuccess: (data) => {
      // Update cache for this specific patient
      queryClient.setQueryData(['patient', data.id], data)
      // Invalidate patients list
      queryClient.invalidateQueries({ queryKey: ['patients'] })
    },
    onError: (error) => {
      logError(error, { context: 'useUpdatePatient' })
    },
  })
}

/**
 * Delete patient
 */
export function useDeletePatient() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (patientId: number) => {
      await api.delete(`/api/v1/patients/${patientId}`)
      return patientId
    },
    onSuccess: () => {
      // Invalidate patients list
      queryClient.invalidateQueries({ queryKey: ['patients'] })
    },
    onError: (error) => {
      logError(error, { context: 'useDeletePatient' })
    },
  })
}

/**
 * Search patients (with debouncing)
 */
export function useSearchPatients(searchTerm: string, debounceMs: number = 300) {
  return useQuery({
    queryKey: ['patients', 'search', searchTerm],
    queryFn: async () => {
      if (!searchTerm || searchTerm.length < 2) {
        return { patients: [], total: 0 }
      }
      const response = await api.get<PatientsResponse>('/api/v1/patients/', {
        params: { search: searchTerm, page_size: 10 },
      })
      return response.data
    },
    enabled: searchTerm.length >= 2,
    staleTime: 30 * 1000, // 30 seconds
    onError: (error) => {
      logError(error, { context: 'useSearchPatients', searchTerm })
    },
  })
}

