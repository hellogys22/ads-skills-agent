'use client'
import React from 'react'
import {
  LineChart, Line, BarChart, Bar, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell, FunnelChart, Funnel, LabelList,
} from 'recharts'

/* ────────────────────────────────────────────────────────
   Shared tooltip styles
───────────────────────────────────────────────────────── */
const TOOLTIP_STYLE = {
  backgroundColor: '#1f2937',
  border: '1px solid #374151',
  borderRadius: '8px',
  color: '#f9fafb',
  fontSize: 12,
}

const LABEL_STYLE = { fill: '#9ca3af', fontSize: 11 }
const TICK_STYLE  = { fill: '#6b7280', fontSize: 11 }

/* ────────────────────────────────────────────────────────
   Types
───────────────────────────────────────────────────────── */
export interface TimeSeriesPoint {
  date: string
  instagram?: number
  facebook?: number
  youtube?: number
  total?: number
}

export interface PlatformBar {
  platform: string
  value: number
  color: string
}

export interface FunnelStep {
  name: string
  value: number
  fill: string
}

/* ────────────────────────────────────────────────────────
   EngagementChart
───────────────────────────────────────────────────────── */
interface EngagementChartProps {
  data: TimeSeriesPoint[]
  height?: number
}

export function EngagementChart({ data, height = 280 }: EngagementChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis dataKey="date" tick={TICK_STYLE} tickLine={false} axisLine={false} />
        <YAxis tick={TICK_STYLE} tickLine={false} axisLine={false} />
        <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={LABEL_STYLE} />
        <Legend wrapperStyle={{ fontSize: 12, color: '#9ca3af' }} />
        <Line type="monotone" dataKey="instagram" stroke="#ec4899" strokeWidth={2} dot={false} name="Instagram" />
        <Line type="monotone" dataKey="facebook"  stroke="#3b82f6" strokeWidth={2} dot={false} name="Facebook" />
        <Line type="monotone" dataKey="youtube"   stroke="#ef4444" strokeWidth={2} dot={false} name="YouTube" />
      </LineChart>
    </ResponsiveContainer>
  )
}

/* ────────────────────────────────────────────────────────
   PlatformComparisonChart
───────────────────────────────────────────────────────── */
interface PlatformComparisonChartProps {
  data: PlatformBar[]
  height?: number
  title?: string
}

export function PlatformComparisonChart({ data, height = 260 }: PlatformComparisonChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
        <XAxis dataKey="platform" tick={TICK_STYLE} tickLine={false} axisLine={false} />
        <YAxis tick={TICK_STYLE} tickLine={false} axisLine={false} />
        <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={LABEL_STYLE} />
        <Bar dataKey="value" radius={[4, 4, 0, 0]} name="Engagements">
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

/* ────────────────────────────────────────────────────────
   ReachChart (Area)
───────────────────────────────────────────────────────── */
interface ReachChartProps {
  data: TimeSeriesPoint[]
  height?: number
}

export function ReachChart({ data, height = 280 }: ReachChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <defs>
          <linearGradient id="reachGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#2563eb" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#2563eb" stopOpacity={0}   />
          </linearGradient>
          <linearGradient id="impressGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#7c3aed" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#7c3aed" stopOpacity={0}   />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis dataKey="date" tick={TICK_STYLE} tickLine={false} axisLine={false} />
        <YAxis tick={TICK_STYLE} tickLine={false} axisLine={false} />
        <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={LABEL_STYLE} />
        <Legend wrapperStyle={{ fontSize: 12, color: '#9ca3af' }} />
        <Area type="monotone" dataKey="instagram" stroke="#2563eb" fill="url(#reachGrad)"  strokeWidth={2} name="Reach" />
        <Area type="monotone" dataKey="facebook"  stroke="#7c3aed" fill="url(#impressGrad)" strokeWidth={2} name="Impressions" />
      </AreaChart>
    </ResponsiveContainer>
  )
}

/* ────────────────────────────────────────────────────────
   ConversionFunnel
───────────────────────────────────────────────────────── */
interface ConversionFunnelProps {
  data: FunnelStep[]
  height?: number
}

export function ConversionFunnel({ data, height = 300 }: ConversionFunnelProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <FunnelChart>
        <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={LABEL_STYLE} />
        <Funnel dataKey="value" data={data} isAnimationActive>
          <LabelList position="right" fill="#9ca3af" stroke="none" dataKey="name" style={{ fontSize: 12 }} />
          {data.map((entry, index) => (
            <Cell key={`funnel-${index}`} fill={entry.fill} />
          ))}
        </Funnel>
      </FunnelChart>
    </ResponsiveContainer>
  )
}

/* ────────────────────────────────────────────────────────
   FollowerGrowthChart
───────────────────────────────────────────────────────── */
interface FollowerGrowthChartProps {
  data: TimeSeriesPoint[]
  height?: number
}

export function FollowerGrowthChart({ data, height = 280 }: FollowerGrowthChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <defs>
          <linearGradient id="followerGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#10b981" stopOpacity={0.4} />
            <stop offset="95%" stopColor="#10b981" stopOpacity={0}   />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis dataKey="date" tick={TICK_STYLE} tickLine={false} axisLine={false} />
        <YAxis tick={TICK_STYLE} tickLine={false} axisLine={false} />
        <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={LABEL_STYLE} />
        <Area type="monotone" dataKey="total" stroke="#10b981" fill="url(#followerGrad)" strokeWidth={2} name="Followers" />
      </AreaChart>
    </ResponsiveContainer>
  )
}
