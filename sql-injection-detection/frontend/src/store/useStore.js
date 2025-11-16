import { create } from 'zustand'

export const useStore = create((set) => ({
  // User state
  user: {
    name: 'Admin',
    role: 'admin',
  },

  // Current model
  currentModel: 'random_forest',
  setCurrentModel: (model) => set({ currentModel: model }),

  // Settings
  settings: {
    theme: 'dark',
    confidenceThreshold: 0.7,
    useEnsemble: false,
    xaiMethod: 'lime',
    explanationStyle: 'simple',
  },
  updateSettings: (newSettings) =>
    set((state) => ({
      settings: { ...state.settings, ...newSettings },
    })),

  // Stats cache
  stats: null,
  setStats: (stats) => set({ stats }),
}))
