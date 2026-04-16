import React from 'react'
import Head from 'next/head'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import {
  Users, TrendingUp, Calendar, DollarSign,
  Instagram, Youtube, CheckCircle, AlertCircle,
  Wand2, Clock, BarChart3, ExternalLink,
} from 'lucide-react'
import Layout from '../components/Layout'
import StatsCard from '../components/StatsCard'
import { FollowerGrowthChart, type TimeSeriesPoint } from '../components/Charts'

/* ── Types ────────────────────────────────────────────── */
interface DashboardStats {
  totalFollowers:  number
  engagementRate:  number
  postsScheduled:  number
  revenue:         number
  followerChange:  number
  engagementChange:number
  scheduledChange: number
  revenueChange:   number
}

interface RecentPost {
  id:       string
  title:    string
  platform: string
  status:   'published' | 'scheduled' | 'draft'
  date:     string
  likes:    number
  comments: number
}

interface ActivityItem {
  id:      string
  message: string
  time:    string
  type:    'success' | 'info' | 'warning'
}

/* ── Mock data (used when API is unavailable) ─────────── */
const MOCK_STATS: DashboardStats = {
  totalFollowers: 124500, engagementRate: 4.82,
  postsScheduled: 12,     revenue:        3240,
  followerChange: 8.3,    engagementChange: 1.2,
  scheduledChange: -2.0,  revenueChange:   22.5,
}

const MOCK_GROWTH: TimeSeriesPoint[] = Array.from({ length: 14 }, (_, i) => ({
  date:  `Dec ${i + 1}`,
  total: 110000 + i * 1050 + Math.round(Math.random() * 500),
}))

const MOCK_POSTS: RecentPost[] = [
  { id: '1', title: 'Summer skincare routine',     platform: 'Instagram', status: 'published', date: 'Dec 12', likes: 1243, comments: 87  },
  { id: '2', title: 'Top affiliate picks 2024',    platform: 'Facebook',  status: 'scheduled', date: 'Dec 15', likes: 0,    comments: 0   },
  { id: '3', title: 'How I made $5k with AI',      platform: 'YouTube',   status: 'published', date: 'Dec 10', likes: 3892, comments: 214 },
  { id: '4', title: 'Morning routine tips',        platform: 'Instagram', status: 'draft',     date: 'Dec 18', likes: 0,    comments: 0   },
  { id: '5', title: 'Product review: FitBand Pro', platform: 'Facebook',  status: 'published', date: 'Dec 9',  likes: 892,  comments: 43  },
]

const MOCK_ACTIVITY: ActivityItem[] = [
  { id: '1', message: 'Content generated for Instagram post',        time: '2m ago',  type: 'success' },
  { id: '2', message: 'Campaign "Summer Sale" reached 10K users',    time: '15m ago', type: 'success' },
  { id: '3', message: 'Affiliate link click detected on post #1',    time: '1h ago',  type: 'info'    },
  { id: '4', message: 'YouTube post scheduled for Dec 20',           time: '2h ago',  type: 'info'    },
  { id: '5', message: 'Instagram API token expiring soon',           time: '5h ago',  type: 'warning' },
]

const PLATFORM_STATUS = [
  { name: 'Instagram', connected: true,  followers: '82.3K', abbr: 'IG', color: 'text-pink-400',  bg: 'bg-pink-900/30'  },
  { name: 'Facebook',  connected: true,  followers: '31.5K', abbr: 'FB', color: 'text-blue-400',  bg: 'bg-blue-900/30'  },
  { name: 'YouTube',   connected: false, followers: '10.7K', abbr: 'YT', color: 'text-red-400',   bg: 'bg-red-900/30'   },
]

const STATUS_BADGE: Record<string, string> = {
  published: 'badge-active',
  scheduled: 'badge-paused',
  draft:     'badge-draft',
}

/* ── Component ────────────────────────────────────────── */
export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn:  async () => {
      const { data } = await axios.get('/api/dashboard/stats')
      return data
    },
    initialData: MOCK_STATS,
    retry:       false,
  })

  const s = stats ?? MOCK_STATS

  return (
    <>
      <Head><title>Dashboard – AdsAgent</title></Head>
      <Layout agentRunning>
        <div className="space-y-6 animate-fade-in">

          {/* Stats cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
            <StatsCard
              title="Total Followers"
              value={s.totalFollowers}
              change={s.followerChange}
              icon={<Users className="w-5 h-5 text-white" />}
              iconBg="bg-blue-600"
              loading={statsLoading}
            />
            <StatsCard
              title="Engagement Rate"
              value={s.engagementRate}
              change={s.engagementChange}
              suffix="%"
              icon={<TrendingUp className="w-5 h-5 text-white" />}
              iconBg="bg-green-600"
              loading={statsLoading}
            />
            <StatsCard
              title="Posts Scheduled"
              value={s.postsScheduled}
              change={s.scheduledChange}
              icon={<Calendar className="w-5 h-5 text-white" />}
              iconBg="bg-purple-600"
              loading={statsLoading}
            />
            <StatsCard
              title="Affiliate Revenue"
              value={s.revenue}
              change={s.revenueChange}
              prefix="$"
              icon={<DollarSign className="w-5 h-5 text-white" />}
              iconBg="bg-yellow-600"
              loading={statsLoading}
            />
          </div>

          {/* Charts + Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* Follower growth */}
            <div className="lg:col-span-2 card">
              <h2 className="text-sm font-semibold text-white mb-4">Follower Growth (14 days)</h2>
              <FollowerGrowthChart data={MOCK_GROWTH} height={240} />
            </div>

            {/* Activity feed */}
            <div className="card flex flex-col">
              <h2 className="text-sm font-semibold text-white mb-4">Recent Activity</h2>
              <div className="flex-1 space-y-3 overflow-y-auto">
                {MOCK_ACTIVITY.map((item) => (
                  <div key={item.id} className="flex items-start gap-3">
                    <span className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                      item.type === 'success' ? 'bg-green-400' :
                      item.type === 'warning' ? 'bg-yellow-400' : 'bg-blue-400'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-200 leading-snug">{item.message}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{item.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Platform health + Quick actions */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {/* Platform health */}
            <div className="card">
              <h2 className="text-sm font-semibold text-white mb-4">Platform Health</h2>
              <div className="space-y-3">
                {PLATFORM_STATUS.map((p) => (
                  <div key={p.name} className={`flex items-center justify-between p-3 rounded-lg ${p.bg} border border-surface-border`}>
                    <div className="flex items-center gap-3">
                      <div className={`w-9 h-9 rounded-lg flex items-center justify-center text-xs font-bold ${p.color} bg-black/20`}>
                        {p.abbr}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-white">{p.name}</p>
                        <p className="text-xs text-gray-400">{p.followers} followers</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {p.connected
                        ? <><CheckCircle className="w-4 h-4 text-green-400" /><span className="text-xs text-green-400">Connected</span></>
                        : <><AlertCircle className="w-4 h-4 text-yellow-400" /><Link href="/settings" className="text-xs text-yellow-400 hover:underline">Connect</Link></>
                      }
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick actions */}
            <div className="card">
              <h2 className="text-sm font-semibold text-white mb-4">Quick Actions</h2>
              <div className="grid grid-cols-1 gap-3">
                {[
                  { href: '/content',   label: 'Generate AI Content',  sub: 'Create posts with AI',          icon: Wand2,     iconBg: 'bg-purple-600' },
                  { href: '/content',   label: 'Schedule a Post',       sub: 'Plan your content calendar',    icon: Clock,     iconBg: 'bg-blue-600'   },
                  { href: '/analytics', label: 'View Analytics',        sub: 'See performance insights',      icon: BarChart3, iconBg: 'bg-green-600'  },
                ].map(({ href, label, sub, icon: Icon, iconBg }) => (
                  <Link
                    key={label}
                    href={href}
                    className="flex items-center gap-4 p-3 rounded-xl border border-surface-border hover:border-blue-600/50 hover:bg-blue-900/10 transition-all duration-200 group"
                  >
                    <div className={`w-10 h-10 rounded-xl ${iconBg} flex items-center justify-center flex-shrink-0`}>
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white">{label}</p>
                      <p className="text-xs text-gray-400">{sub}</p>
                    </div>
                    <ExternalLink className="w-4 h-4 text-gray-600 group-hover:text-blue-400 transition-colors flex-shrink-0" />
                  </Link>
                ))}
              </div>
            </div>
          </div>

          {/* Recent posts table */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-white">Recent Posts</h2>
              <Link href="/content" className="text-xs text-blue-400 hover:text-blue-300 transition-colors">
                View all →
              </Link>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-surface-border">
                    <th className="table-header">Post</th>
                    <th className="table-header">Platform</th>
                    <th className="table-header">Status</th>
                    <th className="table-header">Date</th>
                    <th className="table-header text-right">Likes</th>
                    <th className="table-header text-right">Comments</th>
                  </tr>
                </thead>
                <tbody>
                  {MOCK_POSTS.map((post) => (
                    <tr key={post.id} className="table-row">
                      <td className="table-cell font-medium">{post.title}</td>
                      <td className="table-cell">
                        <span className={`text-xs font-medium ${
                          post.platform === 'Instagram' ? 'text-pink-400' :
                          post.platform === 'Facebook'  ? 'text-blue-400' : 'text-red-400'
                        }`}>{post.platform}</span>
                      </td>
                      <td className="table-cell">
                        <span className={STATUS_BADGE[post.status]}>{post.status}</span>
                      </td>
                      <td className="table-cell text-gray-400">{post.date}</td>
                      <td className="table-cell text-right">{post.likes.toLocaleString()}</td>
                      <td className="table-cell text-right">{post.comments.toLocaleString()}</td>
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
