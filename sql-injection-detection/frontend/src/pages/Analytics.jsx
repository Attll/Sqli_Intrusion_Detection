import React from 'react'
import ModelComparison from '../components/analytics/ModelComparison'
import AttackHeatmap from '../components/analytics/AttackHeatmap'
import TopEndpoints from '../components/analytics/TopEndpoints'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { useApi } from '../hooks/useApi'

const Analytics = () => {
  const { useDashboard } = useApi()
  const { data, isLoading } = useDashboard(30)

  if (isLoading) return <LoadingSpinner text="Loading analytics..." />

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Analytics</h1>
        <p className="text-gray-400">Detailed insights and performance metrics</p>
      </div>

      {/* Model Performance */}
      <ModelComparison data={data?.model_performance || []} />

      {/* Heatmap & Endpoints */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <AttackHeatmap data={data?.heatmap_data || { hours: [], days: [], values: [] }} />
        </div>
        <TopEndpoints endpoints={data?.top_endpoints || []} />
      </div>
    </div>
  )
}

export default Analytics
