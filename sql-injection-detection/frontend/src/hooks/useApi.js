import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'

export const useApi = () => {
  const queryClient = useQueryClient()

  // Fetch dashboard data
  const useDashboard = (days = 7) => {
    return useQuery({
      queryKey: ['dashboard', days],
      queryFn: async () => {
        const { data } = await api.get(`/analytics/dashboard?days=${days}`)
        return data
      },
    })
  }

  // Fetch logs
  const useLogs = (filters = {}) => {
    return useQuery({
      queryKey: ['logs', filters],
      queryFn: async () => {
        const params = new URLSearchParams()
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== null && value !== undefined) {
            params.append(key, value)
          }
        })
        const { data } = await api.get(`/logs?${params}`)
        return data
      },
    })
  }

  // Fetch models
  const useModels = () => {
    return useQuery({
      queryKey: ['models'],
      queryFn: async () => {
        const { data } = await api.get('/models')
        return data
      },
    })
  }

  // Detect mutation
  const useDetect = () => {
    return useMutation({
      mutationFn: async (payload) => {
        const { data } = await api.post('/detect/detect', payload)
        return data
      },
      onSuccess: () => {
        queryClient.invalidateQueries(['logs'])
        queryClient.invalidateQueries(['dashboard'])
      },
    })
  }

  // Activate model mutation
  const useActivateModel = () => {
    return useMutation({
      mutationFn: async (modelId) => {
        const { data } = await api.post(`/models/activate/${modelId}`)
        return data
      },
      onSuccess: () => {
        queryClient.invalidateQueries(['models'])
      },
    })
  }

  return {
    useDashboard,
    useLogs,
    useModels,
    useDetect,
    useActivateModel,
  }
}
