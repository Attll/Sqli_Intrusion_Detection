import React, { useState } from 'react'
import { Zap, Play, AlertCircle } from 'lucide-react'
import Card from '../components/common/Card'
import Button from '../components/common/Button'
import { api } from '../services/api'
import toast from 'react-hot-toast'

const StressTest = () => {
  const [numRequests, setNumRequests] = useState(100)
  const [includeBenign, setIncludeBenign] = useState(true)
  const [isRunning, setIsRunning] = useState(false)
  const [result, setResult] = useState(null)

  const handleRunTest = async () => {
    setIsRunning(true)
    setResult(null)

    try {
      // Start test
      const { data: testData } = await api.post('/stress-test/run', {
        num_requests: numRequests,
        include_benign: includeBenign,
      })

      toast.success('Stress test started')

      // Poll for results
      const pollInterval = setInterval(async () => {
        try {
          const { data: status } = await api.get(`/stress-test/status/${testData.test_id}`)

          if (status.status === 'completed') {
            setResult(status.results)
            setIsRunning(false)
            clearInterval(pollInterval)
            toast.success('Stress test completed')
          } else if (status.status === 'failed') {
            toast.error('Stress test failed')
            setIsRunning(false)
            clearInterval(pollInterval)
          }
        } catch (error) {
          console.error('Polling error:', error)
        }
      }, 2000)

      // Cleanup after 5 minutes
      setTimeout(() => {
        clearInterval(pollInterval)
        if (isRunning) {
          setIsRunning(false)
          toast.error('Test timeout')
        }
      }, 300000)
    } catch (error) {
      toast.error('Failed to start test')
      setIsRunning(false)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Stress Test</h1>
        <p className="text-gray-400">Test system performance with bulk requests</p>
      </div>

      {/* Configuration */}
      <Card>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-yellow-500/10 flex items-center justify-center">
            <Zap className="w-5 h-5 text-yellow-500" />
          </div>
          <div>
            <h3 className="text-lg font-semibold">Test Configuration</h3>
            <p className="text-sm text-gray-400">Configure and run stress tests</p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Number of Requests: {numRequests}
            </label>
            <input
              type="range"
              min="10"
              max="1000"
              step="10"
              value={numRequests}
              onChange={(e) => setNumRequests(parseInt(e.target.value))}
              className="w-full"
              disabled={isRunning}
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="includeBenign"
              checked={includeBenign}
              onChange={(e) => setIncludeBenign(e.target.checked)}
              disabled={isRunning}
              className="w-4 h-4"
            />
            <label htmlFor="includeBenign" className="text-sm">
              Include benign queries (30% benign, 70% malicious)
            </label>
          </div>

          <Button onClick={handleRunTest} isLoading={isRunning} disabled={isRunning}>
            <Play className="w-4 h-4" />
            {isRunning ? 'Running Test...' : 'Start Stress Test'}
          </Button>
        </div>
      </Card>

      {/* Results */}
      {result && (
        <Card>
          <h3 className="text-lg font-semibold mb-6">Test Results</h3>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-dark-surface rounded-lg p-4">
              <p className="text-sm text-gray-400 mb-1">Total Requests</p>
              <p className="text-2xl font-bold">{result.total_requests}</p>
            </div>
            <div className="bg-dark-surface rounded-lg p-4">
              <p className="text-sm text-gray-400 mb-1">Accuracy</p>
              <p className="text-2xl font-bold text-green-500">
                {(result.accuracy * 100).toFixed(1)}%
              </p>
            </div>
            <div className="bg-dark-surface rounded-lg p-4">
              <p className="text-sm text-gray-400 mb-1">Avg Time</p>
              <p className="text-2xl font-bold">{result.avg_processing_time_ms.toFixed(0)}ms</p>
            </div>
            <div className="bg-dark-surface rounded-lg p-4">
              <p className="text-sm text-gray-400 mb-1">Throughput</p>
              <p className="text-2xl font-bold">{result.requests_per_second.toFixed(1)}/s</p>
            </div>
          </div>

          <div className="grid grid-cols-4 gap-4">
            <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
              <p className="text-sm text-gray-400 mb-1">True Positives</p>
              <p className="text-xl font-bold text-green-500">{result.true_positives}</p>
            </div>
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
              <p className="text-sm text-gray-400 mb-1">False Positives</p>
              <p className="text-xl font-bold text-red-500">{result.false_positives}</p>
            </div>
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
              <p className="text-sm text-gray-400 mb-1">False Negatives</p>
              <p className="text-xl font-bold text-red-500">{result.false_negatives}</p>
            </div>
            <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
              <p className="text-sm text-gray-400 mb-1">True Negatives</p>
              <p className="text-xl font-bold text-green-500">{result.true_negatives}</p>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}

export default StressTest
