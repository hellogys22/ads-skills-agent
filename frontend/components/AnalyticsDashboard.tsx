'use client'
import React, { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, RefreshCw, Hash } from 'lucide-react'
import { EngagementChart, type TimeSeriesPoint } from './Charts'
import clsx from 'clsx'

const MOCK_SERIES: TimeSeriesPoint[] = Array.from({ length: 14 }, (_, i) => ({
  date:      `Dec ${i + 1}`,
  instagram: 2000 + Math.round(Math.random() * 3000),
  facebook:  1000 + Math.round(Math.random() * 2000),
  youtube:   500  + Math.round(Math.random() * 1500),
}))

interface Metric {
  label:    string
  value:    string
  change:   number
  platform: string
}

const MOCK_METRICS: Metric[] = [
  { label: 'Engagement Rate', value: '4.82%', change:  12.3, platform: 'All' },
  { label: 'Total Reach',     value: '124K',  change:   8.7, platform: 'All' },
  { label: 'Impressions',     value: '389K',  change:  -2.1, platform: 'All' },
  { label: 'Saves / Shares',  value: '3.2K',  change:  21.5, platform: 'Instagram' },
]

const MOCK_TOP_CONTENT = [
  { id: '1', title: 'Summer skincare routine 🌞', platform: 'Instagram', engagements: 4821, reach: 29300 },
  { id: '2', title: 'Top 5 affiliate products',   platform: 'Facebook',  engagements: 2983, reach: 18400 },
  { id: '3', title: 'How I make $5k/month',        platform: 'YouTube',   engagements: 7200, reach: 56000 },
]

const MOCK_HASHTAGS = [
  { tag: '#skincare',   uses: 243, reach: '18K' },
  { tag: '#affiliate',  uses: 189, reach: '12K' },
  { tag: '#sidehustle', uses: 156, reach: '10K' },
  { tag: '#beauty',     uses: 134, reach: '9K'  },
]

export default function AnalyticsDashboard() {
  const [refreshing, setRefreshing] = useState(false)
  const [lastUpdated, setLastUpdated] = useState(new Date())
  const [series, setSeries] = useState<TimeSeriesPoint[]>(MOCK_SERIES)

  // Auto-refresh every 30 s
  useEffect(() => {
    const interval = setInterval(() => {
      refresh()
    }, 30_000)
    return () => clearInterval(interval)
  }, [])

  function refresh() {
    setRefreshing(true)
    setTimeout(() => {
      setSeries(Array.from({ length: 14 }, (_, i) => ({
        date:      `Dec ${i + 1}`,
        instagram: 2000 + Math.round(Math.random() * 3000),
        facebook:  1000 + Math.round(Math.random() * 2000),
        youtube:   500  + Math.round(Math.random() * 1500),
      })))
      setLastUpdated(new Date())
      setRefreshing(false)
    }, 800)
  }

  return (
    <div className="space-y-5">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-white">Real-time Analytics</h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Last updated: {lastUpdated.toLocaleTimeString()} · Auto-refreshes every 30s
          </p>
        </div>
        <button
          onClick={refresh}
          disabled={refreshing}
          className="btn-secondary text-xs"
        >
          <RefreshCw className={clsx('w-3.5 h-3.5', refreshing && 'animate-spin')} />
          Refresh
        </button>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {MOCK_METRICS.map((m) => {
          const positive = m.change >= 0
          return (
            <div key={m.label} className="card">
              <p className="text-xs text-gray-400 mb-1">{m.label}</p>
              <p className="text-xl font-bold text-white mb-1">{m.value}</p>
              <div className={clsx('flex items-center gap-1 text-xs font-medium', positive ? 'text-green-400' : 'text-red-400')}>
                {positive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                {Math.abs(m.change)}%
              </div>
            </div>
          )
        })}
      </div>

      {/* Engagement chart */}
      <div className="card">
        <h3 className="text-sm font-semibold text-white mb-4">Engagement Over Time</h3>
        <EngagementChart data={series} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Top performing content */}
        <div className="card">
          <h3 className="text-sm font-semibold text-white mb-4">Best Performing Content</h3>
          <div className="space-y-3">
            {MOCK_TOP_CONTENT.map((c, i) => (
              <div key={c.id} className="flex items-start gap-3">
                <span className="w-5 h-5 rounded-full bg-blue-600 text-white text-[10px] font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                  {i + 1}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white truncate">{c.title}</p>
                  <div className="flex items-center gap-3 mt-0.5">
                    <span className="text-xs text-gray-500">{c.platform}</span>
                    <span className="text-xs text-gray-400">{c.engagements.toLocaleString()} engagements</span>
                    <span className="text-xs text-gray-400">{c.reach.toLocaleString()} reach</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Hashtag performance */}
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <Hash className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-white">Hashtag Performance</h3>
          </div>
          <div className="space-y-3">
            {MOCK_HASHTAGS.map((h) => (
              <div key={h.tag} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-blue-400">{h.tag}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-xs text-gray-400">{h.uses} uses</span>
                  <span className="text-xs font-medium text-white w-10 text-right">{h.reach}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
