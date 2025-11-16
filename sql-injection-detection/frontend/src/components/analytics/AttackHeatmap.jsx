import React from 'react'
import Card from '../common/Card'

const AttackHeatmap = ({ data }) => {
  const getColorIntensity = (value, max) => {
    if (value === 0) return 'bg-dark-elevated'
    const intensity = Math.min((value / max) * 100, 100)
    if (intensity < 25) return 'bg-red-500/20'
    if (intensity < 50) return 'bg-red-500/40'
    if (intensity < 75) return 'bg-red-500/60'
    return 'bg-red-500/80'
  }

  const maxValue = Math.max(...data.values.flat())

  return (
    <Card>
      <h3 className="text-lg font-semibold mb-6">Attack Heatmap (Time Analysis)</h3>
      
      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          <div className="flex gap-1 mb-2 ml-16">
            {data.hours.map((hour) => (
              <div key={hour} className="w-8 text-center">
                <span className="text-xs text-gray-400">{hour}</span>
              </div>
            ))}
          </div>

          {data.days.map((day, dayIdx) => (
            <div key={day} className="flex gap-1 items-center mb-1">
              <div className="w-14 text-xs text-gray-400 text-right mr-2">
                {day.slice(0, 3)}
              </div>
              {data.values[dayIdx].map((value, hourIdx) => (
                <div
                  key={hourIdx}
                  className={`w-8 h-8 rounded ${getColorIntensity(value, maxValue)} 
                    flex items-center justify-center cursor-pointer hover:ring-2 
                    hover:ring-white/20 transition-all group relative`}
                  title={`${day} ${data.hours[hourIdx]}:00 - ${value} attacks`}
                >
                  {value > 0 && (
                    <span className="text-xs font-medium">{value}</span>
                  )}
                  
                  {/* Tooltip */}
                  <div className="absolute bottom-full mb-2 hidden group-hover:block z-10">
                    <div className="bg-dark-elevated border border-dark-border rounded px-2 py-1 text-xs whitespace-nowrap">
                      {value} attacks
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-4 mt-6 text-xs text-gray-400">
        <span>Less</span>
        <div className="flex gap-1">
          <div className="w-4 h-4 rounded bg-dark-elevated border border-dark-border" />
          <div className="w-4 h-4 rounded bg-red-500/20" />
          <div className="w-4 h-4 rounded bg-red-500/40" />
          <div className="w-4 h-4 rounded bg-red-500/60" />
          <div className="w-4 h-4 rounded bg-red-500/80" />
        </div>
        <span>More</span>
      </div>
    </Card>
  )
}

export default AttackHeatmap
