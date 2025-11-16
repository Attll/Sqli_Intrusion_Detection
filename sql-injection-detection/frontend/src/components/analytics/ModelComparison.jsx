import React from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import Card from '../common/Card'

const ModelComparison = ({ data }) => {
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-dark-elevated border border-dark-border rounded-lg p-3 shadow-xl">
          <p className="text-sm font-semibold mb-2">{payload[0].payload.model_name}</p>
          {payload.map((entry, index) => (
            <div key={index} className="flex items-center gap-2 text-sm">
              <div
                className="w-3 h-3 rounded"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-gray-400">{entry.name}:</span>
              <span className="font-medium">{(entry.value * 100).toFixed(2)}%</span>
            </div>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <Card>
      <h3 className="text-lg font-semibold mb-6">Model Performance Comparison</h3>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
          <XAxis dataKey="model_name" stroke="#666" style={{ fontSize: '12px' }} />
          <YAxis stroke="#666" style={{ fontSize: '12px' }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Bar dataKey="accuracy" fill="#3b82f6" name="Accuracy" />
          <Bar dataKey="precision" fill="#10b981" name="Precision" />
          <Bar dataKey="recall" fill="#f59e0b" name="Recall" />
          <Bar dataKey="f1_score" fill="#8b5cf6" name="F1 Score" />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  )
}

export default ModelComparison
