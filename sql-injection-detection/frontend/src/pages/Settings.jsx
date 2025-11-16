import React from 'react'
import { Settings as SettingsIcon, Save } from 'lucide-react'
import Card from '../components/common/Card'
import Button from '../components/common/Button'
import { useStore } from '../store/useStore'
import toast from 'react-hot-toast'

const Settings = () => {
  const { settings, updateSettings } = useStore()

  const handleSave = () => {
    toast.success('Settings saved successfully')
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-gray-400">Configure system preferences</p>
      </div>

      {/* Detection Settings */}
      <Card>
        <h3 className="text-lg font-semibold mb-6">Detection Settings</h3>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">
              Confidence Threshold: {settings.confidenceThreshold}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={settings.confidenceThreshold}
              onChange={(e) =>
                updateSettings({ confidenceThreshold: parseFloat(e.target.value) })
              }
              className="w-full"
            />
            <p className="text-xs text-gray-400 mt-1">
              Queries with confidence below this threshold will be flagged for review
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">XAI Method</label>
            <select
              value={settings.xaiMethod}
              onChange={(e) => updateSettings({ xaiMethod: e.target.value })}
              className="input w-full"
            >
              <option value="lime">LIME</option>
              <option value="shap">SHAP</option>
              <option value="feature_importance">Feature Importance</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Explanation Style</label>
            <select
              value={settings.explanationStyle}
              onChange={(e) => updateSettings({ explanationStyle: e.target.value })}
              className="input w-full"
            >
              <option value="simple">Simple</option>
              <option value="technical">Technical</option>
              <option value="detailed">Detailed</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="useEnsemble"
              checked={settings.useEnsemble}
              onChange={(e) => updateSettings({ useEnsemble: e.target.checked })}
              className="w-4 h-4"
            />
            <label htmlFor="useEnsemble" className="text-sm">
              Use ensemble predictions (combines multiple models)
            </label>
          </div>
        </div>
      </Card>

      {/* API Configuration */}
      <Card>
        <h3 className="text-lg font-semibold mb-6">API Configuration</h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">API Key</label>
            <input
              type="password"
              value="demo-key-change-this"
              disabled
              className="input w-full"
            />
            <p className="text-xs text-gray-400 mt-1">
              Configure in .env file: VITE_API_KEY
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">API URL</label>
            <input
              type="text"
              value={import.meta.env.VITE_API_URL || 'http://localhost:8000'}
              disabled
              className="input w-full"
            />
          </div>
        </div>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button onClick={handleSave}>
          <Save className="w-4 h-4" />
          Save Settings
        </Button>
      </div>
    </div>
  )
}

export default Settings
