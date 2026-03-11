import { useState, useEffect } from 'react'
import { Dashboard } from './components/Dashboard'
import { CreateModal } from './components/CreateModal'
import type { Campaign, MediaPlan, OptimizationSuggestion } from './types'

const API = '/api'

async function fetchJSON<T>(url: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(url, { ...opts, headers: { 'Content-Type': 'application/json', ...opts?.headers } })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export default function App() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [suggestions, setSuggestions] = useState<OptimizationSuggestion[]>([])
  const [platformFilter, setPlatformFilter] = useState<string>('')
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [modalOpen, setModalOpen] = useState(false)
  const [plan, setPlan] = useState<MediaPlan | null>(null)
  const [planLoading, setPlanLoading] = useState(false)
  const [createLoading, setCreateLoading] = useState(false)
  const [createStep, setCreateStep] = useState<'input' | 'preview'>('input')

  const loadCampaigns = async () => {
    const params = new URLSearchParams()
    if (platformFilter) params.set('platform', platformFilter)
    if (typeFilter) params.set('campaign_type', typeFilter)
    const data = await fetchJSON<Campaign[]>(`${API}/campaigns?${params}`)
    setCampaigns(data)
  }

  const loadSuggestions = async () => {
    try {
      const data = await fetchJSON<OptimizationSuggestion[]>(`${API}/optimization/suggestions`)
      setSuggestions(data)
    } catch {
      setSuggestions([])
    }
  }

  useEffect(() => { loadCampaigns() }, [platformFilter, typeFilter])
  useEffect(() => { if (campaigns.length > 0) loadSuggestions() }, [campaigns])

  const handleGeneratePlan = async (input: { objective: string; daily_budget: number; product_categories: string[]; country?: string; language?: string }) => {
    setPlanLoading(true)
    try {
      const p = await fetchJSON<MediaPlan>(`${API}/planner/generate`, {
        method: 'POST',
        body: JSON.stringify(input),
      })
      setPlan(p)
      setCreateStep('preview')
    } finally {
      setPlanLoading(false)
    }
  }

  const handleCreateAll = async () => {
    if (!plan) return
    setCreateLoading(true)
    try {
      await fetchJSON(`${API}/campaigns/create-all`, {
        method: 'POST',
        body: JSON.stringify(plan),
      })
      setModalOpen(false)
      setPlan(null)
      setCreateStep('input')
      loadCampaigns()
      setTimeout(loadSuggestions, 500)
    } finally {
      setCreateLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-60 bg-slate-900/80 border-r border-slate-700/50 flex flex-col">
        <div className="p-6">
          <h1 className="font-display font-bold text-xl tracking-tight text-white">Coretas</h1>
          <p className="text-xs text-slate-400 mt-1">Campaign Auto-Builder</p>
        </div>
        <nav className="flex-1 px-3">
          <a href="#" className="flex items-center gap-3 px-4 py-3 rounded-lg bg-slate-800/60 text-emerald-400 font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            Dashboard
          </a>
        </nav>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto">
        <div className="p-8 max-w-7xl mx-auto">
          <Dashboard
            campaigns={campaigns}
            suggestions={suggestions}
            platformFilter={platformFilter}
            typeFilter={typeFilter}
            onPlatformFilterChange={setPlatformFilter}
            onTypeFilterChange={setTypeFilter}
            onCreateCampaigns={() => setModalOpen(true)}
          />
        </div>
      </main>

      {modalOpen && (
        <CreateModal
          onClose={() => { setModalOpen(false); setPlan(null); setCreateStep('input') }}
          step={createStep}
          plan={plan}
          planLoading={planLoading}
          createLoading={createLoading}
          onGeneratePlan={handleGeneratePlan}
          onCreateAll={handleCreateAll}
          onBack={() => setCreateStep('input')}
        />
      )}
    </div>
  )
}
