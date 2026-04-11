import React, { useState } from 'react'
import Head from 'next/head'
import Layout from '../components/Layout'
import { CheckCircle, XCircle, Eye, EyeOff, Save, Loader2, Bell, Bot, Key } from 'lucide-react'
import toast from 'react-hot-toast'
import clsx from 'clsx'

interface Platform {
  id:        string
  name:      string
  abbr:      string
  connected: boolean
  username?: string
  color:     string
  bg:        string
}

interface AgentConfig {
  id:      string
  name:    string
  desc:    string
  enabled: boolean
}

const INITIAL_PLATFORMS: Platform[] = [
  { id: 'instagram', name: 'Instagram', abbr: 'IG', connected: true,  username: '@mystore',  color: 'text-pink-400', bg: 'bg-pink-900/30'  },
  { id: 'facebook',  name: 'Facebook',  abbr: 'FB', connected: true,  username: 'My Page',   color: 'text-blue-400', bg: 'bg-blue-900/30'  },
  { id: 'youtube',   name: 'YouTube',   abbr: 'YT', connected: false, username: undefined,   color: 'text-red-400',  bg: 'bg-red-900/30'   },
]

const INITIAL_AGENTS: AgentConfig[] = [
  { id: 'content',   name: 'Content Agent',   desc: 'Auto-generates posts with AI',             enabled: true  },
  { id: 'scheduler', name: 'Scheduler Agent', desc: 'Schedules posts at optimal times',         enabled: true  },
  { id: 'analytics', name: 'Analytics Agent', desc: 'Fetches and analyses performance data',    enabled: true  },
  { id: 'affiliate', name: 'Affiliate Agent', desc: 'Monitors affiliate link performance',      enabled: false },
]

interface NotificationPrefs {
  email:       boolean
  browser:     boolean
  agentAlerts: boolean
  weeklyReport: boolean
}

export default function SettingsPage() {
  const [platforms,  setPlatforms]  = useState<Platform[]>(INITIAL_PLATFORMS)
  const [agents,     setAgents]     = useState<AgentConfig[]>(INITIAL_AGENTS)
  const [notifPrefs, setNotifPrefs] = useState<NotificationPrefs>({
    email: true, browser: true, agentAlerts: true, weeklyReport: false,
  })
  const [apiKeys, setApiKeys] = useState({
    openai:    'sk-••••••••••••••••••••',
    instagram: 'EAA••••••••••••••••••',
    facebook:  'EAA••••••••••••••••••',
  })
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({})
  const [saving,   setSaving]   = useState(false)

  async function handleSave() {
    setSaving(true)
    await new Promise((r) => setTimeout(r, 800))
    setSaving(false)
    toast.success('Settings saved!')
  }

  function togglePlatform(id: string) {
    setPlatforms((prev) => prev.map((p) =>
      p.id === id ? { ...p, connected: !p.connected } : p
    ))
    const platform = platforms.find((p) => p.id === id)
    toast.success(platform?.connected ? `Disconnected from ${platform.name}` : `Connected to ${platform?.name}!`)
  }

  function toggleAgent(id: string) {
    setAgents((prev) => prev.map((a) =>
      a.id === id ? { ...a, enabled: !a.enabled } : a
    ))
  }

  function toggleKeyVisibility(key: string) {
    setShowKeys((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  return (
    <>
      <Head><title>Settings – AdsAgent</title></Head>
      <Layout>
        <div className="space-y-6 animate-fade-in max-w-3xl">

          {/* Platform connections */}
          <div className="card">
            <div className="flex items-center gap-2 mb-5">
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
                <CheckCircle className="w-4 h-4 text-white" />
              </div>
              <div>
                <h2 className="text-sm font-semibold text-white">Social Media Connections</h2>
                <p className="text-xs text-gray-400">Connect your accounts to enable posting and analytics.</p>
              </div>
            </div>
            <div className="space-y-3">
              {platforms.map((p) => (
                <div
                  key={p.id}
                  className={clsx('flex items-center justify-between p-4 rounded-xl border', p.bg,
                    p.connected ? 'border-green-800/40' : 'border-surface-border'
                  )}
                >
                  <div className="flex items-center gap-3">
                    <div className={clsx('w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold bg-black/20', p.color)}>
                      {p.abbr}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">{p.name}</p>
                      {p.connected && p.username && (
                        <p className="text-xs text-gray-400">{p.username}</p>
                      )}
                      {!p.connected && (
                        <p className="text-xs text-gray-500">Not connected</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {p.connected
                      ? <span className="flex items-center gap-1 text-xs text-green-400"><CheckCircle className="w-3.5 h-3.5" />Connected</span>
                      : <span className="flex items-center gap-1 text-xs text-gray-500"><XCircle className="w-3.5 h-3.5" />Disconnected</span>
                    }
                    <button
                      onClick={() => togglePlatform(p.id)}
                      className={clsx('text-xs font-medium px-3 py-1.5 rounded-lg border transition-all',
                        p.connected
                          ? 'border-red-800 text-red-400 hover:bg-red-900/20'
                          : 'border-blue-700 text-blue-400 hover:bg-blue-900/20'
                      )}
                    >
                      {p.connected ? 'Disconnect' : 'Connect'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* API keys */}
          <div className="card">
            <div className="flex items-center gap-2 mb-5">
              <div className="w-8 h-8 rounded-lg bg-yellow-600 flex items-center justify-center">
                <Key className="w-4 h-4 text-white" />
              </div>
              <div>
                <h2 className="text-sm font-semibold text-white">API Keys</h2>
                <p className="text-xs text-gray-400">Manage your integration API keys securely.</p>
              </div>
            </div>
            <div className="space-y-4">
              {(Object.entries(apiKeys) as [keyof typeof apiKeys, string][]).map(([key, value]) => (
                <div key={key}>
                  <p className="label capitalize">{key === 'openai' ? 'OpenAI API Key' : `${key.charAt(0).toUpperCase() + key.slice(1)} Token`}</p>
                  <div className="flex gap-2">
                    <div className="relative flex-1">
                      <input
                        type={showKeys[key] ? 'text' : 'password'}
                        value={value}
                        onChange={(e) => setApiKeys((prev) => ({ ...prev, [key]: e.target.value }))}
                        className="input pr-10"
                      />
                      <button
                        onClick={() => toggleKeyVisibility(key)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
                      >
                        {showKeys[key] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Notification preferences */}
          <div className="card">
            <div className="flex items-center gap-2 mb-5">
              <div className="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center">
                <Bell className="w-4 h-4 text-white" />
              </div>
              <div>
                <h2 className="text-sm font-semibold text-white">Notification Preferences</h2>
                <p className="text-xs text-gray-400">Choose how you want to be notified.</p>
              </div>
            </div>
            <div className="space-y-3">
              {(Object.entries(notifPrefs) as [keyof NotificationPrefs, boolean][]).map(([key, val]) => {
                const labels: Record<keyof NotificationPrefs, string> = {
                  email:        'Email notifications',
                  browser:      'Browser push notifications',
                  agentAlerts:  'Agent activity alerts',
                  weeklyReport: 'Weekly performance report',
                }
                return (
                  <div key={key} className="flex items-center justify-between p-3 rounded-lg bg-surface-input border border-surface-border">
                    <p className="text-sm text-gray-200">{labels[key]}</p>
                    <button
                      onClick={() => setNotifPrefs((prev) => ({ ...prev, [key]: !prev[key] }))}
                      className={clsx(
                        'relative w-11 h-6 rounded-full transition-colors duration-200',
                        val ? 'bg-blue-600' : 'bg-gray-700'
                      )}
                    >
                      <span className={clsx(
                        'absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform duration-200',
                        val ? 'translate-x-5' : 'translate-x-0.5'
                      )} />
                    </button>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Agent settings */}
          <div className="card">
            <div className="flex items-center gap-2 mb-5">
              <div className="w-8 h-8 rounded-lg bg-green-600 flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div>
                <h2 className="text-sm font-semibold text-white">Agent Settings</h2>
                <p className="text-xs text-gray-400">Enable or disable individual AI agents.</p>
              </div>
            </div>
            <div className="space-y-3">
              {agents.map((agent) => (
                <div key={agent.id} className="flex items-center justify-between p-3 rounded-lg bg-surface-input border border-surface-border">
                  <div>
                    <p className="text-sm font-medium text-white">{agent.name}</p>
                    <p className="text-xs text-gray-400">{agent.desc}</p>
                  </div>
                  <button
                    onClick={() => toggleAgent(agent.id)}
                    className={clsx(
                      'relative w-11 h-6 rounded-full transition-colors duration-200',
                      agent.enabled ? 'bg-blue-600' : 'bg-gray-700'
                    )}
                  >
                    <span className={clsx(
                      'absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform duration-200',
                      agent.enabled ? 'translate-x-5' : 'translate-x-0.5'
                    )} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Save button */}
          <button onClick={handleSave} disabled={saving} className="btn-primary">
            {saving ? <><Loader2 className="w-4 h-4 animate-spin" /> Saving...</> : <><Save className="w-4 h-4" /> Save Settings</>}
          </button>

        </div>
      </Layout>
    </>
  )
}
