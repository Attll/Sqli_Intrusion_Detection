import React from 'react'
import { Shield, AlertTriangle, Activity, Clock } from 'lucide-react'
import StatsCard from '../components/dashboard/StatsCard'
import AttackTimeline from '../components/dashboard/AttackTimeline'
import RecentAttacks from '../components/dashboard/RecentAttacks'
import AttackDistribution from '../components/dashboard/AttackDistribution'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { useApi } from '../hooks/useApi'

const Dashboard = () => {
  const { useDashboard } = useApi()
  const { data, isLoading, error } = useDashboard(7)

  if (isLoading) return <LoadingSpinner text="Loading dashboard..." />
  if (error) return <div>Error loading dashboard</div>

  const stats = data?.attack_stats || {}
  const timelineData = data?.timeline_data || {}
  const attackDistribution = data?.attack_distribution || []

  // Format timeline data for chart
  const chartData = timelineData.timestamps?.map((timestamp, idx) => ({
    timestamp,
    malicious: timelineData.malicious?.[idx] || 0,
    benign: timelineData.benign?.[idx] || 0,
  })) || []

  // Mock recent attacks (in real app, fetch from API)
  const recentAttacks = [
    {
      id: 1,
      query: "' OR '1'='1",
      attack_type: 'Boolean-based SQLi',
      confidence_score: 0.98,
      created_at: new Date(Date.now() - 300000),
    },
    {
      id: 2,
      query: "' UNION SELECT NULL--",
      attack_type: 'Union-based SQLi',
      confidence_score: 0.95,
      created_at: new Date(Date.now() - 600000),
    },
    {
      id: 3,
      query: "'; DROP TABLE users--",
      attack_type: 'Stacked Queries',
      confidence_score: 0.99,
      created_at: new Date(Date.now() - 900000),
    },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
        <p className="text-gray-400">Real-time SQL injection detection overview</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Requests"
          value={stats.total_requests?.toLocaleString() || '0'}
          change={12}
          icon={Activity}
          trend="up"
        />
        <StatsCard
          title="Attacks Blocked"
          value={stats.malicious_requests?.toLocaleString() || '0'}
          change={-8}
          icon={Shield}
          trend="down"
        />
        <StatsCard
          title="Attack Rate"
          value={`${stats.attack_rate || 0}%`}
          change={5}
          icon={AlertTriangle}
          trend="up"
        />
        <StatsCard
          title="Avg Confidence"
          value={`${((stats.avg_confidence || 0) * 100).toFixed(1)}%`}
          icon={Clock}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AttackTimeline data={chartData} />
        <AttackDistribution data={attackDistribution} />
      </div>

      {/* Recent Attacks */}
      <RecentAttacks attacks={recentAttacks} />
    </div>
  )
}

export default Dashboard
