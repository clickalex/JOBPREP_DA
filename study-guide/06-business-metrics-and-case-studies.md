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
