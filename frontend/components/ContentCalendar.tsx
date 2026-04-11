'use client'
import React, { useState } from 'react'
import { ChevronLeft, ChevronRight, Plus, X, Instagram, Youtube } from 'lucide-react'
import {
  format, startOfMonth, endOfMonth, eachDayOfInterval,
  isSameMonth, isToday, addMonths, subMonths, getDay,
} from 'date-fns'
import clsx from 'clsx'

interface ScheduledPost {
  id: string
  date: string          // ISO YYYY-MM-DD
  platform: 'instagram' | 'facebook' | 'youtube'
  title: string
  status: 'scheduled' | 'published' | 'draft'
}

const MOCK_POSTS: ScheduledPost[] = [
  { id: '1', date: format(new Date(), 'yyyy-MM-dd'),           platform: 'instagram', title: 'Summer promo post',       status: 'scheduled' },
  { id: '2', date: format(addMonths(new Date(), 0), 'yyyy-MM-') + '10', platform: 'facebook',  title: 'Product launch update',   status: 'scheduled' },
  { id: '3', date: format(addMonths(new Date(), 0), 'yyyy-MM-') + '14', platform: 'youtube',   title: 'Tutorial video',          status: 'draft'     },
  { id: '4', date: format(addMonths(new Date(), 0), 'yyyy-MM-') + '18', platform: 'instagram', title: 'Behind the scenes',       status: 'published' },
  { id: '5', date: format(addMonths(new Date(), 0), 'yyyy-MM-') + '22', platform: 'facebook',  title: 'Weekly tips',             status: 'scheduled' },
]

const PLATFORM_STYLES = {
  instagram: { bg: 'bg-pink-500',  text: 'text-pink-400',  label: 'IG' },
  facebook:  { bg: 'bg-blue-500',  text: 'text-blue-400',  label: 'FB' },
  youtube:   { bg: 'bg-red-500',   text: 'text-red-400',   label: 'YT' },
}

interface PostDetailModalProps {
  post: ScheduledPost
  onClose: () => void
}

function PostDetailModal({ post, onClose }: PostDetailModalProps) {
  const style = PLATFORM_STYLES[post.platform]
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between p-5 border-b border-surface-border">
          <h3 className="font-semibold text-white">Post Details</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white"><X className="w-5 h-5" /></button>
        </div>
        <div className="p-5 space-y-4">
          <div className="flex items-center gap-3">
            <span className={clsx('px-3 py-1 rounded-full text-xs font-bold text-white', style.bg)}>
              {style.label}
            </span>
            <span className="capitalize text-sm text-gray-400">{post.platform}</span>
          </div>
          <div>
            <p className="label">Title</p>
            <p className="text-white font-medium">{post.title}</p>
          </div>
          <div>
            <p className="label">Scheduled Date</p>
            <p className="text-white">{post.date}</p>
          </div>
          <div>
            <p className="label">Status</p>
            <span className={clsx(
              'inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium',
              post.status === 'published' ? 'badge-completed' :
              post.status === 'scheduled' ? 'badge-active' : 'badge-draft'
            )}>
              {post.status}
            </span>
          </div>
          <div className="flex gap-3 pt-2">
            <button className="btn-primary flex-1 justify-center">Edit Post</button>
            <button className="btn-secondary flex-1 justify-center">Delete</button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function ContentCalendar() {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [selectedPost, setSelectedPost] = useState<ScheduledPost | null>(null)
  const [posts] = useState<ScheduledPost[]>(MOCK_POSTS)

  const monthStart = startOfMonth(currentDate)
  const monthEnd   = endOfMonth(currentDate)
  const days       = eachDayOfInterval({ start: monthStart, end: monthEnd })
  const startPad   = getDay(monthStart)

  const getPostsForDay = (day: Date) =>
    posts.filter((p) => p.date === format(day, 'yyyy-MM-dd'))

  return (
    <div className="card">
      {/* Calendar header */}
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-base font-semibold text-white">
          {format(currentDate, 'MMMM yyyy')}
        </h2>
        <div className="flex items-center gap-2">
          {/* Legend */}
          <div className="flex items-center gap-3 mr-4">
            {Object.entries(PLATFORM_STYLES).map(([key, val]) => (
              <div key={key} className="flex items-center gap-1.5">
                <span className={clsx('w-2.5 h-2.5 rounded-full', val.bg)} />
                <span className="text-xs text-gray-400 capitalize">{key}</span>
              </div>
            ))}
          </div>
          <button
            onClick={() => setCurrentDate(subMonths(currentDate, 1))}
            className="btn-secondary p-2"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            onClick={() => setCurrentDate(new Date())}
            className="btn-secondary px-3 py-2 text-xs"
          >
            Today
          </button>
          <button
            onClick={() => setCurrentDate(addMonths(currentDate, 1))}
            className="btn-secondary p-2"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Day-of-week headers */}
      <div className="grid grid-cols-7 gap-1 mb-1">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((d) => (
          <div key={d} className="text-center text-xs font-semibold text-gray-500 py-2">
            {d}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-1">
        {/* Padding cells */}
        {Array.from({ length: startPad }).map((_, i) => (
          <div key={`pad-${i}`} className="h-24 rounded-lg" />
        ))}

        {days.map((day) => {
          const dayPosts   = getPostsForDay(day)
          const sameMonth  = isSameMonth(day, currentDate)
          const todayClass = isToday(day)

          return (
            <div
              key={day.toISOString()}
              className={clsx(
                'h-24 rounded-lg border p-1.5 flex flex-col group transition-colors duration-150',
                todayClass
                  ? 'border-blue-500 bg-blue-900/20'
                  : sameMonth
                  ? 'border-surface-border bg-surface-card hover:border-gray-600'
                  : 'border-transparent bg-transparent opacity-30'
              )}
            >
              <div className="flex items-center justify-between mb-1">
                <span className={clsx('text-xs font-medium', todayClass ? 'text-blue-400' : 'text-gray-400')}>
                  {format(day, 'd')}
                </span>
                <button className="opacity-0 group-hover:opacity-100 transition-opacity w-4 h-4 rounded flex items-center justify-center bg-blue-600 text-white">
                  <Plus className="w-3 h-3" />
                </button>
              </div>
              <div className="flex-1 overflow-hidden space-y-0.5">
                {dayPosts.slice(0, 3).map((post) => (
                  <button
                    key={post.id}
                    onClick={() => setSelectedPost(post)}
                    className={clsx(
                      'w-full text-left text-[10px] px-1.5 py-0.5 rounded font-medium truncate text-white',
                      PLATFORM_STYLES[post.platform].bg,
                      'hover:opacity-80 transition-opacity'
                    )}
                  >
                    {post.title}
                  </button>
                ))}
                {dayPosts.length > 3 && (
                  <p className="text-[10px] text-gray-500 px-1">+{dayPosts.length - 3} more</p>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Post detail modal */}
      {selectedPost && (
        <PostDetailModal post={selectedPost} onClose={() => setSelectedPost(null)} />
      )}
    </div>
  )
}
