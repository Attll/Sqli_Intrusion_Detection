import React from 'react'
import { Brain, Check, TrendingUp } from 'lucide-react'
import Card from '../common/Card'
import Badge from '../common/Badge'
import Button from '../common/Button'

const ModelCard = ({ model, onActivate, onTrain, isActivating }) => {
  return (
    <Card className={model.is_active ? 'border-green-500/50' : ''}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
            model.is_active
              ? 'bg-green-500/20 text-green-500'
              : 'bg-gray-500/20 text-gray-500'
          }`}>
            <Brain className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold">{model.model_name.replace('_', ' ').toUpperCase()}</h3>
            <p className="text-xs text-gray-400">v{model.version}</p>
          </div>
        </div>
        {model.is_active && (
          <Badge variant="success">
            <Check className="w-3 h-3 inline mr-1" />
            Active
          </Badge>
        )}
      </div>

      {/* Metrics */}
      {model.metrics && (
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-dark-surface rounded-lg p-3">
            <p className="text-xs text-gray-400 mb-1">Accuracy</p>
            <p className="text-lg font-bold">{(model.metrics.accuracy * 100).toFixed(1)}%</p>
          </div>
          <div className="bg-dark-surface rounded-lg p-3">
            <p className="text-xs text-gray-400 mb-1">F1 Score</p>
            <p className="text-lg font-bold">{(model.metrics.f1_score * 100).toFixed(1)}%</p>
          </div>
          <div className="bg-dark-surface rounded-lg p-3">
            <p className="text-xs text-gray-400 mb-1">Precision</p>
            <p className="text-lg font-bold">{(model.metrics.precision * 100).toFixed(1)}%</p>
          </div>
          <div className="bg-dark-surface rounded-lg p-3">
            <p className="text-xs text-gray-400 mb-1">Recall</p>
            <p className="text-lg font-bold">{(model.metrics.recall * 100).toFixed(1)}%</p>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        {!model.is_active && (
          <Button
            onClick={() => onActivate(model.id)}
            isLoading={isActivating}
            variant="secondary"
            className="flex-1"
          >
            Activate
          </Button>
        )}
        <Button
          onClick={() => onTrain(model.model_name)}
          variant="secondary"
          className="flex-1"
        >
          <TrendingUp className="w-4 h-4" />
          Retrain
        </Button>
      </div>
    </Card>
  )
}

export default ModelCard
