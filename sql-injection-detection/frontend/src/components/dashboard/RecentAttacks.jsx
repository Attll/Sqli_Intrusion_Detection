import React from 'react'
import { AlertTriangle, Clock, Shield } from 'lucide-react'
import Card from '../common/Card'
import Badge from '../common/Badge'
import { formatDistanceToNow } from 'date-fns'

const RecentAttacks = ({ attacks }) => {
  return (
    <Card>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold">Recent Attacks</h3>
        <Badge variant="danger">Live</Badge>
      </div>

      <div className="space-y-4">
        {attacks.map((attack) => (
          <div
            key={attack.id}
            className="flex items-start gap-4 p-4 rounded-lg bg-dark-surface border border-dark-border hover:border-red-500/30 transition-colors"
          >
            <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center flex-shrink-0">
              <AlertTriangle className="w-5 h-5 text-red-500" />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-mono text-sm text-gray-300 truncate">
                  {attack.query}
                </span>
              </div>

              <div className="flex items-center gap-4 text-xs text-gray-400">
                <div className="flex items-center gap-1">
                  <Shield className="w-3 h-3" />
                  <span>{attack.attack_type}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  <span>{formatDistanceToNow(new Date(attack.created_at), { addSuffix: true })}</span>
                </div>
              </div>
            </div>

            <div className="text-right">
              <div className="text-sm font-bold text-red-500">
                {(attack.confidence_score * 100).toFixed(1)}%
              </div>
              <div className="text-xs text-gray-400">confidence</div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}

export default RecentAttacks
