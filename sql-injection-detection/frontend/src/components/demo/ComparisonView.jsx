import React, { useState } from 'react'
import { GitCompare, Send } from 'lucide-react'
import Card from '../common/Card'
import Button from '../common/Button'
import { api } from '../../services/api'
import toast from 'react-hot-toast'

const ComparisonView = () => {
  const [query, setQuery] = useState("' OR '1'='1")
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleCompare = async () => {
    if (!query.trim()) {
      toast.error('Please enter a query')
      return
    }

    setIsLoading(true)
    try {
      const response = await api.post('/demo/compare', {
        query,
        use_ensemble: false,
        xai_method: 'lime',
        explanation_style: 'simple'
      })
      setResult(response.data)
    } catch (error) {
      toast.error('Comparison failed: ' + error.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
            <GitCompare className="w-5 h-5 text-purple-500" />
          </div>
          <div>
            <h3 className="text-lg font-semibold">Side-by-Side Comparison</h3>
            <p className="text-sm text-gray-400">See the difference between protected and vulnerable execution</p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">SQL Query</label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="input w-full h-24 resize-none font-mono text-sm"
            />
          </div>

          <Button onClick={handleCompare} isLoading={isLoading}>
            <Send className="w-4 h-4" />
            Compare Execution
          </Button>
        </div>
      </Card>

      {result && (
        <div className="grid grid-cols-2 gap-6">
          {/* Protected */}
          <Card className="border-green-500/20">
            <h4 className="font-semibold text-green-500 mb-4">✅ Protected Mode</h4>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-gray-400">Status</p>
                <p className="text-sm font-medium">
                  {result.protected.blocked ? '🛡️ Attack Blocked' : '✅ Query Allowed'}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-400">Confidence</p>
                <p className="text-sm font-medium">{(result.protected.confidence * 100).toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-xs text-gray-400">Data Protected</p>
                <p className="text-sm font-medium text-green-500">
                  {result.protected.data_protected ? 'Yes ✓' : 'No'}
                </p>
              </div>
              <div className="pt-3 border-t border-dark-border">
                <p className="text-xs text-gray-400 mb-2">Explanation</p>
                <p className="text-sm text-gray-300">{result.protected.explanation}</p>
              </div>
            </div>
          </Card>

          {/* Vulnerable */}
          <Card className="border-red-500/20">
            <h4 className="font-semibold text-red-500 mb-4">⚠️ Vulnerable Mode</h4>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-gray-400">Status</p>
                <p className="text-sm font-medium">
                  {result.vulnerable.attack_successful ? '❌ Attack Successful' : 'Query Executed'}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-400">Data Leaked</p>
                <p className="text-sm font-medium">
                  {result.vulnerable.data_leaked?.length || 0} records
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-400">Impact</p>
                <p className="text-sm font-medium text-red-500">{result.vulnerable.impact}</p>
              </div>
              {result.vulnerable.data_leaked && result.vulnerable.data_leaked.length > 0 && (
                <div className="pt-3 border-t border-dark-border">
                  <p className="text-xs text-gray-400 mb-2">Sample Leaked Data</p>
                  <div className="bg-dark-bg rounded p-2 text-xs font-mono">
                    {JSON.stringify(result.vulnerable.data_leaked[0], null, 2)}
                  </div>
                </div>
              )}
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}

export default ComparisonView
