'use client'
import React, { useState } from 'react'
import axios from 'axios'
import { Wand2, Copy, Clock, Check, Loader2, Hash } from 'lucide-react'
import toast from 'react-hot-toast'
import clsx from 'clsx'

const PLATFORMS   = ['Instagram', 'Facebook', 'YouTube'] as const
const TONES       = ['Professional', 'Casual', 'Exciting', 'Educational'] as const
const MOCK_PRODUCTS = [
  { id: '1', name: 'Glow Serum Pro' },
  { id: '2', name: 'FitBand Ultra' },
  { id: '3', name: 'CodeMaster Course' },
]

type Platform = typeof PLATFORMS[number]
type Tone     = typeof TONES[number]

interface GeneratedContent {
  content:   string
  hashtags:  string[]
  platform:  Platform
}

const PLATFORM_COLORS: Record<Platform, string> = {
  Instagram: 'border-pink-500/50 bg-pink-900/10',
  Facebook:  'border-blue-500/50 bg-blue-900/10',
  YouTube:   'border-red-500/50 bg-red-900/10',
}

interface AIContentGeneratorProps {
  onSchedule?: (content: GeneratedContent) => void
}

export default function AIContentGenerator({ onSchedule }: AIContentGeneratorProps) {
  const [platform,   setPlatform]   = useState<Platform>('Instagram')
  const [product,    setProduct]    = useState(MOCK_PRODUCTS[0].id)
  const [tone,       setTone]       = useState<Tone>('Casual')
  const [topic,      setTopic]      = useState('')
  const [loading,    setLoading]    = useState(false)
  const [generated,  setGenerated]  = useState<GeneratedContent | null>(null)
  const [editedText, setEditedText] = useState('')
  const [copied,     setCopied]     = useState(false)

  async function handleGenerate() {
    if (!topic.trim()) {
      toast.error('Please enter a topic')
      return
    }
    setLoading(true)
    try {
      const productName = MOCK_PRODUCTS.find((p) => p.id === product)?.name ?? ''
      const { data } = await axios.post('/api/content/generate', {
        platform: platform.toLowerCase(),
        topic,
        tone: tone.toLowerCase(),
        product: productName,
      })
      const result: GeneratedContent = {
        content:  data.content  ?? `🌟 ${topic}\n\nDiscover the amazing ${productName} – your next ${tone.toLowerCase()} essential!\n\nTap the link in bio to learn more. 🔗`,
        hashtags: data.hashtags ?? ['#sponsored', '#affiliate', `#${productName.toLowerCase().replace(/\s/g, '')}`, '#trending', '#musthave'],
        platform,
      }
      setGenerated(result)
      setEditedText(result.content)
    } catch {
      // Use mock content when API is unavailable
      const productName = MOCK_PRODUCTS.find((p) => p.id === product)?.name ?? 'Product'
      const mock: GeneratedContent = {
        content:  `✨ ${topic} ✨\n\nHave you tried ${productName} yet? I've been obsessed lately! Here's why you need it in your life:\n\n🔥 Game-changing results in just 2 weeks\n💡 Perfect for your daily routine\n⭐ Rated #1 by thousands of users\n\nUse my exclusive link to get 20% off! Limited time only. 👇`,
        hashtags: ['#affiliate', '#sponsored', '#musthave', '#trending', '#deal'],
        platform,
      }
      setGenerated(mock)
      setEditedText(mock.content)
    } finally {
      setLoading(false)
    }
  }

  async function handleCopy() {
    await navigator.clipboard.writeText(editedText + '\n\n' + (generated?.hashtags.join(' ') ?? ''))
    setCopied(true)
    toast.success('Copied to clipboard!')
    setTimeout(() => setCopied(false), 2000)
  }

  function handleSchedule() {
    if (!generated) return
    onSchedule?.({ ...generated, content: editedText })
    toast.success('Content sent to scheduler!')
  }

  return (
    <div className="space-y-5">
      {/* Form */}
      <div className="card space-y-4">
        <div className="flex items-center gap-2 mb-1">
          <Wand2 className="w-4 h-4 text-purple-400" />
          <h3 className="text-sm font-semibold text-white">AI Content Generator</h3>
        </div>

        {/* Platform selector */}
        <div>
          <p className="label">Platform</p>
          <div className="flex gap-2">
            {PLATFORMS.map((p) => (
              <button
                key={p}
                onClick={() => setPlatform(p)}
                className={clsx(
                  'flex-1 py-2 rounded-lg text-sm font-medium border transition-all duration-200',
                  platform === p
                    ? 'bg-blue-600 border-blue-500 text-white'
                    : 'border-surface-border text-gray-400 hover:border-gray-500 hover:text-white'
                )}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        {/* Tone selector */}
        <div>
          <p className="label">Tone</p>
          <div className="flex gap-2 flex-wrap">
            {TONES.map((t) => (
              <button
                key={t}
                onClick={() => setTone(t)}
                className={clsx(
                  'px-3 py-1.5 rounded-lg text-xs font-medium border transition-all duration-200',
                  tone === t
                    ? 'bg-purple-700 border-purple-600 text-white'
                    : 'border-surface-border text-gray-400 hover:border-gray-500 hover:text-white'
                )}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Product selector */}
        <div>
          <p className="label">Product</p>
          <select
            value={product}
            onChange={(e) => setProduct(e.target.value)}
            className="input"
          >
            {MOCK_PRODUCTS.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>

        {/* Topic */}
        <div>
          <p className="label">Topic / Prompt</p>
          <textarea
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            rows={2}
            className="input resize-none"
            placeholder="e.g. Why skincare routine matters in summer..."
          />
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="btn-primary w-full justify-center"
        >
          {loading ? (
            <><Loader2 className="w-4 h-4 animate-spin" /> Generating...</>
          ) : (
            <><Wand2 className="w-4 h-4" /> Generate Content</>
          )}
        </button>
      </div>

      {/* Generated content preview */}
      {generated && (
        <div className={clsx('card border-2 animate-slide-up', PLATFORM_COLORS[generated.platform])}>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-white">Generated Content</h3>
            <div className="flex gap-2">
              <button onClick={handleCopy} className="btn-secondary text-xs py-1.5 px-3">
                {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
                {copied ? 'Copied!' : 'Copy'}
              </button>
              <button onClick={handleSchedule} className="btn-primary text-xs py-1.5 px-3">
                <Clock className="w-3.5 h-3.5" />
                Schedule
              </button>
            </div>
          </div>

          <textarea
            value={editedText}
            onChange={(e) => setEditedText(e.target.value)}
            rows={7}
            className="input resize-none mb-3 text-sm"
          />

          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <Hash className="w-3.5 h-3.5 text-blue-400" />
              <p className="text-xs font-medium text-gray-400">Suggested Hashtags</p>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {generated.hashtags.map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-0.5 rounded-full bg-blue-900/40 border border-blue-800 text-blue-300 text-xs"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
