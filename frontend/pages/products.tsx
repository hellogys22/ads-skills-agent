import React, { useState } from 'react'
import Head from 'next/head'
import Layout from '../components/Layout'
import { Plus, X, Wand2, ExternalLink, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import clsx from 'clsx'

interface Product {
  id:           string
  name:         string
  url:          string
  commissionRate: number
  niche:        string
  description:  string
  clicks:       number
  conversions:  number
  revenue:      number
}

const MOCK_PRODUCTS: Product[] = [
  { id: '1', name: 'Glow Serum Pro',      url: 'https://example.com/glow',    commissionRate: 20, niche: 'Beauty',   description: 'Anti-aging vitamin C serum',   clicks: 1243, conversions: 89,  revenue: 2134 },
  { id: '2', name: 'FitBand Ultra',       url: 'https://example.com/fitband', commissionRate: 15, niche: 'Fitness',  description: 'Smart fitness tracker band',   clicks: 892,  conversions: 54,  revenue: 1620 },
  { id: '3', name: 'CodeMaster Course',   url: 'https://example.com/code',    commissionRate: 40, niche: 'Education',description: 'Learn Python & AI in 30 days', clicks: 567,  conversions: 102, revenue: 4080 },
  { id: '4', name: 'OrganicBlend Coffee', url: 'https://example.com/coffee',  commissionRate: 12, niche: 'Health',   description: 'Premium organic coffee blend', clicks: 321,  conversions: 28,  revenue: 672  },
]

const NICHES = ['Beauty', 'Fitness', 'Education', 'Health', 'Tech', 'Finance', 'Lifestyle', 'Food']

interface PromoteModalProps {
  product: Product
  onClose: () => void
}

function PromoteModal({ product, onClose }: PromoteModalProps) {
  const [platform, setPlatform] = useState('instagram')
  const [loading,  setLoading]  = useState(false)

  async function handlePromote() {
    setLoading(true)
    await new Promise((r) => setTimeout(r, 1000))
    toast.success(`AI content for ${product.name} created on ${platform}!`)
    setLoading(false)
    onClose()
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between p-5 border-b border-surface-border">
          <h3 className="font-semibold text-white">Promote: {product.name}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white"><X className="w-5 h-5" /></button>
        </div>
        <div className="p-5 space-y-4">
          <div>
            <p className="label">Select Platform</p>
            <div className="flex gap-2">
              {['instagram', 'facebook', 'youtube'].map((p) => (
                <button
                  key={p}
                  onClick={() => setPlatform(p)}
                  className={clsx(
                    'flex-1 py-2 rounded-lg text-xs font-medium border capitalize transition-all',
                    platform === p
                      ? 'bg-blue-600 border-blue-500 text-white'
                      : 'border-surface-border text-gray-400 hover:text-white'
                  )}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
          <div className="p-3 rounded-lg bg-surface-input border border-surface-border">
            <p className="text-xs text-gray-400 mb-1">Product</p>
            <p className="text-sm text-white font-medium">{product.name}</p>
            <p className="text-xs text-gray-400 mt-0.5">{product.description}</p>
          </div>
          <button onClick={handlePromote} disabled={loading} className="btn-primary w-full justify-center">
            {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Generating...</> : <><Wand2 className="w-4 h-4" /> Generate & Schedule</>}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function ProductsPage() {
  const [products,      setProducts]      = useState<Product[]>(MOCK_PRODUCTS)
  const [promoteTarget, setPromoteTarget] = useState<Product | null>(null)
  const [showForm,      setShowForm]      = useState(false)
  const [form, setForm] = useState({ name: '', url: '', commissionRate: '', niche: 'Beauty', description: '' })

  function handleAdd(e: React.FormEvent) {
    e.preventDefault()
    if (!form.name || !form.url) { toast.error('Name and URL are required'); return }
    const newProduct: Product = {
      id:   Date.now().toString(),
      name: form.name,
      url:  form.url,
      commissionRate: Number(form.commissionRate) || 10,
      niche: form.niche,
      description: form.description,
      clicks: 0, conversions: 0, revenue: 0,
    }
    setProducts((prev) => [newProduct, ...prev])
    setForm({ name: '', url: '', commissionRate: '', niche: 'Beauty', description: '' })
    setShowForm(false)
    toast.success('Product added!')
  }

  const totalRevenue  = products.reduce((s, p) => s + p.revenue, 0)
  const totalClicks   = products.reduce((s, p) => s + p.clicks, 0)
  const totalConvRate = products.length
    ? (products.reduce((s, p) => s + (p.conversions / (p.clicks || 1)) * 100, 0) / products.length).toFixed(1)
    : '0.0'

  return (
    <>
      <Head><title>Products – AdsAgent</title></Head>
      <Layout>
        <div className="space-y-5 animate-fade-in">

          {/* Summary cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              { label: 'Total Revenue',   value: `$${totalRevenue.toLocaleString()}`, color: 'text-green-400' },
              { label: 'Total Clicks',    value: totalClicks.toLocaleString(),         color: 'text-blue-400'  },
              { label: 'Avg Conv. Rate',  value: `${totalConvRate}%`,                 color: 'text-purple-400' },
            ].map((s) => (
              <div key={s.label} className="card text-center">
                <p className="text-xs text-gray-400 mb-1">{s.label}</p>
                <p className={clsx('text-2xl font-bold', s.color)}>{s.value}</p>
              </div>
            ))}
          </div>

          {/* Add product toggle */}
          <div className="flex justify-between items-center">
            <h2 className="text-base font-semibold text-white">Affiliate Products</h2>
            <button onClick={() => setShowForm(!showForm)} className="btn-primary text-sm">
              <Plus className="w-4 h-4" /> Add Product
            </button>
          </div>

          {/* Add product form */}
          {showForm && (
            <div className="card animate-slide-up">
              <h3 className="text-sm font-semibold text-white mb-4">New Product</h3>
              <form onSubmit={handleAdd} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <p className="label">Product Name *</p>
                  <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Glow Serum Pro" />
                </div>
                <div>
                  <p className="label">Affiliate URL *</p>
                  <input className="input" value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })} placeholder="https://..." />
                </div>
                <div>
                  <p className="label">Commission Rate (%)</p>
                  <input type="number" className="input" value={form.commissionRate} onChange={(e) => setForm({ ...form, commissionRate: e.target.value })} placeholder="20" min="0" max="100" />
                </div>
                <div>
                  <p className="label">Niche</p>
                  <select className="input" value={form.niche} onChange={(e) => setForm({ ...form, niche: e.target.value })}>
                    {NICHES.map((n) => <option key={n}>{n}</option>)}
                  </select>
                </div>
                <div className="sm:col-span-2">
                  <p className="label">Description</p>
                  <textarea className="input resize-none" rows={2} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Brief product description..." />
                </div>
                <div className="sm:col-span-2 flex gap-3">
                  <button type="submit" className="btn-primary">Add Product</button>
                  <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
                </div>
              </form>
            </div>
          )}

          {/* Products table */}
          <div className="card">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-surface-border">
                    <th className="table-header">Product</th>
                    <th className="table-header">Niche</th>
                    <th className="table-header text-right">Commission</th>
                    <th className="table-header text-right">Clicks</th>
                    <th className="table-header text-right">Conversions</th>
                    <th className="table-header text-right">Revenue</th>
                    <th className="table-header text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map((p) => (
                    <tr key={p.id} className="table-row">
                      <td className="table-cell">
                        <div>
                          <p className="font-medium text-white">{p.name}</p>
                          <p className="text-xs text-gray-500 truncate max-w-[180px]">{p.description}</p>
                        </div>
                      </td>
                      <td className="table-cell">
                        <span className="px-2 py-0.5 rounded-full bg-purple-900/40 border border-purple-800 text-purple-300 text-xs">
                          {p.niche}
                        </span>
                      </td>
                      <td className="table-cell text-right text-green-400 font-medium">{p.commissionRate}%</td>
                      <td className="table-cell text-right">{p.clicks.toLocaleString()}</td>
                      <td className="table-cell text-right">{p.conversions}</td>
                      <td className="table-cell text-right font-semibold text-white">${p.revenue.toLocaleString()}</td>
                      <td className="table-cell text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => setPromoteTarget(p)}
                            className="text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1"
                          >
                            <Wand2 className="w-3 h-3" /> Promote
                          </button>
                          <a href={p.url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-400 hover:text-blue-300">
                            <ExternalLink className="w-3.5 h-3.5" />
                          </a>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>

        {promoteTarget && (
          <PromoteModal product={promoteTarget} onClose={() => setPromoteTarget(null)} />
        )}
      </Layout>
    </>
  )
}
