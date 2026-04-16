import React from 'react'
import clsx from 'clsx'

interface StatsCardProps {
  title: string
  value: string | number
  change?: number
  icon: React.ReactNode
  iconBg?: string
  loading?: boolean
  suffix?: string
  prefix?: string
}

export default function StatsCard({
  title,
  value,
  change,
  icon,
  iconBg = 'bg-blue-600',
  loading = false,
  suffix = '',
  prefix = '',
}: StatsCardProps) {
  const isPositive = change !== undefined && change >= 0

  if (loading) {
    return (
      <div className="stat-card">
        <div className="flex-1">
          <div className="shimmer h-4 w-24 rounded mb-3" />
          <div className="shimmer h-8 w-32 rounded mb-2" />
          <div className="shimmer h-3 w-20 rounded" />
        </div>
        <div className={clsx('w-12 h-12 rounded-xl shimmer', iconBg)} />
      </div>
    )
  }

  return (
    <div className="stat-card animate-fade-in">
      <div className="flex-1">
        <p className="text-sm font-medium text-gray-400">{title}</p>
        <p className="text-2xl font-bold text-white mt-1">
          {prefix}
          {typeof value === 'number' ? value.toLocaleString() : value}
          {suffix}
        </p>
        {change !== undefined && (
          <div className={clsx('flex items-center gap-1 mt-2 text-xs font-medium',
            isPositive ? 'text-green-400' : 'text-red-400'
          )}>
            <span>{isPositive ? '▲' : '▼'}</span>
            <span>{Math.abs(change).toFixed(1)}% vs last period</span>
          </div>
        )}
      </div>
      <div className={clsx('w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ml-4', iconBg)}>
        {icon}
      </div>
    </div>
  )
}
