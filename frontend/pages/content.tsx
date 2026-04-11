import React, { useState } from 'react'
import Head from 'next/head'
import Layout from '../components/Layout'
import AIContentGenerator from '../components/AIContentGenerator'
import PostScheduler from '../components/PostScheduler'
import ContentCalendar from '../components/ContentCalendar'
import { Wand2, Clock, CalendarDays } from 'lucide-react'
import clsx from 'clsx'

type Tab = 'generate' | 'schedule' | 'calendar'

const TABS: { id: Tab; label: string; icon: React.ReactNode }[] = [
  { id: 'generate', label: 'AI Generator',     icon: <Wand2      className="w-4 h-4" /> },
  { id: 'schedule', label: 'Schedule Post',    icon: <Clock      className="w-4 h-4" /> },
  { id: 'calendar', label: 'Content Calendar', icon: <CalendarDays className="w-4 h-4" /> },
]

export default function ContentPage() {
  const [activeTab, setActiveTab]       = useState<Tab>('generate')
  const [schedulerContent, setSchedulerContent] = useState('')

  function handleScheduleFromGenerator(content: { content: string }) {
    setSchedulerContent(content.content)
    setActiveTab('schedule')
  }

  return (
    <>
      <Head><title>Content – AdsAgent</title></Head>
      <Layout>
        <div className="space-y-5 animate-fade-in">
          {/* Tab bar */}
          <div className="flex gap-1 p-1 bg-surface-card border border-surface-border rounded-xl w-fit">
            {TABS.map(({ id, label, icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={clsx(
                  'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                  activeTab === id
                    ? 'bg-brand-blue text-white shadow-glow'
                    : 'text-gray-400 hover:text-white'
                )}
              >
                {icon}
                {label}
              </button>
            ))}
          </div>

          {/* Tab content */}
          {activeTab === 'generate' && (
            <div className="max-w-2xl">
              <AIContentGenerator onSchedule={handleScheduleFromGenerator} />
            </div>
          )}

          {activeTab === 'schedule' && (
            <div className="max-w-2xl">
              <PostScheduler
                initialContent={schedulerContent}
                onScheduled={() => setSchedulerContent('')}
              />
            </div>
          )}

          {activeTab === 'calendar' && (
            <ContentCalendar />
          )}
        </div>
      </Layout>
    </>
  )
}
