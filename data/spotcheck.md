# Methodology spot-check

> Pre-tagged labels in `summary.json` are almost certainly LLM-generated.
> Treating them as ground truth would only measure 'does our LLM agree with their LLM?'
> Instead: 12-transcript stratified sample, one-line reasoning per disagreement.
> Disagreement is INFORMATION about taxonomy/extractor quality, not error.

| Meeting | Call type (ours) | Topics — disagreement | Risk signals (ours / pre-tag types) |
|---|---|---|---|
| `7C24624D` Competitive Landscape Review | internal (0.85) | ours add: go-to-market & competitive>competitive positioning, go-to-market & competitive>sales enablement, product & engineering delivery>feature requests; pre-tag adds: competitive analysis, compliance features, pricing pressure | ours=['blocker', 'churn', 'escalation'] / pre-tag=['action_item', 'concern', 'feature_gap', 'positive_pivot'] |
| `080D92AB` Detect Team - Sprint Planning | internal (0.85) | ours add: product & engineering delivery>qa & release readiness, product & engineering delivery>sprint execution, reliability & incidents>post-mortem & rca; pre-tag adds: capacity planning, ci/cd improvement, pipeline architecture | ours=['blocker'] / pre-tag=['action_item', 'feature_gap', 'positive_pivot', 'technical_issue'] |
| `16C9E300` Weekly Engineering Standup | internal (0.85) | ours add: compliance & comply product>comply v2 launch, product & engineering delivery>qa & release readiness, product & engineering delivery>sprint execution; pre-tag adds: circuit breaker, compliance bug, incident response | ours=['blocker', 'churn', 'escalation'] / pre-tag=['action_item', 'concern', 'feature_gap', 'technical_issue'] |
| `C55ADCF8` Protect Performance - Scalability Concerns | internal (0.95) | ours add: customer accounts & renewals>upsell & expansion, go-to-market & competitive>sales enablement, product & engineering delivery>quarterly planning; pre-tag adds: architecture scalability, backup infrastructure, incident risk | ours=['blocker', 'churn', 'escalation'] / pre-tag=['churn_signal', 'concern', 'feature_gap', 'technical_issue'] |
| `E4A98889` Support Case #7572 - Brightpath Commerce I | support (0.98) | ours add: customer accounts & renewals>account roadmap reviews, reliability & incidents>backup performance, support cases>billing & licensing; pre-tag adds: account management, backup policy, billing dispute | ours=['blocker', 'churn', 'escalation'] / pre-tag=['action_item', 'concern', 'pricing_offer', 'technical_issue'] |
| `C42F2C03` Support Case #7570 - Silverline Brands Com | support (0.98) | ours add: compliance & comply product>compliance reporting, compliance & comply product>comply v2 launch, support cases>billing & licensing; pre-tag adds: billing discrepancy, compliance reporting, credit request | ours=['blocker', 'escalation'] / pre-tag=['action_item', 'concern', 'praise', 'technical_issue'] |
| `89DC89B6` Support Case #3266 - Trailhead Marketplace | support (0.98) | ours add: compliance & comply product>audit preparation, customer accounts & renewals>at-risk accounts, reliability & incidents>outage response; pre-tag adds: churn risk, detect pipeline failure, fraud monitoring | ours=['blocker', 'churn', 'escalation'] / pre-tag=['churn_signal', 'concern', 'technical_issue'] |
| `A6B62A59` Support Case #8749 - Coastal Living Co SAM | support (0.98) | ours add: customer accounts & renewals>at-risk accounts, product & engineering delivery>identity roadmap, support cases>escalations & communication gaps; pre-tag adds: authentication failure, customer reliability concerns, identity federation | ours=['blocker', 'churn', 'escalation'] / pre-tag=['action_item', 'churn_signal', 'concern', 'technical_issue'] |
| `3F99EE7D` Aegis / Axiom Labs - Multi-Year Renewal | external (0.95) | ours add: compliance & comply product>compliance reporting, customer accounts & renewals>renewal & contract, customer accounts & renewals>upsell & expansion; pre-tag adds: api rate limits, competitive displacement, compliance reporting | ours=['blocker', 'churn', 'escalation'] / pre-tag=['churn_signal', 'feature_gap', 'positive_pivot', 'praise'] |
| `583FB020` Aegis / Harborview Banking - Threat Detect | external (0.95) | ours add: compliance & comply product>audit preparation, compliance & comply product>framework coverage gaps, customer accounts & renewals>account roadmap reviews; pre-tag adds: alert routing, alert tuning, compliance | ours=['blocker', 'churn', 'escalation'] / pre-tag=['action_item', 'concern', 'technical_issue'] |
| `EE4B6251` Aegis / Nova Retail Group - Renewal Discus | external (0.95) | ours add: compliance & comply product>compliance reporting, compliance & comply product>comply v2 launch, customer accounts & renewals>at-risk accounts; pre-tag adds: churn risk, competitive evaluation, compliance reporting | ours=['blocker', 'churn', 'escalation'] / pre-tag=['churn_signal', 'feature_gap', 'positive_pivot'] |
| `D4580008` Aegis / Cobalt Software - Q2 Planning | external (0.95) | ours add: compliance & comply product>comply v2 launch, customer accounts & renewals>at-risk accounts, customer accounts & renewals>renewal & contract; pre-tag adds: cloud expansion, competitive threat, compliance | ours=['blocker', 'churn', 'escalation'] / pre-tag=['action_item', 'churn_signal', 'positive_pivot'] |

## Known limitations surfaced by the spot-check

1. **Action-item closure rate is 0% across owners.** Our fuzzy-match heuristic 
   requires 3 distinctive tokens from the action description to appear as a literal 
   substring in a later utterance. Real conversations paraphrase. The conservative 
   bias is deliberate (no false positives via the 'no citation, no claim' rule), but 
   the rate itself isn't meaningful — open-item *counts* per owner still are.
2. **Corpus-aggregate risk uses an `utt#-1` sentinel** for citations. PM-persona 
   queries about corpus-wide risk should drill into specific meetings, not just 
   carry an aggregate.
3. **Pre-tagged `topics` are flat strings** (`'performance degradation'`); ours are 
   2-level (`'Reliability & Incidents > Backup Performance'`). The disagreement 
   table reads as more divergent than it actually is — same content, finer structure.