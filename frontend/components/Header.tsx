import React, { useState } from 'react'
import { useRouter } from 'next/router'
import { Bell, Loader2, ChevronDown, User, LogOut, HelpCircle } from 'lucide-react'
import clsx from 'clsx'

const pageTitles: Record<string, string> = {
  '/dashboard':  'Dashboard',
  '/content':    'Content Management',
  '/analytics':  'Analytics',
  '/products':   'Affiliate Products',
  '/campaigns':  'Campaigns',
  '/settings':   'Settings',
}

interface HeaderProps {
  agentRunning?: boolean
  notificationCount?: number
}

export default function Header({ agentRunning = false, notificationCount = 3 }: HeaderProps) {
  const router = useRouter()
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [notifOpen, setNotifOpen] = useState(false)

  const pageTitle = pageTitles[router.pathname] ?? 'AdsAgent'

  const notifications = [
    { id: 1, text: 'Content generated for Instagram',  time: '2m ago',  read: false },
    { id: 2, text: 'Campaign "Summer Sale" is active', time: '15m ago', read: false },
    { id: 3, text: 'New affiliate click detected',     time: '1h ago',  read: false },
    { id: 4, text: 'Analytics report ready',           time: '3h ago',  read: true  },
  ]

  return (
    <header className="sticky top-0 z-30 bg-navy-950/80 backdrop-blur-md border-b border-surface-border px-6 py-3 flex items-center justify-between">
      {/* Page title */}
      <div>
        <h1 className="text-lg font-semibold text-white">{pageTitle}</h1>
        <p className="text-xs text-gray-500">
          {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </p>
      </div>

      {/* Right controls */}
      <div className="flex items-center gap-3">
        {/* Agent running indicator */}
        {agentRunning && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-900/40 border border-blue-800 text-blue-400 text-xs font-medium">
            <Loader2 className="w-3 h-3 animate-spin" />
            Agent running
          </div>
        )}

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => { setNotifOpen(!notifOpen); setUserMenuOpen(false) }}
            className="relative w-9 h-9 rounded-lg bg-surface-card border border-surface-border flex items-center justify-center text-gray-400 hover:text-white hover:bg-surface-hover transition-all duration-200"
          >
            <Bell className="w-4 h-4" />
            {notificationCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center">
                {notificationCount}
              </span>
            )}
          </button>

          {notifOpen && (
            <div className="absolute right-0 top-11 w-80 bg-surface-card border border-surface-border rounded-xl shadow-2xl z-50 animate-slide-up overflow-hidden">
              <div className="px-4 py-3 border-b border-surface-border flex items-center justify-between">
                <span className="text-sm font-semibold text-white">Notifications</span>
                <button className="text-xs text-blue-400 hover:text-blue-300">Mark all read</button>
              </div>
              <div className="max-h-64 overflow-y-auto">
                {notifications.map((n) => (
                  <div key={n.id} className={clsx('px-4 py-3 border-b border-surface-border/50 hover:bg-surface-hover cursor-pointer transition-colors', !n.read && 'bg-blue-900/10')}>
                    <div className="flex items-start gap-3">
                      {!n.read && <span className="w-2 h-2 rounded-full bg-blue-400 flex-shrink-0 mt-1.5" />}
                      {n.read  && <span className="w-2 h-2 rounded-full bg-transparent flex-shrink-0 mt-1.5" />}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-200">{n.text}</p>
                        <p className="text-xs text-gray-500 mt-0.5">{n.time}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="px-4 py-2.5 text-center">
                <button className="text-xs text-gray-400 hover:text-white transition-colors">
                  View all notifications
                </button>
              </div>
            </div>
          )}
        </div>

        {/* User menu */}
        <div className="relative">
          <button
            onClick={() => { setUserMenuOpen(!userMenuOpen); setNotifOpen(false) }}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-card border border-surface-border hover:bg-surface-hover transition-all duration-200"
          >
            <div className="w-6 h-6 rounded-full bg-gradient-brand flex items-center justify-center">
              <User className="w-3 h-3 text-white" />
            </div>
            <span className="text-sm text-gray-300 font-medium">Admin</span>
            <ChevronDown className={clsx('w-3 h-3 text-gray-400 transition-transform duration-200', userMenuOpen && 'rotate-180')} />
          </button>

          {userMenuOpen && (
            <div className="absolute right-0 top-11 w-44 bg-surface-card border border-surface-border rounded-xl shadow-2xl z-50 animate-slide-up overflow-hidden">
              {[
                { icon: User,        label: 'Profile'  },
                { icon: HelpCircle,  label: 'Help'     },
                { icon: LogOut,      label: 'Sign out', danger: true },
              ].map(({ icon: Icon, label, danger }) => (
                <button
                  key={label}
                  className={clsx(
                    'w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors duration-150',
                    danger
                      ? 'text-red-400 hover:bg-red-900/20'
                      : 'text-gray-300 hover:bg-surface-hover hover:text-white'
                  )}
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
