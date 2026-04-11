import React, { useState } from 'react'
import Head from 'next/head'
import Layout from '../components/Layout'
import { Plus, X, Wand2, Play, Pause, Check, Loader2, ChevronDown, ChevronUp } from 'lucide-react'
import toast from 'react-hot-toast'
import clsx from 'clsx'
import { format, addDays } from 'date-fns'

type CampaignStatus = 'active' | 'paused' | 'completed' | 'draft'

interface Campaign {
  id:        string
  name:      string
  platforms: string[]
  budget:    number
  spent:     number
  startDate: string
  endDate:   string
  status:    CampaignStatus
  reach:     number
  clicks:    number
  conversions: number
}

const STATUS_STYLE: Record<CampaignStatus, string> = {
  active:    'badge-active',
  paused:    'badge-paused',
  completed: 'badge-completed',
  draft:     'badge-draft',
}

const MOCK_CAMPAIGNS: Campaign[] = [
  { id: '1', name: 'Summer Beauty Sale',    platforms: ['instagram', 'facebook'], budget: 500,  spent: 312,  startDate: 'Dec 1',  endDate: 'Dec 31', status: 'active',    reach: 18400, clicks: 1243, conversions: 89  },
  { id: '2', name: 'FitBand Launch',        platforms: ['youtube', 'instagram'],  budget: 300,  spent: 300,  startDate: 'Nov 15', endDate: 'Dec 15', status: 'completed', reach: 32100, clicks: 892,  conversions: 54  },
  { id: '3', name: 'Course Promo – Jan',    platforms: ['facebook'],              budget: 200,  spent: 0,    startDate: 'Jan 1',  endDate: 'Jan 31', status: 'draft',     reach: 0,     clicks: 0,    conversions: 0   },
  { id: '4', name: 'Coffee Brand Collab',   platforms: ['instagram'],             budget: 150,  spent: 67,   startDate: 'Dec 10', endDate: 'Dec 25', status: 'paused',    reach: 8900,  clicks: 321,  conversions: 28  },
]

interface CampaignDetailProps {
  campaign: Campaign
  onOptimize: (id: string) => void
  onTogglePause: (id: string) => void
  onClose: () => void
}

function CampaignDetail({ campaign: c, onOptimize, onTogglePause, onClose }: CampaignDetailProps) {
  const [optimizing, setOptimizing] = useState(false)

  async function handleOptimize() {
    setOptimizing(true)
    await new Promise((r) => setTimeout(r, 1500))
    onOptimize(c.id)
    setOptimizing(false)
    toast.success('Campaign optimized by AI!')
  }

  const spentPct = c.budget > 0 ? Math.min((c.spent / c.budget) * 100, 100) : 0

  return (
    <div className="card border-blue-600/30 animate-slide-up space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-white">{c.name}</h3>
        <button onClick={onClose} className="text-gray-400 hover:text-white"><X className="w-4 h-4" /></button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Reach',       value: c.reach.toLocaleString()       },
          { label: 'Clicks',      value: c.clicks.toLocaleString()      },
          { label: 'Conversions', value: c.conversions.toLocaleString() },
          { label: 'Conv. Rate',  value: c.clicks > 0 ? `${((c.conversions / c.clicks) * 100).toFixed(1)}%` : '—' },
        ].map((m) => (
          <div key={m.label} className="bg-surface-input rounded-lg p-3 border border-surface-border">
            <p className="text-xs text-gray-400 mb-0.5">{m.label}</p>
            <p className="text-lg font-bold text-white">{m.value}</p>
          </div>
        ))}
      </div>

      {/* Budget progress */}
      <div>
        <div className="flex justify-between text-xs text-gray-400 mb-1.5">
          <span>Budget spent</span>
          <span>${c.spent} / ${c.budget}</span>
        </div>
        <div className="w-full h-2 rounded-full bg-surface-input">
          <div
            className={clsx('h-2 rounded-full transition-all', spentPct >= 90 ? 'bg-red-500' : 'bg-blue-500')}
            style={{ width: `${spentPct}%` }}
          />
        </div>
      </div>

      <div className="flex gap-3">
        <button onClick={handleOptimize} disabled={optimizing} className="btn-primary flex-1 justify-center text-sm">
          {optimizing ? <><Loader2 className="w-4 h-4 animate-spin" /> Optimizing...</> : <><Wand2 className="w-4 h-4" /> AI Optimize</>}
        </button>
        {c.status !== 'completed' && (
          <button onClick={() => onTogglePause(c.id)} className="btn-secondary text-sm">
            {c.status === 'paused' ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
            {c.status === 'paused' ? 'Resume' : 'Pause'}
          </button>
        )}
      </div>
    </div>
  )
}

export default function CampaignsPage() {
  const [campaigns,    setCampaigns]    = useState<Campaign[]>(MOCK_CAMPAIGNS)
  const [selected,     setSelected]     = useState<string | null>(null)
  const [showForm,     setShowForm]     = useState(false)
  const [form, setForm] = useState({
    name:      '',
    platforms: [] as string[],
    budget:    '',
    startDate: format(new Date(), 'yyyy-MM-dd'),
    endDate:   format(addDays(new Date(), 30), 'yyyy-MM-dd'),
  })

  function togglePlatform(p: string) {
    setForm((prev) => ({
      ...prev,
      platforms: prev.platforms.includes(p)
        ? prev.platforms.filter((x) => x !== p)
        : [...prev.platforms, p],
    }))
  }

  function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!form.name) { toast.error('Campaign name is required'); return }
    if (form.platforms.length === 0) { toast.error('Select at least one platform'); return }
    const newCampaign: Campaign = {
      id:          Date.now().toString(),
      name:        form.name,
      platforms:   form.platforms,
      budget:      Number(form.budget) || 0,
      spent:       0,
      startDate:   form.startDate,
      endDate:     form.endDate,
      status:      'draft',
      reach:       0, clicks: 0, conversions: 0,
    }
    setCampaigns((prev) => [newCampaign, ...prev])
    setShowForm(false)
    toast.success('Campaign created!')
  }

  function handleTogglePause(id: string) {
    setCampaigns((prev) => prev.map((c) =>
      c.id === id
        ? { ...c, status: c.status === 'paused' ? 'active' : 'paused' }
        : c
    ))
  }

  function handleOptimize(id: string) {
    setCampaigns((prev) => prev.map((c) =>
      c.id === id ? { ...c, status: 'active' } : c
    ))
  }

  const selectedCampaign = campaigns.find((c) => c.id === selected)

  return (
    <>
      <Head><title>Campaigns – AdsAgent</title></Head>
      <Layout>
        <div className="space-y-5 animate-fade-in">

          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-semibold text-white">Campaigns</h2>
              <p className="text-xs text-gray-400 mt-0.5">{campaigns.filter((c) => c.status === 'active').length} active campaigns</p>
            </div>
            <button onClick={() => setShowForm(!showForm)} className="btn-primary text-sm">
              <Plus className="w-4 h-4" /> New Campaign
            </button>
          </div>

          {/* Create form */}
          {showForm && (
            <div className="card animate-slide-up">
              <h3 className="text-sm font-semibold text-white mb-4">Create Campaign</h3>
              <form onSubmit={handleCreate} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="sm:col-span-2">
                    <p className="label">Campaign Name *</p>
                    <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Summer Sale 2024" />
                  </div>
                  <div>
                    <p className="label">Platforms *</p>
                    <div className="flex gap-2">
                      {['instagram', 'facebook', 'youtube'].map((p) => (
                        <button
                          key={p} type="button"
                          onClick={() => togglePlatform(p)}
                          className={clsx(
                            'flex-1 py-2 rounded-lg text-xs font-medium border capitalize transition-all',
                            form.platforms.includes(p)
                              ? 'bg-blue-600 border-blue-500 text-white'
                              : 'border-surface-border text-gray-400 hover:text-white'
                          )}
                        >
                          {p}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p className="label">Budget ($)</p>
                    <input type="number" className="input" value={form.budget} onChange={(e) => setForm({ ...form, budget: e.target.value })} placeholder="500" min="0" />
                  </div>
                  <div>
                    <p className="label">Start Date</p>
                    <input type="date" className="input" value={form.startDate} onChange={(e) => setForm({ ...form, startDate: e.target.value })} />
                  </div>
                  <div>
                    <p className="label">End Date</p>
                    <input type="date" className="input" value={form.endDate} onChange={(e) => setForm({ ...form, endDate: e.target.value })} />
                  </div>
                </div>
                <div className="flex gap-3">
                  <button type="submit" className="btn-primary">Create Campaign</button>
                  <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
                </div>
              </form>
            </div>
          )}

          {/* Selected campaign detail */}
          {selectedCampaign && (
            <CampaignDetail
              campaign={selectedCampaign}
              onOptimize={handleOptimize}
              onTogglePause={handleTogglePause}
              onClose={() => setSelected(null)}
            />
          )}

          {/* Campaigns list */}
          <div className="card">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-surface-border">
                    <th className="table-header">Campaign</th>
                    <th className="table-header">Platforms</th>
                    <th className="table-header">Status</th>
                    <th className="table-header">Dates</th>
                    <th className="table-header text-right">Budget</th>
                    <th className="table-header text-right">Reach</th>
                    <th className="table-header" />
                  </tr>
                </thead>
                <tbody>
                  {campaigns.map((c) => (
                    <tr key={c.id} className="table-row cursor-pointer" onClick={() => setSelected(selected === c.id ? null : c.id)}>
                      <td className="table-cell font-medium">{c.name}</td>
                      <td className="table-cell">
                        <div className="flex gap-1">
                          {c.platforms.map((p) => (
                            <span key={p} className={clsx('text-xs px-1.5 py-0.5 rounded font-medium',
                              p === 'instagram' ? 'bg-pink-900/40 text-pink-400' :
                              p === 'facebook'  ? 'bg-blue-900/40 text-blue-400' : 'bg-red-900/40 text-red-400'
                            )}>
                              {p.slice(0, 2).toUpperCase()}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="table-cell"><span className={STATUS_STYLE[c.status]}>{c.status}</span></td>
                      <td className="table-cell text-gray-400 text-xs">{c.startDate} – {c.endDate}</td>
                      <td className="table-cell text-right">
                        <div>
                          <p className="text-white text-sm">${c.budget}</p>
                          <p className="text-xs text-gray-500">${c.spent} spent</p>
                        </div>
                      </td>
                      <td className="table-cell text-right">{c.reach.toLocaleString()}</td>
                      <td className="table-cell text-right">
                        {selected === c.id
                          ? <ChevronUp className="w-4 h-4 text-gray-400 ml-auto" />
                          : <ChevronDown className="w-4 h-4 text-gray-400 ml-auto" />
                        }
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </Layout>
    </>
  )
}
