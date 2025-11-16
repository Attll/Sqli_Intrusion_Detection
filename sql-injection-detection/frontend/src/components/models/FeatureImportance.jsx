import React from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import Card from '../common/Card'

const FeatureImportance = ({ modelName, featureImportance }) => {
  const data = Object.entries(featureImportance || {})
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10)
    .map(([feature, importance]) => ({
      feature: feature.length > 20 ? feature.slice(0, 20) + '...' : feature,
      importance: importance * 100,
      fullFeature: feature,
    }))

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-dark-elevated border border-dark-border rounded-lg p-3 shadow-xl">
          <p className="text-sm font-medium">{payload[0].payload.fullFeature}</p>
          <p className="text-sm text-gray-400">
            Importance: {payload[0].value.toFixed(2)}%
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <Card>
      <h3 className="text-lg font-semibold mb-6">
        Feature Importance - {modelName?.replace('_', ' ').toUpperCase()}
      </h3>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
          <XAxis type="number" stroke="#666" style={{ fontSize: '12px' }} />
          <YAxis
            dataKey="feature"
            type="category"
            width={150}
            stroke="#666"
            style={{ fontSize: '11px' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="importance" fill="#3b82f6" />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  )
}

export default FeatureImportance
