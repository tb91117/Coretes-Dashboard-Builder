import { useState } from 'react'
import { PlanPreview } from './PlanPreview'
import type { MediaPlan } from '../types'

interface InputForm {
  objective: string
  daily_budget: string
  product_categories: string
  country: string
  language: string
}

interface Props {
  onClose: () => void
  step: 'input' | 'preview'
  plan: MediaPlan | null
  planLoading: boolean
  createLoading: boolean
  onGeneratePlan: (input: { objective: string; daily_budget: number; product_categories: string[]; country?: string; language?: string }) => Promise<void>
  onCreateAll: () => Promise<void>
  onBack: () => void
}

export function CreateModal({ onClose, step, plan, planLoading, createLoading, onGeneratePlan, onCreateAll, onBack }: Props) {
  const [form, setForm] = useState<InputForm>({
    objective: 'sales',
    daily_budget: '100',
    product_categories: 'running shoes, trail gear',
    country: 'US',
    language: 'en',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const categories = form.product_categories.split(/[,;]/).map((s) => s.trim()).filter(Boolean)
    if (categories.length === 0) return
    const budget = parseFloat(form.daily_budget)
    if (isNaN(budget) || budget < 1) return
    onGeneratePlan({
      objective: form.objective,
      daily_budget: budget,
      product_categories: categories,
      country: form.country || undefined,
      language: form.language || undefined,
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div
        className="w-full max-w-2xl max-h-[90vh] overflow-auto rounded-2xl bg-slate-900 border border-slate-700 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sticky top-0 z-10 flex items-center justify-between px-6 py-4 border-b border-slate-700 bg-slate-900/95 backdrop-blur">
          <h2 className="font-display font-semibold text-lg text-white">
            {step === 'input' ? 'Create Campaigns' : 'Preview & Create'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-6">
          {step === 'input' ? (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Objective</label>
                <select
                  value={form.objective}
                  onChange={(e) => setForm((f) => ({ ...f, objective: e.target.value }))}
                  className="w-full px-4 py-2.5 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 outline-none"
                >
                  <option value="sales">Sales</option>
                  <option value="leads">Leads</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Daily Budget ($)</label>
                <input
                  type="number"
                  min={1}
                  step={1}
                  value={form.daily_budget}
                  onChange={(e) => setForm((f) => ({ ...f, daily_budget: e.target.value }))}
                  className="w-full px-4 py-2.5 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Product Categories (comma or semicolon separated)</label>
                <input
                  type="text"
                  placeholder="running shoes, trail gear"
                  value={form.product_categories}
                  onChange={(e) => setForm((f) => ({ ...f, product_categories: e.target.value }))}
                  className="w-full px-4 py-2.5 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 outline-none"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Country (optional)</label>
                  <input
                    type="text"
                    placeholder="US"
                    value={form.country}
                    onChange={(e) => setForm((f) => ({ ...f, country: e.target.value }))}
                    className="w-full px-4 py-2.5 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Language (optional)</label>
                  <input
                    type="text"
                    placeholder="en"
                    value={form.language}
                    onChange={(e) => setForm((f) => ({ ...f, language: e.target.value }))}
                    className="w-full px-4 py-2.5 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 outline-none"
                  />
                </div>
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  type="submit"
                  disabled={planLoading}
                  className="flex-1 py-2.5 rounded-lg bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-white font-medium transition-colors"
                >
                  {planLoading ? 'Generating plan…' : 'Generate Plan'}
                </button>
                <button
                  type="button"
                  onClick={onClose}
                  className="px-5 py-2.5 rounded-lg border border-slate-600 text-slate-300 hover:bg-slate-800 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <div className="space-y-6">
              {plan && <PlanPreview plan={plan} />}
              <div className="flex gap-3 pt-2">
                <button
                  onClick={onCreateAll}
                  disabled={createLoading}
                  className="flex-1 py-2.5 rounded-lg bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-white font-medium transition-colors"
                >
                  {createLoading ? 'Creating…' : 'Create All'}
                </button>
                <button
                  onClick={onBack}
                  disabled={createLoading}
                  className="px-5 py-2.5 rounded-lg border border-slate-600 text-slate-300 hover:bg-slate-800 transition-colors"
                >
                  Back
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
