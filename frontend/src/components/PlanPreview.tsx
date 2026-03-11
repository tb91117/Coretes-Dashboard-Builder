import type { MediaPlan } from '../types'

interface Props {
  plan: MediaPlan
}

export function PlanPreview({ plan }: Props) {
  const cp = plan.creative_pack
  const th = plan.targeting_hints

  return (
    <div className="space-y-4">
      <div className="rounded-lg bg-slate-800/50 border border-slate-700/50 p-4">
        <h4 className="text-sm font-medium text-slate-400 mb-2">Plan summary</h4>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <span className="text-slate-500">Objective</span>
          <span className="text-slate-200">{plan.objective}</span>
          <span className="text-slate-500">Daily budget</span>
          <span className="text-slate-200">${plan.daily_budget}</span>
          <span className="text-slate-500">Geo</span>
          <span className="text-slate-200">{plan.geo.join(', ')}</span>
          <span className="text-slate-500">Categories</span>
          <span className="text-slate-200">{plan.product_categories.join(', ')}</span>
        </div>
      </div>

      <div className="rounded-lg bg-slate-800/50 border border-slate-700/50 p-4">
        <h4 className="text-sm font-medium text-slate-400 mb-2">Creative pack</h4>
        <div className="space-y-2 text-sm">
          <div>
            <span className="text-slate-500">Headlines:</span>
            <ul className="list-disc list-inside text-slate-300 mt-0.5">
              {cp.headlines.slice(0, 3).map((h, i) => (
                <li key={i}>{h}</li>
              ))}
            </ul>
          </div>
          {cp.descriptions.length > 0 && (
            <div>
              <span className="text-slate-500">Descriptions:</span>
              <p className="text-slate-300 mt-0.5">{cp.descriptions[0]}</p>
            </div>
          )}
          {cp.callouts.length > 0 && (
            <p className="text-slate-400">Callouts: {cp.callouts.join(', ')}</p>
          )}
        </div>
      </div>

      <div className="rounded-lg bg-slate-800/50 border border-slate-700/50 p-4">
        <h4 className="text-sm font-medium text-slate-400 mb-2">Targeting</h4>
        <div className="flex flex-wrap gap-2">
          {th.keywords.slice(0, 5).map((k, i) => (
            <span key={i} className="px-2 py-0.5 rounded bg-slate-700/50 text-slate-300 text-xs">
              {k}
            </span>
          ))}
        </div>
      </div>

      <p className="text-xs text-slate-500">
        Will create: Google Performance Max · Meta Shopping · Amazon Sponsored Brands
      </p>
    </div>
  )
}
