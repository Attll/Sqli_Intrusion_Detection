import React, { useState } from 'react'
import { Shield, Send, AlertTriangle, CheckCircle, Loader2 } from 'lucide-react'
import Card from '../common/Card'
import Button from '../common/Button'
import Badge from '../common/Badge'
import CodeBlock from '../common/CodeBlock'
import { api } from '../../services/api'
import toast from 'react-hot-toast'

const ProtectedDemo = () => {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const sampleQueries = {
    safe: "SELECT * FROM products WHERE id = 1",
    malicious: "' OR '1'='1"
  }

  const handleTest = async () => {
    if (!query.trim()) {
      toast.error('Please enter a query')
      return
    }

    setIsLoading(true)
    try {
      const response = await api.post('/demo/protected', {
        query,
        use_ensemble: false,
        xai_method: 'lime',
        explanation_style: 'simple'
      })
      setResult(response.data)
      
      if (response.data.is_malicious) {
        toast.error('Attack Blocked!')
      } else {
        toast.success('Query Allowed')
      }
    } catch (error) {
      toast.error('Test failed: ' + error.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <Card>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
            <Shield className="w-5 h-5 text-green-500" />
          </div>
          <div>
            <h3 className="text-lg font-semibold">Protected Mode</h3>
            <p className="text-sm text-gray-400">Queries are analyzed and blocked if malicious</p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Enter SQL Query</label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your SQL query here..."
              className="input w-full h-32 resize-none font-mono text-sm"
            />
          </div>

          <div className="flex items-center gap-2">
            <Button onClick={handleTest} isLoading={isLoading}>
              <Send className="w-4 h-4" />
              Test Query
            </Button>
            <Button
              variant="secondary"
              onClick={() => setQuery(sampleQueries.safe)}
            >
              Load Safe Example
            </Button>
            <Button
              variant="secondary"
              onClick={() => setQuery(sampleQueries.malicious)}
            >
              Load Attack Example
            </Button>
          </div>
        </div>
      </Card>

      {/* Result Section */}
      {result && (
        <Card>
          <div className="space-y-6">
            {/* Status */}
            <div className={`p-4 rounded-lg border ${
              result.is_malicious
                ? 'bg-red-500/10 border-red-500/20'
                : 'bg-green-500/10 border-green-500/20'
            }`}>
              <div className="flex items-start gap-3">
                {result.is_malicious ? (
                  <AlertTriangle className="w-6 h-6 text-red-500 flex-shrink-0 mt-1" />
                ) : (
                  <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0 mt-1" />
                )}
                <div className="flex-1">
                  <h4 className="font-semibold mb-2">
                    {result.is_malicious ? '🚨 Attack Detected & Blocked' : '✅ Query Allowed'}
                  </h4>
                  <p className="text-sm text-gray-300">
                    Confidence: <span className="font-bold">{(result.confidence_score * 100).toFixed(2)}%</span>
                  </p>
                  {result.attack_type && (
                    <p className="text-sm text-gray-300">
                      Attack Type: <Badge variant="danger">{result.attack_type}</Badge>
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* XAI Explanation */}
            <div>
              <h4 className="font-semibold mb-3">🤖 AI Explanation</h4>
              <div className="bg-dark-surface border border-dark-border rounded-lg p-4">
                <p className="text-sm text-gray-300 leading-relaxed">
                  {result.gemini_explanation}
                </p>
              </div>
            </div>

            {/* Feature Importance */}
            {result.xai_output && result.xai_output.top_features && (
              <div>
                <h4 className="font-semibold mb-3">🔍 Key Detection Factors</h4>
                <div className="space-y-2">
                  {result.xai_output.top_features.slice(0, 5).map((feature, idx) => (
                    <div
                      key={idx}
                      className="flex items-center gap-3 p-3 bg-dark-surface rounded-lg"
                    >
                      <div className="flex-1">
                        <p className="text-sm font-mono">{feature.feature}</p>
                      </div>
                      <div className="w-32 bg-dark-bg rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            feature.importance > 0 ? 'bg-red-500' : 'bg-green-500'
                          }`}
                          style={{ width: `${Math.abs(feature.importance) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-400 w-16 text-right">
                        {(Math.abs(feature.importance) * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Metadata */}
            <div className="grid grid-cols-3 gap-4 pt-4 border-t border-dark-border">
              <div>
                <p className="text-xs text-gray-400">Model Used</p>
                <p className="text-sm font-medium">{result.model_used}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400">Processing Time</p>
                <p className="text-sm font-medium">{result.processing_time_ms.toFixed(2)}ms</p>
              </div>
              <div>
                <p className="text-xs text-gray-400">XAI Method</p>
                <p className="text-sm font-medium">{result.xai_output?.method || 'N/A'}</p>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}

export default ProtectedDemo
