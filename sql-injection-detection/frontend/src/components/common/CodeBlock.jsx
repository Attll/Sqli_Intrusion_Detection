import React, { useState } from 'react'
import { Copy, Check } from 'lucide-react'

const CodeBlock = ({ code, language = 'sql' }) => {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="relative group">
      <pre className="bg-dark-elevated border border-dark-border rounded-lg p-4 overflow-x-auto">
        <code className="text-sm font-mono text-gray-300">{code}</code>
      </pre>
      <button
        onClick={handleCopy}
        className="absolute top-2 right-2 p-2 bg-dark-surface border border-dark-border rounded-md hover:bg-dark-hover transition-colors opacity-0 group-hover:opacity-100"
      >
        {copied ? (
          <Check className="w-4 h-4 text-green-500" />
        ) : (
          <Copy className="w-4 h-4" />
        )}
      </button>
    </div>
  )
}

export default CodeBlock
