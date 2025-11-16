import React, { useState } from 'react'
import { Shield, AlertTriangle, GitCompare } from 'lucide-react'
import ProtectedDemo from '../components/demo/ProtectedDemo'
import VulnerableDemo from '../components/demo/VulnerableDemo'
import ComparisonView from '../components/demo/ComparisonView'

const Demo = () => {
  const [activeTab, setActiveTab] = useState('protected')

  const tabs = [
    { id: 'protected', label: 'Protected', icon: Shield },
    { id: 'vulnerable', label: 'Vulnerable', icon: AlertTriangle },
    { id: 'comparison', label: 'Comparison', icon: GitCompare },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Interactive Demo</h1>
        <p className="text-gray-400">
          Test SQL injection detection with real-time explanations
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-dark-border">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-6 py-3 border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-white text-white'
                : 'border-transparent text-gray-400 hover:text-white'
            }`}
          >
            <tab.icon className="w-5 h-5" />
            <span className="font-medium">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Content */}
      <div>
        {activeTab === 'protected' && <ProtectedDemo />}
        {activeTab === 'vulnerable' && <VulnerableDemo />}
        {activeTab === 'comparison' && <ComparisonView />}
      </div>
    </div>
  )
}

export default Demo
