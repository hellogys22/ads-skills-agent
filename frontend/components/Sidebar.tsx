import React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import clsx from 'clsx'
import {
  LayoutDashboard,
  FileText,
  BarChart3,
  ShoppingBag,
  Megaphone,
  Settings,
  Zap,
  Activity,
} from 'lucide-react'

const navItems = [
  { href: '/dashboard',  label: 'Dashboard',  icon: LayoutDashboard },
  { href: '/content',    label: 'Content',     icon: FileText },
  { href: '/analytics',  label: 'Analytics',   icon: BarChart3 },
  { href: '/products',   label: 'Products',    icon: ShoppingBag },
  { href: '/campaigns',  label: 'Campaigns',   icon: Megaphone },
  { href: '/settings',   label: 'Settings',    icon: Settings },
]

const platformIcons = [
  { name: 'IG', color: 'text-pink-400',  bg: 'bg-pink-900/40',  connected: true },
  { name: 'FB', color: 'text-blue-400',  bg: 'bg-blue-900/40',  connected: true },
  { name: 'YT', color: 'text-red-400',   bg: 'bg-red-900/40',   connected: false },
]

export default function Sidebar() {
  const router = useRouter()

  return (
    <aside className="flex flex-col w-64 min-h-screen bg-navy-950 border-r border-surface-border">
      {/* Brand */}
      <div className="px-5 py-5 border-b border-surface-border">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-brand flex items-center justify-center shadow-glow">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-white font-bold text-base leading-tight">AdsAgent</p>
            <p className="text-gray-500 text-xs">Marketing AI</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <p className="px-3 pb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
          Main Menu
        </p>
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive = router.pathname === href
          return (
            <Link
              key={href}
              href={href}
              className={isActive ? 'nav-link-active' : 'nav-link'}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {label}
              {isActive && (
                <span className="ml-auto w-1.5 h-1.5 rounded-full bg-white opacity-60" />
              )}
            </Link>
          )
        })}
      </nav>

      {/* Agent Status */}
      <div className="px-4 py-3 border-t border-surface-border">
        <div className="flex items-center gap-2 mb-3">
          <Activity className="w-4 h-4 text-green-400" />
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Agent Status</p>
        </div>
        <div className="space-y-2">
          {[
            { name: 'Content Agent', active: true },
            { name: 'Analytics Agent', active: true },
            { name: 'Scheduler Agent', active: false },
          ].map((agent) => (
            <div key={agent.name} className="flex items-center justify-between">
              <span className="text-xs text-gray-400">{agent.name}</span>
              <span className={clsx(
                'w-2 h-2 rounded-full',
                agent.active ? 'bg-green-400 agent-active' : 'bg-gray-600'
              )} />
            </div>
          ))}
        </div>
      </div>

      {/* Platform Connections */}
      <div className="px-4 py-3 border-t border-surface-border">
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
          Platforms
        </p>
        <div className="flex items-center gap-2">
          {platformIcons.map((p) => (
            <div
              key={p.name}
              title={p.connected ? 'Connected' : 'Disconnected'}
              className={clsx(
                'w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold relative',
                p.bg, p.color
              )}
            >
              {p.name}
              <span className={clsx(
                'absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full border border-navy-950',
                p.connected ? 'bg-green-400' : 'bg-gray-600'
              )} />
            </div>
          ))}
        </div>
      </div>
    </aside>
  )
}
