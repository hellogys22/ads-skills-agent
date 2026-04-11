import React from 'react'
import Sidebar from './Sidebar'
import Header from './Header'

interface LayoutProps {
  children: React.ReactNode
  agentRunning?: boolean
}

export default function Layout({ children, agentRunning = false }: LayoutProps) {
  return (
    <div className="flex min-h-screen bg-surface">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header agentRunning={agentRunning} />
        <main className="flex-1 p-6 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
