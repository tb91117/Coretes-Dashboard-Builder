import type { Campaign, OptimizationSuggestion } from '../types'

const PLATFORM_COLORS: Record<string, string> = {
  google: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  meta: 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30',
  amazon: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
}

const STATUS_STYLES: Record<string, string> = {
  active: 'bg-emerald-500/20 text-emerald-400',
  pending: 'bg-amber-500/20 text-amber-400',
  failed: 'bg-red-500/20 text-red-400',
}

interface Props {
  campaigns: Campaign[]
  suggestions: OptimizationSuggestion[]
  platformFilter: string
  typeFilter: string
  onPlatformFilterChange: (v: string) => void
  onTypeFilterChange: (v: string) => void
  onCreateCampaigns: () => void
}

export function Dashboard({ campaigns, suggestions, platformFilter, typeFilter, onPlatformFilterChange, onTypeFilterChange, onCreateCampaigns }: Props) {
  const platformColor = (p: string) => PLATFORM_COLORS[p] ?? 'bg-slate-500/20 text-slate-400'
  const statusStyle = (s: string) => STATUS_STYLES[s] ?? 'bg-slate-500/20 text-slate-400'

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="font-display font-semibold text-2xl text-white">Campaigns</h2>
          <p className="text-slate-400 text-sm mt-0.5">All platforms · Last 7 days</p>
        </div>
        <button
          onClick={onCreateCampaigns}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-white font-medium transition-all shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 hover:scale-[1.02] active:scale-[0.98]"
        >
          <span className="text-lg">+</span>
          Create Campaigns
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <div>
          <label className="block text-xs text-slate-500 mb-1.5">Platform</label>
          <select
            value={platformFilter}
            onChange={(e) => onPlatformFilterChange(e.target.value)}
            className="w-40 px-3 py-2 rounded-lg bg-slate-800/80 border border-slate-600/50 text-slate-200 text-sm focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 outline-none"
          >
            <option value="">All</option>
            <option value="google">Google</option>
            <option value="meta">Meta</option>
            <option value="amazon">Amazon</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-slate-500 mb-1.5">Campaign type</label>
          <select
            value={typeFilter}
            onChange={(e) => onTypeFilterChange(e.target.value)}
            className="w-48 px-3 py-2 rounded-lg bg-slate-800/80 border border-slate-600/50 text-slate-200 text-sm focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 outline-none"
          >
            <option value="">All</option>
            <option value="pmax">Performance Max</option>
            <option value="shopping">Shopping</option>
            <option value="sponsored_brands">Sponsored Brands</option>
          </select>
        </div>
      </div>

      {/* Optimization Suggestions */}
      {suggestions.length > 0 && (
        <div className="rounded-xl bg-slate-800/50 border border-slate-700/50 p-5">
          <h3 className="font-display font-medium text-slate-200 mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
            Optimization suggestions
          </h3>
          <div className="space-y-3">
            {suggestions.map((s, i) => (
              <div key={i} className="flex flex-col sm:flex-row sm:items-start gap-3 p-4 rounded-lg bg-slate-900/60 border border-slate-700/30">
                <div className="flex-1">
                  <p className="text-sm font-medium text-slate-200">{s.issue_detected}</p>
                  <p className="text-sm text-emerald-400/90 mt-0.5">{s.recommended_action}</p>
                  <p className="text-xs text-slate-500 mt-1">{s.reasoning}</p>
                </div>
                <span className="text-xs px-2 py-1 rounded bg-slate-700/50 text-slate-400 shrink-0">
                  {Math.round(s.confidence * 100)}% confidence
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Table */}
      <div className="rounded-xl border border-slate-700/50 overflow-hidden bg-slate-800/30">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700/50 bg-slate-800/50">
                <th className="text-left py-4 px-5 text-slate-400 font-medium">Platform</th>
                <th className="text-left py-4 px-5 text-slate-400 font-medium">Campaign Name</th>
                <th className="text-left py-4 px-5 text-slate-400 font-medium">Type</th>
                <th className="text-left py-4 px-5 text-slate-400 font-medium">Status</th>
                <th className="text-right py-4 px-5 text-slate-400 font-medium">Spend</th>
                <th className="text-right py-4 px-5 text-slate-400 font-medium">Impressions</th>
                <th className="text-right py-4 px-5 text-slate-400 font-medium">Clicks</th>
                <th className="text-right py-4 px-5 text-slate-400 font-medium">CTR</th>
                <th className="text-right py-4 px-5 text-slate-400 font-medium">Conv. Value</th>
              </tr>
            </thead>
            <tbody>
              {campaigns.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-16 text-center text-slate-500">
                    No campaigns yet. Click <strong className="text-emerald-400">Create Campaigns</strong> to get started.
                  </td>
                </tr>
              ) : (
                campaigns.map((c) => (
                  <tr key={c.id} className="border-b border-slate-700/30 hover:bg-slate-800/30 transition-colors">
                    <td className="py-4 px-5">
                      <span className={`inline-flex px-2.5 py-1 rounded-md text-xs font-medium border ${platformColor(c.platform)}`}>
                        {c.platform}
                      </span>
                    </td>
                    <td className="py-4 px-5 font-medium text-slate-200">{c.campaign_name}</td>
                    <td className="py-4 px-5 text-slate-400">{c.campaign_type.replace('_', ' ')}</td>
                    <td className="py-4 px-5">
                      <span className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${statusStyle(c.status)}`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="py-4 px-5 text-right text-slate-300">${c.spend.toFixed(2)}</td>
                    <td className="py-4 px-5 text-right text-slate-300">{c.impressions.toLocaleString()}</td>
                    <td className="py-4 px-5 text-right text-slate-300">{c.clicks.toLocaleString()}</td>
                    <td className="py-4 px-5 text-right text-slate-300">{c.ctr.toFixed(2)}%</td>
                    <td className="py-4 px-5 text-right text-emerald-400/90">${c.conversion_value.toFixed(2)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
