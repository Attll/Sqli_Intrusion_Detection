export const ATTACK_TYPES = {
  UNION_BASED: 'Union-based SQLi',
  BOOLEAN_BASED: 'Boolean-based SQLi',
  TIME_BASED: 'Time-based Blind SQLi',
  ERROR_BASED: 'Error-based SQLi',
  STACKED_QUERIES: 'Stacked Queries',
  GENERIC: 'Generic SQLi Pattern',
}

export const MODEL_NAMES = {
  random_forest: 'Random Forest',
  xgboost: 'XGBoost',
  logistic_regression: 'Logistic Regression',
  svm: 'Support Vector Machine',
  naive_bayes: 'Naive Bayes',
}

export const XAI_METHODS = {
  lime: 'LIME',
  shap: 'SHAP',
  feature_importance: 'Feature Importance',
}

export const EXPLANATION_STYLES = {
  simple: 'Simple',
  technical: 'Technical',
  detailed: 'Detailed',
}
