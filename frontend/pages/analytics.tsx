import React, { useState } from 'react'
import Head from 'next/head'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Download } from 'lucide-react'
import Layout from '../components/Layout'
import {
  EngagementChart, ReachChart, PlatformComparisonChart,
  type TimeSeriesPoint, type PlatformBar,
} from '../components/Charts'
import clsx from 'clsx'

type Platform = 'all' | 'instagram' | 'facebook' | 'youtube'
type Range    = '7d' | '30d' | '90d'

const PLATFORMS: { id: Platform; label: string }[] = [
  { id: 'all',       label: 'All Platforms' },
  { id: 'instagram', label: 'Instagram' },
  { id: 'facebook',  label: 'Facebook' },
  { id: 'youtube',   label: 'YouTube' },
]

const RANGES: { id: Range; label: string }[] = [
  { id: '7d',  label: 'Last 7 days'  },
  { id: '30d', label: 'Last 30 days' },
  { id: '90d', label: 'Last 90 days' },
]

function makeSeries(days: number): TimeSeriesPoint[] {
  return Array.from({ length: days }, (_, i) => ({
    date:      `Dec ${i + 1}`,
    instagram: 1500 + Math.round(Math.random() * 3500),
    facebook:  800  + Math.round(Math.random() * 2000),
    youtube:   400  + Math.round(Math.random() * 1600),
  }))
}

const PLATFORM_BARS: PlatformBar[] = [
  { platform: 'Instagram', value: 4820, color: '#ec4899' },
  { platform: 'Facebook',  value: 2310, color: '#3b82f6' },
  { platform: 'YouTube',   value: 6120, color: '#ef4444' },
]

const TOP_POSTS = [
  { id: '1', title: 'Skincare routine 🌞',      platform: 'Instagram', reach: 29300, engagement: 4.8, likes: 1243, comments: 87  },
  { id: '2', title: 'Top 5 affiliate products',  platform: 'Facebook',  reach: 18400, engagement: 3.2, likes: 892,  comments: 43  },
  { id: '3', title: 'Making $5k with AI tools',  platform: 'YouTube',   reach: 56000, engagement: 6.1, likes: 3892, comments: 214 },
  { id: '4', title: 'Morning wellness routine',  platform: 'Instagram', reach: 21000, engagement: 5.3, likes: 1100, comments: 62  },
  { id: '5', title: 'Product review: FitBand',   platform: 'Facebook',  reach: 9800,  engagement: 2.9, likes: 456,  comments: 29  },
]

export default function AnalyticsPage() {
  const [activePlatform, setActivePlatform] = useState<Platform>('all')
  const [activeRange,    setActiveRange]    = useState<Range>('30d')

  const days  = activeRange === '7d' ? 7 : activeRange === '30d' ? 30 : 90
  const series = makeSeries(days)

  return (
    <>
      <Head><title>Analytics – AdsAgent</title></Head>
      <Layout>
        <div className="space-y-5 animate-fade-in">

          {/* Controls row */}
          <div className="flex flex-wrap items-center gap-3 justify-between">
            {/* Platform tabs */}
            <div className="flex gap-1 p-1 bg-surface-card border border-surface-border rounded-xl">
              {PLATFORMS.map(({ id, label }) => (
                <button
                  key={id}
                  onClick={() => setActivePlatform(id)}
                  className={clsx(
                    'px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200',
                    activePlatform === id
                      ? 'bg-brand-blue text-white'
                      : 'text-gray-400 hover:text-white'
                  )}
                >
                  {label}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-3">
              {/* Date range */}
              <div className="flex gap-1 p-1 bg-surface-card border border-surface-border rounded-xl">
                {RANGES.map(({ id, label }) => (
                  <button
                    key={id}
                    onClick={() => setActiveRange(id)}
                    className={clsx(
                      'px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200',
                      activeRange === id
                        ? 'bg-surface-hover text-white'
                        : 'text-gray-400 hover:text-white'
                    )}
                  >
                    {label}
                  </button>
                ))}
              </div>
              <button className="btn-secondary text-xs">
                <Download className="w-3.5 h-3.5" />
                Export
              </button>
            </div>
          </div>

          {/* Summary metrics */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: 'Total Reach',      value: '124K',  change: '+8.7%',  positive: true  },
              { label: 'Impressions',      value: '389K',  change: '-2.1%',  positive: false },
              { label: 'Avg Engagement',   value: '4.82%', change: '+12.3%', positive: true  },
              { label: 'Link Clicks',      value: '3,241', change: '+31.0%', positive: true  },
            ].map((m) => (
              <div key={m.label} className="card">
                <p className="text-xs text-gray-400 mb-1">{m.label}</p>
                <p className="text-2xl font-bold text-white mb-1">{m.value}</p>
                <p className={clsx('text-xs font-medium', m.positive ? 'text-green-400' : 'text-red-400')}>
                  {m.change} vs previous
                </p>
              </div>
            ))}
          </div>

          {/* Charts row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <div className="card">
              <h2 className="text-sm font-semibold text-white mb-4">Engagement Over Time</h2>
              <EngagementChart data={series} height={260} />
            </div>
            <div className="card">
              <h2 className="text-sm font-semibold text-white mb-4">Reach & Impressions</h2>
              <ReachChart data={series} height={260} />
            </div>
          </div>

          {/* Platform comparison */}
          <div className="card">
            <h2 className="text-sm font-semibold text-white mb-4">Platform Comparison</h2>
            <PlatformComparisonChart data={PLATFORM_BARS} height={240} />
          </div>

          {/* Top performing posts table */}
          <div className="card">
            <h2 className="text-sm font-semibold text-white mb-4">Top Performing Posts</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-surface-border">
                    <th className="table-header">Post</th>
                    <th className="table-header">Platform</th>
                    <th className="table-header text-right">Reach</th>
                    <th className="table-header text-right">Engagement</th>
                    <th className="table-header text-right">Likes</th>
                    <th className="table-header text-right">Comments</th>
                  </tr>
                </thead>
                <tbody>
                  {TOP_POSTS.map((post) => (
                    <tr key={post.id} className="table-row">
                      <td className="table-cell font-medium">{post.title}</td>
                      <td className="table-cell">
                        <span className={clsx('text-xs font-medium',
                          post.platform === 'Instagram' ? 'text-pink-400' :
                          post.platform === 'Facebook'  ? 'text-blue-400' : 'text-red-400'
                        )}>{post.platform}</span>
                      </td>
                      <td className="table-cell text-right">{post.reach.toLocaleString()}</td>
                      <td className="table-cell text-right">{post.engagement}%</td>
                      <td className="table-cell text-right">{post.likes.toLocaleString()}</td>
                      <td className="table-cell text-right">{post.comments}</td>
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
