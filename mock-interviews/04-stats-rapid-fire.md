# Mock 04 · Stats & concepts rapid-fire (20 minutes)

**Interviewer:** ask the questions in any order, one at a time. The candidate gets **60–90 seconds** per answer. Mark
✓ (clear and correct), ~ (roughly right, or rambling), or ✗. The model answers are deliberately short: that's the
length a good spoken answer should be.

**Target:** ✓ on 14 or more of 20. Anything ✗ goes into your review list, linked to
[chapter 03](../study-guide/03-statistics.md) or [chapter 06](../study-guide/06-business-metrics-and-case-studies.md).

---

### Descriptive stats

<details><summary>1. When would you report the median instead of the mean?</summary>

When the distribution is skewed or has outliers, e.g. order values, salaries, session length. ShopKart's median
order is ₹2,297 while the mean (AOV) is higher, pulled up by a few big Electronics orders.
</details>

<details><summary>2. What's the difference between standard deviation and standard error?</summary>

Standard deviation measures the spread of individual data points. Standard error measures the uncertainty of an
*estimate* (like a mean), and equals SD / √n. It shrinks as the sample grows; SD doesn't.
</details>

<details><summary>3. Correlation is 0.8 between ice-cream sales and drownings. Explain.</summary>

A confounder: hot weather drives both. Correlation isn't causation; to claim causation you need an experiment or a
design that rules out confounders.
</details>

<details><summary>4. What is Simpson's paradox? Give a quick example.</summary>

A trend that appears in every subgroup reverses when the groups are combined, because the group sizes differ. E.g. a
new checkout wins on both App and Web, yet looks worse overall because it got more of the low-converting Web traffic.
Always check the segment mix.
</details>

### A/B testing

<details><summary>5. What is a p-value, in plain English?</summary>

If there were truly no difference, the p-value is the probability of seeing a result at least this extreme by chance.
It is **not** the probability that the null hypothesis is true.
</details>

<details><summary>6. Our test: control 10.35% vs variant 11.79% conversion, p = 0.0004. Ship it?</summary>

Statistically, yes: the 95% CI for the lift is +0.65 to +2.24 pp, which excludes 0. But first check the sample-ratio
mismatch (SRM p = 0.94, fine), guardrail metrics, and segments. The lift is concentrated in the App (11.3% → 14.6%);
Web and Desktop weren't significant. Ship, and keep monitoring. (These are the real numbers from `checkout_experiment`.)
</details>

<details><summary>7. What's statistical power, and what drives the sample size you need?</summary>

Power is the probability of detecting a real effect of a given size (typically 80%). The required sample size grows
with a smaller minimum detectable effect, lower baseline rate, higher confidence level and higher power. Detecting
10% → 11% at α = 0.05 and 80% power needs about **14,750 users per group**.
</details>

<details><summary>8. What's "peeking" and why is it a problem?</summary>

Checking results repeatedly and stopping as soon as p < 0.05. Each look is another chance for a false positive, so
the real error rate balloons well past 5%. Fix: pre-register the sample size and duration, or use sequential testing
methods.
</details>

<details><summary>9. What's a sample-ratio mismatch (SRM)?</summary>

When the observed split between variants differs from the design (e.g. 50/50 planned, 52/48 observed) by more than
chance allows. Check it with a chi-square test. SRM signals a bug in assignment or logging, and invalidates the
results until it's explained.
</details>

<details><summary>10. Name two guardrail metrics for a checkout test.</summary>

Order cancellation or return rate, average order value, page load time, customer-support tickets. You want the
primary metric to rise *without* hurting these.
</details>

<details><summary>11. Why run a test for at least one full week even if you hit the sample size on day 3?</summary>

Day-of-week effects: weekend shoppers behave differently. Also novelty effects, since new designs get a
temporary curiosity bump.
</details>

<details><summary>12. When would you use a t-test vs a chi-square / z-test for proportions?</summary>

Use a z-test or chi-square for **rates** (converted yes/no), and a t-test (Welch) for **means** of continuous metrics
like revenue per visitor. For heavily skewed revenue, also consider a bootstrap or Mann-Whitney test.
</details>

### Metrics & business sense

<details><summary>13. Define conversion rate. What's the tricky part?</summary>

Conversions ÷ opportunities. The tricky part is the denominator: sessions, users or visitors? And what's the
attribution window? Always state the definition.
</details>

<details><summary>14. Retention vs churn vs repeat rate: what's the difference?</summary>

Retention: % of a cohort still active after N periods. Churn: % who stopped (often 1 − retention). Repeat rate: % of
customers with 2+ orders (ShopKart: 47.2% of buyers). Retention is time-bound; repeat rate isn't.
</details>

<details><summary>15. Revenue is up 20% but profit is flat. What could explain it?</summary>

A mix shift toward low-margin products (ShopKart: Electronics is 35% of revenue but 19% of profit), heavier
discounting or coupons, higher returns, rising shipping/COGS costs, or paid acquisition spend.
</details>

<details><summary>16. What is a cohort analysis and why use it?</summary>

Group users by a shared start event (e.g. sign-up month) and track their behaviour over time. It separates "are new
customers worse?" from "is everyone churning?", which aggregate curves hide.
</details>

<details><summary>17. How would you estimate the revenue impact of fixing mobile web checkout?</summary>

Sessions × (target conversion − current conversion) × AOV × 12 months, with a conservative target. E.g. close part
of the gap between Mobile Web (4.9%) and App (14.0%) purchase rates, not all of it. State the assumptions and give a
range.
</details>

### Data quality & judgement

<details><summary>18. You find 3% of orders have a NULL price. What do you do?</summary>

Investigate first: are they concentrated in one product or date (a bug) or random? Then choose: exclude, impute
(e.g. with the product's median price), or fix at the source. Document the decision and quantify its impact on the
headline numbers (the portfolio project's imputation moved revenue by just ₹445).
</details>

<details><summary>19. Two dashboards show different revenue for the same month. How do you debug?</summary>

Compare definitions (which statuses? gross or net of discounts/returns? order date or ship date? timezone?), then the
filters, then the joins (a one-to-many join double-counting). Reconcile step by step down to row level.
</details>

<details><summary>20. A stakeholder asks for "all the data" in Excel. What do you do?</summary>

Ask what decision they're trying to make. Usually a focused summary or a filtered extract answers it better. If they
do need the raw data, provide it with a data dictionary and flag any caveats.
</details>
