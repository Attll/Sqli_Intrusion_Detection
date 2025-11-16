import React, { useState } from 'react'
import { Download, RefreshCw } from 'lucide-react'
import Card from '../components/common/Card'
import Button from '../components/common/Button'
import LogsTable from '../components/logs/LogsTable'
import LogDetails from '../components/logs/LogDetails'
import LogFilters from '../components/logs/LogFilters'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { useApi } from '../hooks/useApi'
import { api } from '../services/api'
import toast from 'react-hot-toast'

const Logs = () => {
  const [filters, setFilters] = useState({
    is_malicious: null,
    model_used: null,
    min_confidence: null,
    search_query: null,
    skip: 0,
    limit: 50,
  })
  const [selectedLog, setSelectedLog] = useState(null)
  const [isDetailsOpen, setIsDetailsOpen] = useState(false)

  const { useLogs } = useApi()
  const { data, isLoading, refetch } = useLogs(filters)

  const handleViewDetails = (log) => {
    setSelectedLog(log)
    setIsDetailsOpen(true)
  }

  const handleExport = async (format) => {
    try {
      const response = await api.get(`/logs/export/${format}`, {
        responseType: 'blob',
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `logs.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      
      toast.success(`Logs exported as ${format.toUpperCase()}`)
    } catch (error) {
      toast.error('Export failed')
    }
  }

  const handleResetFilters = () => {
    setFilters({
      is_malicious: null,
      model_used: null,
      min_confidence: null,
      search_query: null,
      skip: 0,
      limit: 50,
    })
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Request Logs</h1>
          <p className="text-gray-400">View and analyze detection history</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => refetch()}>
            <RefreshCw className="w-4 h-4" />
            Refresh
          </Button>
          <Button variant="secondary" onClick={() => handleExport('csv')}>
            <Download className="w-4 h-4" />
            CSV
          </Button>
          <Button variant="secondary" onClick={() => handleExport('json')}>
            <Download className="w-4 h-4" />
            JSON
          </Button>
        </div>
      </div>

      {/* Filters */}
      <LogFilters filters={filters} setFilters={setFilters} onReset={handleResetFilters} />

      {/* Table */}
      <Card>
        {isLoading ? (
          <LoadingSpinner />
        ) : (
          <>
            <LogsTable logs={data?.logs || []} onViewDetails={handleViewDetails} />
            
            {/* Pagination */}
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-dark-border">
              <p className="text-sm text-gray-400">
                Showing {data?.logs?.length || 0} of {data?.total || 0} logs
              </p>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  disabled={filters.skip === 0}
                  onClick={() => setFilters({ ...filters, skip: Math.max(0, filters.skip - filters.limit) })}
                >
                  Previous
                </Button>
                <Button
                  variant="secondary"
                  disabled={filters.skip + filters.limit >= (data?.total || 0)}
                  onClick={() => setFilters({ ...filters, skip: filters.skip + filters.limit })}
                >
                  Next
                </Button>
              </div>
            </div>
          </>
        )}
      </Card>

      {/* Log Details Modal */}
      <LogDetails
        log={selectedLog}
        isOpen={isDetailsOpen}
        onClose={() => setIsDetailsOpen(false)}
        onFeedbackSubmitted={() => {
          refetch()
          toast.success('Thank you for your feedback!')
        }}
      />
    </div>
  )
}

export default Logs
