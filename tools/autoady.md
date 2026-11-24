# AutoAdy tool map

AutoAdy is a hosted connector (an MCP server) that lets your AI read and run ad accounts. The ads jobs in this kit are written for it. This page lists every tool it exposed on the day this file was generated: 151 tools, 67 of them marked read-only by the server.

Generated from the server's own tool list by a script, not written by hand. The live list can change. Ask your agent to list the tools to see today's.

## Connect it

1. Create an account at https://www.autoady.io and connect your ad account there.
2. Add the connector to your AI tool with the address and key AutoAdy gives you. Keep the key in your tool's own settings, never in this folder.
3. Ask: "list my ad accounts". You should see your accounts and nothing should change.

## How the kit treats these tools

- **Read tools** run freely. They look, they change nothing.
- **Every other tool** can spend money or change what is live. The job shows an approval card and stops. With the kit's guard installed in Claude Code, the call is blocked until you type the yes for that card.
- New ads and campaigns are built paused. Turning something on is its own card.
- The kit's never-list still applies: no budget or status change without a card, however sure the AI is.

Read-only below means the server marks the tool as read-only. Anything else is treated as a change.


## Meta Ads: read accounts and results

| Tool | Read-only | What it does |
|---|---|---|
| `get_account_insights` | yes | Get high-level KPI metrics for the ad account: spend, impressions, reach, clicks, CTR, CPM, CPC, frequency, leads, CPL. |
| `get_ads` | yes | Get individual ads inside an ad set with full creative copy: name, status, primary text, headline, description, CTA, link URL, thumbnail, and creative type. |
| `get_adset_insights` | yes | Get performance metrics broken down by ad set within a campaign. |
| `get_adsets` | yes | Get all ad sets inside a campaign, with their status, daily budget, and targeting info. |
| `get_campaign_ad_insights` | yes | Get ad-level performance breakdown for a SPECIFIC campaign. |
| `get_campaign_insights` | yes | Get per-campaign performance: spend, impressions, CTR, CPM, CPC, reach, leads, CPL. |
| `get_connected_account` | yes | Returns the active Meta ad account: name, ID, currency, and its delivery status , whether the account can still spend, why it is disabled if it is not, and any spending limit. |
| `get_top_performers` | yes | Statistically proven winners, grouped by creative dimension: which primary text (copy), headline, landing page, or video hook actually performs best. |
| `get_top_performing_ads` | yes | Find the best-performing ads in the account by spend and conversions. |
| `list_ad_accounts` | yes | List every Meta ad account the user can manage (id, name, currency), and which one is active. |
| `list_campaigns` | yes | List campaigns with their name, status, objective, budget and budget_type (CBO = budget on the campaign, ABO = budget on each ad set). |
| `list_custom_audiences` | yes | List the account's custom + lookalike audiences: id, name, subtype, approximate size, delivery status (read-only). |
| `list_lead_forms` | yes | List the Instant Lead Forms that already exist on the account's Facebook Page, with their ids, names and status. |
| `run_graph_read` | yes | Run a read-only Meta Marketing API (Graph) request and return the JSON. |

## Meta Ads: build and change (approval needed)

| Tool | Read-only | What it does |
|---|---|---|
| `adjust_adset_budget` | no | Adjust the daily budget of an ad set that carries its own budget (ABO , no campaign-level budget). |
| `adjust_campaign_budget` | no | Adjust the daily budget of a CBO campaign (one that has a campaign-level daily budget). |
| `archive_ad` | no | Archive a ad (status ARCHIVED): it stops delivering. |
| `archive_adset` | no | Archive a ad set (status ARCHIVED): every ad in it stops delivering. |
| `archive_campaign` | no | Archive a campaign (status ARCHIVED): the campaign and every ad set and ad in it stop delivering. |
| `bulk_enable_ads` | no | Re-enable multiple paused ads at once. |
| `bulk_pause_ads` | no | Pause multiple ads at once. |
| `create_adset` | no | Create a NEW EMPTY ad set (no ads) in two possible ways. |
| `create_campaign` | no | Create a NEW Meta campaign , the top-level container an ad set and ads live in. |
| `create_custom_audience` | no | Create a WEBSITE custom audience from a pixel rule , entirely via API, no Business Manager. |
| `create_lead_ad` | no | Create a lead-form (instant form) ad from a CUSTOM image URL in an existing ad set. |
| `create_lead_ads` | no | Batch of create_lead_ad , create MANY lead-form ads (each a custom image + its matched copy) in ONE existing ad set in a single call. |
| `create_lead_form` | no | Create a NEW Instant Lead Form , the form that opens when someone taps a lead ad. |
| `create_lookalike_audience` | no | Create a LOOKALIKE audience from an existing custom audience , Meta finds people similar to the seed (e.g. |
| `create_website_ad` | no | Create a WEBSITE (link) ad in an existing ad set , it clicks through to a landing page URL instead of opening an instant form. |
| `create_website_ads` | no | Batch of create_website_ad , create MANY website (link) ads in ONE existing ad set in a single call. |
| `duplicate_ad` | no | Duplicate an ad to a different ad set. |
| `duplicate_adset` | no | Duplicate an ad set to the same or different campaign, preserving its EXACT targeting (city/radius geo, exclusions), bid strategy and bid cap , things create_adset cannot always reproduce. |
| `enable_ad` | no | Re-enable a paused ad by setting its status to ACTIVE. |
| `enable_adset` | no | Re-enable a paused ad set. |
| `pause_ad` | no | Pause a specific ad by setting its status to PAUSED. |
| `pause_adset` | no | Pause an ad set. |
| `scale_budget_relative` | no | Scale a campaign's daily budget by a percentage. |
| `set_campaign_status` | no | Set a campaign's status to ACTIVE (launch it) or PAUSED (stop it). |
| `switch_account` | no | Switch the active Meta ad account that every subsequent tool operates on. |
| `update_adset_targeting` | no | Update specific targeting fields on a LIVE ad set without touching the rest: countries (narrow a broad/Europe-wide set to an exact country list), location_types (['home'] = residents only , removes tr |

## Creative: analysis, briefs and generation

| Tool | Read-only | What it does |
|---|---|---|
| `analyze_creative_performance` | yes | Analyze creative performance by visual style, messaging angle, or hook tactic. |
| `analyze_winning_ad` | yes | Deep analysis of a single ad: returns the actual creative image/video URL, full ad copy (primary text, headline, description, CTA, link), adset targeting (age, gender, locations, interests, behaviors, |
| `approve_creative_brief` | no | Approve a creative brief version so it can generate media. |
| `approve_generation_artifact` | no | Record a reviewer's approval of one generated artifact by artifact_id, with an optional reason. |
| `create_creative_brief` | no | Create a draft creative brief from research: facts, hypothesis, cited snapshots and observations, approved offers and claims, and the image and video direction. |
| `creative_autopsy` | no | Analyze recently failed/paused ads to extract anti-patterns. |
| `creative_matrix` | no | Scientific A/B test: specify angles × hooks × visual styles to generate all combinations (max 27). |
| `edit_creative_brief` | no | Change a creative brief by version_id with a patch of the fields to replace. |
| `enable_creative_loop` | no | Enable the autonomous creative loop: auto-detects fatiguing ads, generates replacements, optionally auto-launches winners. |
| `extract_creative_dna` | no | Extract brand DNA from a website URL: visual identity, voice profile, target avatar, winning patterns, unique mechanism. |
| `find_novelty_candidates` | yes | Compare recent competitor observations against this account's own creative history and return the concepts that are new rather than similar or duplicate, with citations. |
| `generate_from_brief` | no | Start image or video generation from an approved creative brief. |
| `get_creative_analytics` | yes | Creative analytics for the currently selected, authorized ad account: win rate and cost-per-lead by messaging angle, hook, visual style and format; the angle-by-style combo matrix; 28-day cost trends  |
| `get_creative_brief` | yes | Read one creative brief version by version_id, with the evidence it cites. |
| `get_daily_briefing` | yes | Get the account's daily briefing: AI narrative + headline, mood, week-over-week deltas, current winners and bleeders, budget recommendations, and alert/fatigue summary. |
| `get_fatigue_forecast` | yes | Get creative fatigue predictions from the survival analysis engine. |
| `get_generation_status` | yes | Read the state of a generation run by run_id: queued, running, succeeded, failed, cancelled or uncertain, with progress. |
| `get_winning_frameworks` | yes | Review framework evidence within the currently selected, authorized ad account. |
| `multiply_winner` | no | Take a winning ad and generate 10+ variations preserving the winning DNA but rotating visual style, hook, and messaging angle. |
| `reject_generation_artifact` | no | Record a reviewer's rejection of one generated artifact by artifact_id, with an optional reason. |
| `resume_generation` | no | Resume an interrupted generation run by its original idempotency_key. |
| `revoke_creative_brief` | no | Withdraw approval from a creative brief version, with an optional reason. |
| `testimonial_mine` | no | Turn customer testimonial quotes into social proof ad creatives. |
| `trigger_creative_generation` | no | Generate a NEW brand-aware ad image. |
| `url_to_ads` | no | Full pipeline: extract brand DNA from a URL and generate up to 50 ad creative variants across multiple angles, hooks, and visual styles. |

## Analysis, audits, experiments and playbooks

| Tool | Read-only | What it does |
|---|---|---|
| `approve_meta_test_plan` | no | Approve a previewed Meta test plan by sending back the preview with its previewHash and confirmationToken. |
| `assess_experiment` | yes | Assess an experiment by experiment_id: whether the recorded control and variant results are sufficient evidence to learn from, and what is missing if not. |
| `audit_tracking` | yes | Audit the account's conversion tracking health (read-only): Meta Pixel presence + freshness (last fired), server-side/Conversions-API event detection (via pixel stats by source), and UTM hygiene on ad |
| `backtest_rule` | yes | Replay a draft rule over the account's last 30 days of real data BEFORE creating it: how many times it would have fired, which ads it would have hit, and (for pause rules) the spend it would have avoi |
| `content_calendar` | no | Create a multi-week content calendar with themed weeks and angle rotations. |
| `create_experiment` | no | Register a creative experiment: control and variant references, objective, metric, audience, source, provider, a settled measurement window and attribution. |
| `create_rule` | no | Create an automation rule from natural language. |
| `cross_platform_cascade` | no | Generate creatives optimized for multiple platforms: Meta Feed, Meta Reels, TikTok, Pinterest, Website. |
| `diagnose_drop` | yes | Diagnose WHY account performance broke (CPL spiked, leads dried up, results collapsed). |
| `get_account_health` | yes | Compute the account health score (0-100) with 5 components: creative diversity, fatigue risk, budget efficiency, testing velocity, waste level. |
| `get_decision_history` | yes | The account's decision ledger (proof of work): every action AutoAdy or the agent executed , pauses, budget changes, launches , with when, why (source), the before-snapshot, and the MEASURED impact whe |
| `get_findings` | yes | List the open findings from AutoAdy's continuous account scan , the same actionable to-do queue shown on the dashboard (bleeders to kill, winners to scale, anomalies, tracking issues). |
| `get_playbook_template` | yes | Get a multi-week tactical playbook (dated week-by-week checklist) for a campaign window. |
| `get_skill` | yes | Get the full methodology of one AutoAdy media-buying skill by slug , e.g. |
| `get_strategic_synthesis` | yes | Read available account strategy context from the intelligence cache: alerts, forecasts, recommendation candidates, benchmarks, allocation signals and priorities. |
| `get_workflow_status` | yes | Check the status of a running workflow (url_to_ads, multiply_winner, etc.). |
| `list_kill_recommendations` | yes | List the ad kill (pause) recommendations currently cached from strategic analysis, for user review BEFORE anything pauses. |
| `list_learning` | yes | List experiments, results, interpretations and learning candidates for this account, or for one experiment when experiment_id is given. |
| `list_skills` | yes | List AutoAdy's expert media-buying skills (foundation, audit, diagnose, ad-creative-strategist, launch, targeting, scale, playbooks) , opinionated playbooks for managing Meta ads. |
| `placement_optimize` | no | Generate placement-specific creatives: Feed (4:5), Reels (9:16), Stories (9:16), Right Column (1:1). |
| `plan_scale_axis` | yes | Plan HOW to scale a winner , vertical (raise budget), horizontal (duplicate to a new audience), bid-cap (Tichenor), or target-ROAS (Faris) , and return the exact execution parameters (budget step, bid |
| `preview_meta_test_plan` | yes | Build a preview of a Meta creative test plan: scope, brief, approved artifacts, control and variant, objective, metric, allocation, dates, budget, and success and kill rules. |
| `product_launch_blitz` | no | Maximum-scale product launch: generates 50 ads across 6 messaging angles from a single URL. |
| `propose_learning_memory` | no | Propose a learning from an experiment, with the text and the rationale behind it. |
| `record_experiment_result` | no | Record the measured result for one side (control or variant) of an experiment: sample size, spend, events, numerator and denominator, and when the data was fresh. |
| `record_result_interpretation` | no | Attach a written interpretation to an experiment's results, optionally naming the hypothesis. |
| `resolve_finding` | no | Mark one scan finding as resolved/handled so it leaves the findings queue (on the dashboard and in get_findings). |
| `retargeting_ladder` | no | Generate funnel-stage-specific creatives: Cold (awareness), Warm (consideration), Hot (conversion), Buyer (retention). |
| `review_learning_memory` | no | Approve or reject a pending learning candidate by candidateId, with an optional reason. |
| `run_full_audit` | yes | Run a comprehensive audit of the entire ad account. |

## Competitor research

| Tool | Read-only | What it does |
|---|---|---|
| `analyze_competitor` | no | Analyze a competitor's ad strategy using the Meta Ad Library. |
| `audience_mirror` | no | Analyze which demographics convert best and suggest matching avatar descriptions + settings for creative generation. |
| `capture_competitor_snapshot` | no | Search the public Meta Ad Library by page id or search terms in one market and save what it returns as a competitor snapshot. |
| `competitor_creatives` | no | Analyze competitor Meta ads, reverse-engineer their best creatives into templates, then generate your own branded versions using your brand DNA. |
| `create_competitor_change_routine` | no | Start monitoring a tracked competitor source for changes on a cadence in seconds. |
| `dismiss_competitor_change_alert` | no | Dismiss a competitor change alert by alert_id, or restore a dismissed one. |
| `list_competitor_board` | yes | List the tracked competitor board: saved snapshots and change alerts, with filters and cursor paging. |
| `pause_competitor_change_routine` | no | Pause a competitor monitoring routine by routine_id. |
| `refresh_competitor_change_routine` | no | Record one refresh of an active competitor monitoring routine: the content hash observed, when, and with what coverage. |
| `resume_competitor_change_routine` | no | Resume a paused competitor monitoring routine by routine_id, so it checks for changes on its cadence again. |

## Tracking, integrations and business results

| Tool | Read-only | What it does |
|---|---|---|
| `calculate_qualified_lead_cost` | yes | Compute observed cost per lead, cost per qualified lead and qualification rate from ad spend, total leads and qualified leads the user supplies. |
| `get_roi_metrics` | yes | Calculate AutoAdy's ROI for this account: net money saved from pausing bleeders (reconciled against the account's own spend), time saved, performance improvement, and an ROI multiplier of net savings  |
| `integrations_get_status` | yes | Read one CRM or analytics connection status and permissions. |
| `integrations_intelligence_report` | yes | Build a CRM pipeline report from one to four imported integration connections. |
| `integrations_list_connections` | yes | List read-only CRM and analytics connections with account, coverage, and freshness. |
| `integrations_query` | yes | Run a bounded read-only query against a connected CRM or analytics source, including CRM stage history. |
| `list_pixels` | yes | List the Meta Pixels (datasets) on the ad account: id, name, and when each last fired (read-only). |
| `send_pixel_event` | no | Send ONE server-side conversion event to a pixel via the Conversions API. |

## Google Ads

| Tool | Read-only | What it does |
|---|---|---|
| `add_google_keywords` | no | Add up to 100 positive keywords to a Google Ads Search ad group. |
| `add_google_negative_keywords` | no | Exclude search terms from a Google Ads campaign or ad group. |
| `apply_google_recommendation` | no | Apply one of Google's own recommendations. |
| `create_google_conversion_action` | no | Create a website conversion action owned by the selected customer. |
| `create_google_responsive_search_ad` | no | Create a responsive search ad, paused, in an existing Search ad group. |
| `create_google_search_campaign` | no | Create a reviewed Search campaign, PAUSED: its own daily budget, manual CPC, one ad group, one responsive search ad, its keywords, and location and language targeting from countries and languages. |
| `dismiss_google_recommendation` | no | Dismiss one of Google's recommendations so it stops being suggested. |
| `read_google_ads_overview` | yes | Read the workspace's selected Google Ads customer from its saved report: customer, currency, the report window, totals and prior-window totals, every campaign (status, primary status and reasons, dail |
| `remove_google_keyword` | no | Permanently remove one positive keyword. |
| `research_keywords` | yes | Get Google keyword ideas with average monthly search volume, competition and top-of-page bid range, from seed keywords, a landing page URL, or both. |
| `run_gaql` | yes | Run a read-only Google Ads Query Language (GAQL) query against the workspace's selected Google Ads customer and return the rows. |
| `set_google_ad_group_cpc_bid` | no | Change an ad group's default max CPC bid. |
| `set_google_ad_group_status` | no | Pause or enable a Google Ads ad group. |
| `set_google_ad_status` | no | Pause or enable one ad. |
| `set_google_bidding_target` | no | Set the target CPA or target ROAS on a campaign that bids with Maximize conversions, Target CPA, Maximize conversion value or Target ROAS. |
| `set_google_campaign_budget` | no | Change the daily budget on a Google Ads campaign budget. |
| `set_google_campaign_status` | no | Pause or enable a Google Ads campaign. |
| `set_google_conversion_goal` | no | Use or stop using a standard conversion goal (category + origin) for bidding, at account level or for one campaign that uses campaign-specific goals. |
| `set_google_keyword_status` | no | Pause or enable one positive keyword in a Google Ads Search ad group. |
| `update_google_conversion_action` | no | Edit settings of an enabled website conversion action owned by the selected customer. |
| `upload_google_image_asset` | no | Upload an image from a public URL as a reusable Google Ads image asset. |

## TikTok and Microsoft Ads

| Tool | Read-only | What it does |
|---|---|---|
| `get_microsoft_ads_report` | yes | Read Microsoft Advertising campaign performance for the selected account over the last 30 settled days: spend, impressions, clicks and conversions. |
| `get_tiktok_report` | yes | Read TikTok Ads performance for the selected advertiser over the last 30 settled days: spend, impressions, clicks and conversions by campaign, ad group or ad. |
| `list_microsoft_ads_accounts` | yes | List the Microsoft Advertising accounts this workspace's connection can read, and which one is currently selected. |
| `list_tiktok_advertisers` | yes | List the TikTok Ads advertisers this workspace's connection can read, with each one's currency, timezone and status, and which one is currently selected. |

## Organic search, AI traffic and website

| Tool | Read-only | What it does |
|---|---|---|
| `generate_llms_txt` | yes | Generate an llms.txt index for a registered site from the pages the last crawl read, grouped into product, pricing, documentation, writing, company and legal. |
| `get_ai_traffic` | yes | Get which AI assistants (ChatGPT, Claude, Perplexity, Gemini, Copilot and others) sent visits to a registered site, the pages they linked to, and how those visits converted against search and direct. |
| `get_organic_audits` | yes | Get the four Search Console audits for a registered site: queries in striking distance of page one, the site's own pages competing for one query, pages losing clicks against the matched previous windo |
| `get_organic_rankings` | yes | Get the tracked keyword positions for a registered site, with the movement against the last day the provider actually answered. |
| `get_organic_score` | yes | Get a registered site's 0 to 100 Organic score with the arithmetic behind it: a subscore per dimension (technical, indexation, content, structured data, crawler access, internal links, AI citation, ra |
| `get_organic_visibility` | yes | Get which answer engines (ChatGPT, Perplexity, Google AI Overviews, Claude, Gemini) cite a registered site for its tracked buyer questions, how often, and which competitors were cited instead. |
| `get_page_verdicts` | yes | Get the pages of a registered site that the last crawl read, worst first, with every technical and GEO issue found on each and the evidence behind it: title and meta length, H1 count, canonical, struc |
| `get_search_pages` | yes | Get the pages of a registered site that search actually sends people to, from its Search Console capture: clicks, impressions, click-through rate and average position per URL, most impressions first. |
| `get_search_queries` | yes | Get the search queries a registered site actually gets impressions for, from its Search Console capture: clicks, impressions, click-through rate and average position per query, most impressions first, |
| `get_website_installation` | yes | Get the safe GitHub installation connection and latest job status for an analytics website. |
| `list_analytics_websites` | yes | List analytics websites available to the authenticated AutoAdy user. |
| `list_organic_sites` | yes | List the websites this workspace has registered for Organic (SEO, GEO and AI visibility), with their verification state, crawl budget and when each was last crawled. |
| `prepare_website_installation` | no | Inspect a connected GitHub HTML file and prepare an analytics installation preview. |
