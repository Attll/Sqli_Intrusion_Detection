import React from 'react'
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Shield,
  BarChart3,
  FileText,
  Brain,
  Zap,
  Settings,
  ChevronLeft,
  Activity
} from 'lucide-react'
import { cn } from '../../utils/helpers'

const Sidebar = ({ isOpen, setIsOpen }) => {
  const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/demo', icon: Shield, label: 'Demo' },
    { to: '/analytics', icon: BarChart3, label: 'Analytics' },
    { to: '/logs', icon: FileText, label: 'Logs' },
    { to: '/models', icon: Brain, label: 'Models' },
    { to: '/stress-test', icon: Zap, label: 'Stress Test' },
    { to: '/settings', icon: Settings, label: 'Settings' },
  ]

  return (
    <aside
      className={cn(
        'bg-dark-surface border-r border-dark-border transition-all duration-300 flex flex-col',
        isOpen ? 'w-64' : 'w-20'
      )}
    >
      {/* Logo */}
      <div className="p-6 border-b border-dark-border flex items-center justify-between">
        {isOpen ? (
          <>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                <Shield className="w-5 h-5" />
              </div>
              <div>
                <h1 className="text-sm font-bold">SQLi Shield</h1>
                <p className="text-xs text-gray-400">Detection System</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 hover:bg-dark-hover rounded transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
          </>
        ) : (
          <button
            onClick={() => setIsOpen(true)}
            className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center mx-auto"
          >
            <Shield className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 px-4 py-3 rounded-lg transition-all group',
                    isActive
                      ? 'bg-white text-black'
                      : 'hover:bg-dark-hover text-gray-300 hover:text-white'
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    <item.icon className="w-5 h-5 flex-shrink-0" />
                    {isOpen && (
                      <span className="text-sm font-medium">{item.label}</span>
                    )}
                  </>
                )}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Status indicator */}
      <div className="p-4 border-t border-dark-border">
        <div
          className={cn(
            'flex items-center gap-3 px-4 py-3 rounded-lg bg-green-500/10 border border-green-500/20',
            !isOpen && 'justify-center'
          )}
        >
          <Activity className="w-4 h-4 text-green-500" />
          {isOpen && (
            <div className="flex-1">
              <p className="text-xs font-medium text-green-500">System Active</p>
              <p className="text-xs text-gray-400">All models operational</p>
            </div>
          )}
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
