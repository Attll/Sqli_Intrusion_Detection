import React from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'
import Card from '../common/Card'
import { cn } from '../../utils/helpers'

const StatsCard = ({ title, value, change, icon: Icon, trend = 'up' }) => {
  const isPositive = trend === 'up'

  return (
    <Card className="hover:border-white/10 transition-all cursor-pointer">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-gray-400 mb-1">{title}</p>
          <h3 className="text-3xl font-bold mb-2">{value}</h3>
          {change !== undefined && (
            <div className={cn(
              'flex items-center gap-1 text-sm',
              isPositive ? 'text-green-500' : 'text-red-500'
            )}>
              {isPositive ? (
                <TrendingUp className="w-4 h-4" />
              ) : (
                <TrendingDown className="w-4 h-4" />
              )}
              <span>{Math.abs(change)}%</span>
              <span className="text-gray-400">vs last period</span>
            </div>
          )}
        </div>
        {Icon && (
          <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center">
            <Icon className="w-6 h-6 text-blue-400" />
          </div>
        )}
      </div>
    </Card>
  )
}

export default StatsCard
