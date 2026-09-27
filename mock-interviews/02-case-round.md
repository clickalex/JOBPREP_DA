# Mock 02 · Case round: "Orders dropped 13% last week" (40 minutes)

The metric-investigation case is the most common non-SQL round for analysts. This one has a twist most practice cases
don't: **the data is real (well, synthetic but consistent)**, so after the conversation the candidate can run the
queries and see whether their hypotheses hold.

**Interviewer:** read the prompts in order. Reveal the data in each "📊 Reveal" block only when the candidate asks for
that cut (or something close to it). Don't volunteer it.

---

## Part A · The alarm (≈20 min)

> **Prompt:** "It's Monday, 21 July 2025. The CEO forwards you the weekly dashboard: valid orders fell from **125** in
> the week of 7 July to **108** in the week of 14 July, **down 13.6% week over week**. She asks: 'What happened? Do we
> need to do something?' Walk me through how you'd approach this."

### What a strong answer sounds like (for the interviewer)

1. **Clarify before diagnosing.** How is the metric defined (valid = Delivered + Shipped; by order date)? Is the week
   complete? Any tracking or pipeline changes? *Is 13.6% actually unusual for this metric?*
2. **Check whether it's real, then check whether it's big.** Compare against normal week-to-week variation, the same
   week last year, and the 4-week average, not just last week.
3. **Decompose.** Orders = sessions × conversion. Segment by device, payment method, channel and region to see if the
   drop is concentrated or broad.
4. **Internal vs external.** Releases, outages, price changes, stock-outs, marketing calendar vs holidays, competitors,
   weather.
5. **Conclude and recommend**, including "no action, keep monitoring" when that's what the data says.

### 📊 Reveals

<details><summary>Reveal 1: "How much does this metric normally move?"</summary>

Weekly valid orders, Jan–Sep 2025: **mean 111, standard deviation 16.5**. Week-over-week changes have a standard
deviation of **13.6 percentage points**, and **13 of 37 weeks** moved by 12% or more in one direction.

(Sanity check a candidate can do mentally: at ~110 events per week, Poisson noise alone is about √110 ≈ 10.5 orders,
≈ 9.5% of the mean. A 17-order swing is less than 2σ.)
</details>

<details><summary>Reveal 2: "Break it down by device / payment / channel / state"</summary>

Week of 14 Jul vs the average of the 4 prior weeks (valid orders):

| Cut | Biggest movers |
|---|---|
| Device | Mobile App 56.8 → 48 (−15%), Desktop 25.2 → 23 (−9%), Mobile Web 36.8 → 37 (+1%) |
| Payment | UPI 58.5 → 51 (−13%), Credit Card 20.0 → 17, COD 20.0 → 22 (+10%) |
| Channel | Organic 35.5 → 31, Paid Social 17.0 → 12, Email 13.2 → 16 (+21%), Paid Search 21.0 → 23 (+10%) |
| State | Telangana 12.0 → 7, Delhi 15.2 → 12, Karnataka 13.8 → 17 (+23%), Maharashtra 21.0 → 23 (+10%) |

No segment explains the drop: some are down, some up, all by single-digit order counts.
</details>

<details><summary>Reveal 3: "What did traffic and conversion do?"</summary>

Web sessions: 1,542 (w/c 7 Jul) → 1,486 (w/c 14 Jul), −3.6%. Session conversion was 10.7% → 11.4%, *higher*. No
outage, release or price change was logged that week.
</details>

<details><summary>Model conclusion</summary>

"A 13.6% drop sounds alarming, but at ~110 orders a week this metric swings ±14% routinely. That's about one standard
deviation of normal weekly movement, the drop isn't concentrated in any segment, and traffic and conversion
are stable. I'd **not** take action. I'd reply to the CEO with that context, and propose we change the dashboard to
show a 4-week rolling average with a control band, so we stop reacting to noise. If next week is also low, a
two-week decline is much less likely by chance, and I'd dig deeper then."

**Why this is the "hire" answer:** it shows statistical judgement, not just a checklist. Candidates who immediately
invent a cause ("probably the app release") score low on framing and verification.
</details>

## Part B · The real incident (≈15 min)

> **Prompt:** "Good. Now a different alert: in June 2025 the overall **cancellation rate** rose to **8.9%**, from 5.7%
> in January–May. Same question: what's going on?"

<details><summary>Reveal 4: "Cancellation rate by state (June 2025)"</summary>

| State | June orders | Cancellation rate |
|---|---:|---:|
| **Maharashtra** | 111 | **30.6%** (Jan–May: 5.1%) |
| Delhi | 83 | 6.0% |
| Karnataka | 62 | 3.2% |
| Uttar Pradesh | 59 | 1.7% |
| Telangana | 56 | 5.4% |
| West Bengal | 40 | 2.5% |

Excluding Maharashtra, June cancellations were **3.8%**, i.e. normal.
</details>

<details><summary>Reveal 5: "Within Maharashtra, by payment method"</summary>

COD 48.0% (25 orders), Debit Card 37.5% (8), UPI 26.2% (61), Credit Card 21.4% (14), Net Banking 0% (3).
Elevated across **all** payment methods, so it's not a payment-gateway issue. That points to fulfilment: courier,
warehouse or delivery-time promises in one region.
</details>

<details><summary>Model conclusion</summary>

"The company-wide spike is entirely one state: Maharashtra's cancellations went from 5% to 31% in June while
everywhere else stayed under 6%. It hits every payment method, which rules out a payment problem and points to
logistics in that region, e.g. a courier partner failing or a warehouse issue pushing delivery estimates out. Next
steps: check delivery-promise dates and courier assignment for Maharashtra orders, talk to ops, and add a
state-level cancellation alert. Unlike Part A, this is a real signal: 34 of 111 cancelled against about 6 expected
is far outside noise."

This is the same incident found in the [portfolio project](../portfolio/shopkart-growth-analysis/README.md) and in
SQL exercise Q34.
</details>

## Part C · Follow-up questions (≈5 min, pick two)

1. "How would you set up alerting so we catch Part B faster but don't page anyone for Part A?" *(Segment-level
   metrics, thresholds relative to each segment's own variance, minimum volume, e.g. alert when a state's 7-day
   cancellation rate is above its baseline + 3σ with ≥ 30 orders.)*
2. "The CEO still wants a single number for 'is the business healthy'. What would you pick?" *(A north-star metric,
   e.g. weekly revenue from repeat customers or contribution margin, with 2–3 guardrails: return rate, cancellation
   rate, NPS.)*
3. "How would you communicate Part A to the CEO in two sentences?"

---

### Now verify it yourself

Every reveal above can be reproduced with SQL on `data/shopkart.db`. As homework, write the queries for Reveals 1, 2
and 4, e.g. weekly valid orders:

```sql
SELECT date(order_ts, 'weekday 0', '-6 days') AS week_start,   -- Monday of each week
       SUM(status IN ('Delivered','Shipped')) AS valid_orders
FROM orders
WHERE order_ts >= '2025-01-06' AND order_ts < '2025-09-29'
GROUP BY week_start ORDER BY week_start;
```
