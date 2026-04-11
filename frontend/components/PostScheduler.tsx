'use client'
import React, { useState } from 'react'
import { Calendar, Clock, X, Image, Plus, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import clsx from 'clsx'
import { format, addDays } from 'date-fns'

const PLATFORMS = [
  { id: 'instagram', label: 'Instagram', color: 'border-pink-500 text-pink-400  bg-pink-900/20'  },
  { id: 'facebook',  label: 'Facebook',  color: 'border-blue-500 text-blue-400  bg-blue-900/20'  },
  { id: 'youtube',   label: 'YouTube',   color: 'border-red-500  text-red-400   bg-red-900/20'   },
] as const

interface PostSchedulerProps {
  initialContent?: string
  onScheduled?: () => void
}

export default function PostScheduler({ initialContent = '', onScheduled }: PostSchedulerProps) {
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['instagram'])
  const [content, setContent]     = useState(initialContent)
  const [hashtags, setHashtags]   = useState('')
  const [scheduleDate, setScheduleDate] = useState(format(addDays(new Date(), 1), "yyyy-MM-dd'T'HH:mm"))
  const [loading, setLoading]     = useState(false)
  const [hasImage, setHasImage]   = useState(false)

  const charLimit = selectedPlatforms.includes('instagram') ? 2200 : selectedPlatforms.includes('facebook') ? 63206 : 5000
  const charCount = content.length

  function togglePlatform(id: string) {
    setSelectedPlatforms((prev) =>
      prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]
    )
  }

  async function handleSchedule() {
    if (!content.trim()) { toast.error('Content cannot be empty'); return }
    if (selectedPlatforms.length === 0) { toast.error('Select at least one platform'); return }

    setLoading(true)
    try {
      // POST to backend (gracefully handles missing backend)
      await fetch('/api/posts/schedule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          platforms: selectedPlatforms,
          content,
          hashtags: hashtags.split(/\s+/).filter(Boolean),
          scheduled_at: scheduleDate,
        }),
      })
    } catch {
      // ignore network errors in demo
    }
    toast.success(`Post scheduled for ${format(new Date(scheduleDate), 'MMM d, h:mm a')}!`)
    setLoading(false)
    setContent('')
    setHashtags('')
    onScheduled?.()
  }

  return (
    <div className="card space-y-4">
      {/* Platform multi-select */}
      <div>
        <p className="label">Platforms</p>
        <div className="flex gap-2">
          {PLATFORMS.map((p) => (
            <button
              key={p.id}
              onClick={() => togglePlatform(p.id)}
              className={clsx(
                'flex-1 py-2 rounded-lg text-xs font-medium border-2 transition-all duration-200',
                selectedPlatforms.includes(p.id)
                  ? p.color
                  : 'border-surface-border text-gray-500 hover:border-gray-600'
              )}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content textarea */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <p className="label">Content</p>
          <span className={clsx('text-xs', charCount > charLimit ? 'text-red-400' : 'text-gray-500')}>
            {charCount}/{charLimit}
          </span>
        </div>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={6}
          className="input resize-none"
          placeholder="Write your post content here..."
        />
      </div>

      {/* Hashtags */}
      <div>
        <p className="label">Hashtags</p>
        <input
          type="text"
          value={hashtags}
          onChange={(e) => setHashtags(e.target.value)}
          className="input"
          placeholder="#marketing #affiliate #trending"
        />
      </div>

      {/* Image upload placeholder */}
      <div>
        <p className="label">Media</p>
        {hasImage ? (
          <div className="relative rounded-lg bg-surface-input border border-surface-border overflow-hidden h-32 flex items-center justify-center">
            <div className="w-16 h-16 rounded-xl bg-blue-900/40 flex items-center justify-center">
              <Image className="w-8 h-8 text-blue-400" />
            </div>
            <button
              onClick={() => setHasImage(false)}
              className="absolute top-2 right-2 w-6 h-6 rounded-full bg-red-600 flex items-center justify-center"
            >
              <X className="w-3 h-3 text-white" />
            </button>
          </div>
        ) : (
          <button
            onClick={() => setHasImage(true)}
            className="w-full h-24 rounded-lg border-2 border-dashed border-surface-border hover:border-blue-500 flex flex-col items-center justify-center gap-2 text-gray-500 hover:text-blue-400 transition-all duration-200"
          >
            <Plus className="w-5 h-5" />
            <span className="text-xs">Upload image or video</span>
          </button>
        )}
      </div>

      {/* Date/time picker */}
      <div>
        <p className="label">Schedule Date & Time</p>
        <div className="relative">
          <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
          <input
            type="datetime-local"
            value={scheduleDate}
            onChange={(e) => setScheduleDate(e.target.value)}
            className="input pl-9"
          />
        </div>
      </div>

      <button
        onClick={handleSchedule}
        disabled={loading || charCount > charLimit}
        className="btn-primary w-full justify-center"
      >
        {loading ? (
          <><Loader2 className="w-4 h-4 animate-spin" /> Scheduling...</>
        ) : (
          <><Clock className="w-4 h-4" /> Schedule Post</>
        )}
      </button>
    </div>
  )
}
