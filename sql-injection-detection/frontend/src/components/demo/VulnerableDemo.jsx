import React, { useState } from 'react'
import { AlertTriangle, Send, Database, Eye } from 'lucide-react'
import Card from '../common/Card'
import Button from '../common/Button'
import CodeBlock from '../common/CodeBlock'
import { api } from '../../services/api'
import toast from 'react-hot-toast'

const VulnerableDemo = () => {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const sampleAttacks = {
    union: "' UNION SELECT username, password FROM users--",
    boolean: "' OR '1'='1",
    drop: "'; DROP TABLE users--"
  }

  const handleExecute = async () => {
    if (!query.trim()) {
      toast.error('Please enter a query')
      return
    }

    setIsLoading(true)
    try {
      const response = await api.post('/demo/vulnerable', {
        query
      })
      setResult(response.data)
      
      if (response.data.attack_successful) {
        toast.error('Attack Successful - Data Compromised!')
      }
    } catch (error) {
      toast.error('Execution failed: ' + error.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Warning Banner */}
      <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-red-500 mb-1">Vulnerable Demo Environment</h4>
            <p className="text-sm text-gray-300">
              This demo executes queries WITHOUT protection to demonstrate SQL injection impact.
              Only for educational purposes with mock data.
            </p>
          </div>
        </div>
      </div>

      {/* Input Section */}
      <Card>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center">
            <Database className="w-5 h-5 text-red-500" />
          </div>
          <div>
            <h3 className="text-lg font-semibold">Vulnerable Mode</h3>
            <p className="text-sm text-gray-400">Execute queries without any protection</p>
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
            <Button onClick={handleExecute} isLoading={isLoading} variant="danger">
              <Send className="w-4 h-4" />
              Execute (Unprotected)
            </Button>
            <Button
              variant="secondary"
              onClick={() => setQuery(sampleAttacks.union)}
            >
              UNION Attack
            </Button>
            <Button
              variant="secondary"
              onClick={() => setQuery(sampleAttacks.boolean)}
            >
              Boolean Attack
            </Button>
          </div>
        </div>
      </Card>

      {/* Result Section */}
      {result && (
        <Card>
          <div className="space-y-6">
            {/* Attack Status */}
            <div className={`p-4 rounded-lg border ${
              result.attack_successful
                ? 'bg-red-500/10 border-red-500/20'
                : 'bg-yellow-500/10 border-yellow-500/20'
            }`}>
              <div className="flex items-start gap-3">
                <AlertTriangle className={`w-6 h-6 flex-shrink-0 mt-1 ${
                  result.attack_successful ? 'text-red-500' : 'text-yellow-500'
                }`} />
                <div className="flex-1">
                  <h4 className="font-semibold mb-2">
                    {result.attack_successful ? '⚠️ CRITICAL: Attack Successful!' : 'Query Executed'}
                  </h4>
                  <p className="text-sm text-gray-300">{result.impact_description}</p>
                </div>
              </div>
            </div>

            {/* Leaked Data */}
            {result.data_leaked && result.data_leaked.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Eye className="w-5 h-5 text-red-500" />
                  <h4 className="font-semibold text-red-500">Exposed Data (Sample)</h4>
                </div>
                <div className="bg-dark-surface border border-red-500/20 rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <thead className="bg-red-500/10 border-b border-red-500/20">
                      <tr>
                        {Object.keys(result.data_leaked[0]).map((key) => (
                          <th key={key} className="px-4 py-2 text-left font-medium">
                            {key}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {result.data_leaked.map((row, idx) => (
                        <tr key={idx} className="border-b border-dark-border last:border-0">
                          {Object.values(row).map((value, vidx) => (
                            <td key={vidx} className="px-4 py-2 font-mono text-xs">
                              {value || 'NULL'}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <p className="text-xs text-red-400 mt-2">
                  ⚠️ In a real attack, this sensitive data would be stolen by hackers!
                </p>
              </div>
            )}

            {/* Query Executed */}
            <div>
              <h4 className="font-semibold mb-3">Executed Query</h4>
              <CodeBlock code={result.query_executed} />
            </div>

            {/* Educational Note */}
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
              <h4 className="font-semibold text-blue-400 mb-2">💡 Why This Happened</h4>
              <p className="text-sm text-gray-300">
                Without proper input validation and parameterized queries, attackers can:
              </p>
              <ul className="list-disc list-inside text-sm text-gray-300 mt-2 space-y-1">
                <li>Extract sensitive data (usernames, passwords, credit cards)</li>
                <li>Modify or delete database records</li>
                <li>Bypass authentication and authorization</li>
                <li>Execute administrative operations</li>
              </ul>
              <p className="text-sm text-gray-300 mt-3">
                ✅ The protected demo prevents all these attacks using ML-based detection!
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}

export default VulnerableDemo
