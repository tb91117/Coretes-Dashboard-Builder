export interface Campaign {
  id: number
  platform: string
  platform_campaign_id?: string
  campaign_name: string
  campaign_type: string
  status: string
  spend: number
  impressions: number
  clicks: number
  ctr: number
  conversions: number
  conversion_value: number
  currency: string
}

export interface CreativePack {
  headlines: string[]
  descriptions: string[]
  long_headlines: string[]
  primary_texts: string[]
  callouts: string[]
  image_urls: string[]
  logo_url?: string
}

export interface TargetingHints {
  keywords: string[]
  audiences: string[]
  placements: string[]
}

export interface MediaPlan {
  objective: string
  daily_budget: number
  geo: string[]
  lang: string[]
  product_categories: string[]
  creative_pack: CreativePack
  targeting_hints: TargetingHints
  bidding_strategy: string
}

export interface OptimizationSuggestion {
  campaign_id: number
  platform: string
  issue_detected: string
  recommended_action: string
  reasoning: string
  confidence: number
}
