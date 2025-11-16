import React, { useState } from 'react'
import { Brain, TrendingUp } from 'lucide-react'
import ModelCard from '../components/models/ModelCard'
import FeatureImportance from '../components/models/FeatureImportance'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { useApi } from '../hooks/useApi'
import toast from 'react-hot-toast'
import { api } from '../services/api'

const Models = () => {
  const { useModels, useActivateModel } = useApi()
  const { data: models, isLoading } = useModels()
  const activateModel = useActivateModel()
  const [selectedModel, setSelectedModel] = useState(null)
  const [featureImportance, setFeatureImportance] = useState(null)

  const handleActivate = async (modelId) => {
    try {
      await activateModel.mutateAsync(modelId)
      toast.success('Model activated successfully')
    } catch (error) {
      toast.error('Failed to activate model')
    }
  }

  const handleTrain = async (modelName) => {
    toast.loading(`Training ${modelName}...`, { duration: 2000 })
    // In a real app, this would trigger background training
  }

  const handleViewFeatures = async (modelName) => {
    try {
      const { data } = await api.get(`/models/${modelName}/feature-importance`)
      setFeatureImportance(data.feature_importance)
      setSelectedModel(modelName)
    } catch (error) {
      toast.error('Failed to load feature importance')
    }
  }

  if (isLoading) return <LoadingSpinner text="Loading models..." />

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">ML Models</h1>
          <p className="text-gray-400">Manage and compare detection models</p>
        </div>
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-blue-400" />
          <span className="text-sm text-gray-400">
            {models?.filter(m => m.is_active).length || 0} active models
          </span>
        </div>
      </div>

      {/* Model Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {models?.map((model) => (
          <ModelCard
            key={model.id}
            model={model}
            onActivate={handleActivate}
            onTrain={handleTrain}
            isActivating={activateModel.isPending}
          />
        ))}
      </div>

      {/* Feature Importance */}
      {featureImportance && (
        <FeatureImportance
          modelName={selectedModel}
          featureImportance={featureImportance}
        />
      )}
    </div>
  )
}

export default Models
