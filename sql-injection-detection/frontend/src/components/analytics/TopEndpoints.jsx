import React from 'react'
import { Target, TrendingUp } from 'lucide-react'
import Card from '../common/Card'
import { formatDistanceToNow } from 'date-fns'

const TopEndpoints = ({ endpoints }) => {
  const maxCount = Math.max(...endpoints.map(e => e.attack_count))

  return (
    <Card>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold">Most Targeted Endpoints</h3>
        <Target className="w-5 h-5 text-gray-400" />
      </div>

      <div className="space-y-3">
        {endpoints.map((endpoint, idx) => (
          <div
            key={idx}
            className="p-4 bg-dark-surface rounded-lg border border-dark-border hover:border-red-500/30 transition-colors"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-sm font-medium">{endpoint.endpoint}</span>
              <span className="text-sm font-bold text-red-500">{endpoint.attack_count}</span>
            </div>

            {/* Progress bar */}
            <div className="w-full bg-dark-bg rounded-full h-2 mb-2">
              <div
                className="bg-red-500 h-2 rounded-full transition-all"
                style={{ width: `${(endpoint.attack_count / maxCount) * 100}%` }}
              />
            </div>

            <p className="text-xs text-gray-400">
              Last attack: {formatDistanceToNow(new Date(endpoint.last_attack), { addSuffix: true })}
            </p>
          </div>
        ))}
      </div>
    </Card>
  )
}

export default TopEndpoints
