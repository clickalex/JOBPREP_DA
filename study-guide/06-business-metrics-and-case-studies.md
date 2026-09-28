# 06 · Business metrics, product sense & case studies

Technical skills get you shortlisted; **business thinking gets you hired.** Case rounds test whether you can take a vague
question, structure it, pick the right metrics, form hypotheses and recommend an action. There's rarely one "right"
answer. The interviewer is scoring your *structure and judgement*.

---

## 1. Metrics every DA should be able to define

### E-commerce / retail
| Metric | Formula | Watch out for |
|---|---|---|
| GMV | Σ order value (before cancellations/returns) | Not revenue! |
| Net revenue | GMV − cancellations − returns − discounts (± shipping, taxes: define it!) | |
| AOV | revenue ÷ orders | Rises when order count drops |
| Conversion rate | orders (or buyers) ÷ sessions (or visitors) | Know the denominator |
| Cart abandonment | 1 − purchases ÷ carts created | |
| Repeat purchase rate | customers with 2+ orders ÷ buyers | Depends on the time window |
| Retention / churn | active in period N ÷ cohort size | Define "active" |
| CAC | marketing spend ÷ new customers acquired | By channel |
| LTV / CLV | avg order value × purchase frequency × lifespan (× margin) | Use gross margin, not revenue |
| LTV : CAC | target ≥ 3 : 1 is a common rule of thumb | Payback period matters too |
| Gross margin % | (revenue − COGS) ÷ revenue | |
| Return rate / RTO | returned ÷ delivered; RTO = return-to-origin (failed delivery, huge for COD in India) | |

### Subscription / SaaS / apps
MRR/ARR · churn (logo vs revenue) · net revenue retention (NRR) · DAU / MAU (stickiness) · activation rate ·
ARPU · session length · feature adoption · NPS / CSAT

### Operations / fintech / others
On-time delivery %, SLA breach %, average handling time, first-contact resolution, fill rate, inventory turnover,
default rate / NPA (lending), approval rate, fraud rate, TAT (turnaround time)

## 2. Frameworks (use them lightly: structure, not jargon)

* **AARRR (pirate metrics)**: Acquisition → Activation → Retention → Referral → Revenue. Good for "which metrics would you track for X?"
* **North Star metric + inputs**: one metric capturing the value delivered to customers (e.g. *weekly orders delivered on time*), broken into input metrics teams can move.
* **Metric tree**: Revenue = Traffic × Conversion × AOV. Each factor splits further (traffic by channel; AOV = items per order × price per item). This is how you diagnose any change.
* **Counter-metrics / guardrails**: every metric you push has one you must protect (conversion ↔ returns; speed ↔ accuracy).

## 3. The "metric dropped" case, a repeatable approach

> *"Orders fell 12% last week. Investigate."*

1. **Clarify & validate.** How is it measured? Compared to what (WoW, YoY, forecast)? Is the data right? Tracking bug, pipeline delay, definition change, a dashboard filter?
2. **Seasonality / external.** Last year's same week? Festival shift (Diwali moves every year!), a holiday, IPL final, a competitor's sale, a payment-gateway (UPI) outage, weather.
3. **Decompose** with the metric tree: traffic × conversion × AOV. Which factor moved?
4. **Segment** the moving factor: platform (App/Web, Android/iOS, app version), region/city, channel, new vs returning, category, payment method. Is it everywhere (a systemic cause) or concentrated (a local cause)?
5. **Internal changes.** Releases, pricing, promotions ending, marketing budget cuts, stock-outs, delivery issues.
6. **Hypothesise → test** with data, then **size** the impact and **recommend** a fix and a monitor.

*ShopKart example:* SQL Q34 finds Maharashtra's June 2025 cancellations at 30.6% (vs ~5% normally). That's concentrated
in one region, points to a courier issue, and suggests the fix: a state-level anomaly alert.

## 4. Other common case types

**"Which metrics would you track for feature X?"** Goal of the feature → primary success metric → supporting metrics →
guardrails → how you'd measure them (experiment? pre/post?).
*E.g. a "Buy Now, Pay Later" option at checkout:* conversion at checkout (primary), AOV, BNPL adoption %, default rate / payment failures and
refunds (guardrails), cannibalisation of UPI/card.

**"Should we launch X?"** (e.g. *charge ₹25 for COD*). Upside (fewer cancellations and RTO costs, a shift to prepaid) vs downside
(lost orders from COD-dependent users, especially tier-2/3 cities) → propose an A/B test by region, with conversion
and net contribution margin as metrics.

**Guesstimates / market sizing.** Structure beats precision. State your assumptions and sanity-check at the end.
> *How many food-delivery orders happen in Delhi NCR per day?*
> NCR population ~33 M → smartphone users with online-food habits ~30% → ~10 M → ordering frequency ~1.5×/month
> → 15 M orders/month → **~0.5 M orders/day**. Sanity check: reported national volumes are in the few-million-per-day range, and NCR is one of the largest markets, so this is plausible.

**Root cause with limited data / take-home.** Keep the report short: question → key findings (3–5, with numbers) →
recommendation + impact → caveats → appendix. The [portfolio README](../portfolio/shopkart-growth-analysis/README.md) follows this structure.

## 5. Communicating insights

* **Lead with the answer** (pyramid principle): "Orders fell 12% because Android app v5.2 broke the UPI flow. Rolling back recovers ~₹8 L/week."
* **So what → now what.** Each finding needs an implication and an action.
* **Quantify** (₹, %, customers affected), and give **confidence** ("high: consistent across all cities").
* **Know your audience.** Executives get 3 bullets and a chart; analysts get the method and caveats.

## 6. Practice prompts (use the ShopKart data)

1. Revenue per customer is highest for Referral. Should we move all Paid Social budget to referrals? What else would you need to know?
2. Fashion has a 16% return rate. Design an analysis to find the root cause, and list the data you'd request.
3. The CEO wants one number on a daily dashboard. What is it and why?
4. The new checkout lifted App conversion only. Give three hypotheses for why web didn't improve, and how to test each.
5. Diwali 2026 falls in early November. What would you change in the October vs November YoY comparisons?
6. Estimate the number of UPI transactions made in India in a day, then find the real number and compare.

## 7. Interview questions

<details><summary><b>What's the difference between a metric, a KPI and a north-star metric?</b></summary>A metric is anything you measure. A KPI is a metric tied to a goal someone owns (e.g. return rate &lt; 8%). A north-star metric is the single number that best captures the value customers get and predicts long-term success (e.g. weekly repeat orders), supported by input metrics and guardrails.</details>
<details><summary><b>How do you calculate AOV, and why can it mislead?</b></summary>AOV = revenue ÷ number of orders (state which orders count: usually excluding cancelled). It's an average, so a handful of large orders or a category mix shift moves it without anything changing for the typical customer. Pair it with the median order value and orders per customer.</details>
<details><summary><b>What is customer lifetime value (LTV) and a simple way to estimate it?</b></summary>The total gross profit a customer generates over their relationship. Simple version: average order value × gross margin × orders per year × expected customer lifetime in years. Compare it with CAC: LTV/CAC above ~3 is a common health rule of thumb.</details>
<details><summary><b>Define CAC and payback period.</b></summary>CAC = marketing and sales spend ÷ new customers acquired, per channel and period. Payback period = CAC ÷ monthly gross profit per customer, i.e. months until the customer has "paid back" what it cost to acquire them.</details>
<details><summary><b>What's a metric tree and why is it useful?</b></summary>A breakdown of a top-line metric into its drivers, e.g. revenue = visitors × conversion rate × AOV, and each of those into segments. When the top line moves, you walk down the tree to find which branch moved, instead of guessing.</details>
<details><summary><b>Orders dropped 10% week over week. What are your first three questions?</b></summary>1) Is it real? Check data freshness, tracking changes, definitions, and whether a 10% move is normal for this metric (at ~100 orders/week it often is). 2) Is it everywhere or concentrated? Split by device, channel, region, payment method, new vs returning. 3) What changed? Releases, pricing, stock, marketing calendar, holidays, competitors. See <a href="../mock-interviews/02-case-round.md">mock case round 02</a>.</details>
<details><summary><b>Revenue is up 20% but profit is flat. Explain.</b></summary>Candidates: a mix shift toward low-margin categories (ShopKart: Electronics is 35% of revenue but 19% of profit), heavier discounts or coupons, more returns, higher shipping/COGS, or paid-acquisition spend growing faster than revenue. Decompose profit by category and cost line to find which.</details>
<details><summary><b>What are guardrail metrics?</b></summary>Metrics that must not get worse while you optimise the primary one, e.g. return rate, cancellation rate, page load time or support tickets during a checkout test. A "win" that breaks a guardrail isn't a win.</details>
