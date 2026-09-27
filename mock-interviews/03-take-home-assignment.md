# Mock 03 · Take-home assignment: "Should we keep the coupons?"

A realistic analyst take-home: an ambiguous business question, messy-enough data, a time box, and a deliverable a
non-technical manager will read. Many loops end with a 20-minute presentation of your take-home, so the rubric covers
both the work and how you explain it.

---

## The brief (give this to the candidate)

> **From:** Priya Nair, Head of Growth, ShopKart
> **To:** Analytics
> **Subject:** Coupons: keep, change, or kill?
>
> We run three coupon codes: **WELCOME15** (first-order discount), **FEST10** (festive season) and **SAVE5**
> (always-on). Finance says coupons are "eating our margin". Marketing says they "drive loyalty and growth". I need a
> recommendation I can take to the leadership meeting.
>
> Please send me:
> 1. A **one-page summary** (recommendation first, then 3–4 supporting findings with numbers)
> 2. The **analysis** (notebook, SQL file, or Excel workbook) so someone can check your work
> 3. **2–4 charts** that make the case
>
> Use the ShopKart data (`data/shopkart.db` or `data/clean/*.csv`). Please don't spend more than **4 hours**; tell
> me what you'd do with more time.

**Rules for the candidate:** time-box to 4 hours (set a timer). Any tool is fine. Write down assumptions as you go.
You may use the definitions in the [SQL exercise conventions](../practice/sql/EXERCISES.md) (valid orders = Delivered
+ Shipped; revenue = quantity × unit_price − discount; gross profit = revenue − quantity × unit_cost).

---

## Suggested approach (read *after* your attempt, or if stuck for >30 min)

<details><summary>Questions a strong submission answers</summary>

1. **How big is the programme?** Share of orders and revenue with a coupon, and the total discount given away.
2. **What does it cost?** Gross margin on coupon vs non-coupon orders. Is the discount the only cost?
3. **Does it drive loyalty?** Do customers whose *first* order used a coupon come back more often than those who paid
   full price? (This is the core of Marketing's claim, and it's testable.)
4. **Which coupon?** WELCOME15 vs FEST10 vs SAVE5 behave differently. Treat them separately.
5. **Side effects?** Return rates, AOV, category mix.
6. **Causality caveat.** This is observational data: coupon users may differ from non-users. What experiment would
   settle it? (Randomly withhold WELCOME15 from a holdout group of new sign-ups for 8 weeks, then compare 90-day
   revenue per customer, not just conversion.)
</details>

<details><summary>Self-check numbers (compare after you finish)</summary>

Valid orders (Delivered + Shipped), all dates in the dataset:

| | Orders | Share | AOV (₹) | Revenue (₹) | Discount (₹) | Gross margin |
|---|---:|---:|---:|---:|---:|---:|
| No coupon | 6,566 | 64.8% | 3,118.9 | 20,478,631.0 | 0 | 39.3% |
| Coupon | 3,559 | 35.2% | 2,824.8 | 10,053,317.3 | 1,431,057.7 | 30.5% |
| **Total** | 10,125 | | | **30,531,948.3** (matches SQL Q9) | | |

- **Loyalty:** customers whose first valid order used a coupon repeat at **42.6%** vs **43.7%** for full-price first
  orders (2,837 vs 2,843 customers). *No evidence that coupons buy loyalty.*
- **Returns** (excluding cancellations): 10.1% with a coupon vs 9.6% without, not materially different.
- Coupon usage across all 11,885 orders: WELCOME15 2,823 · FEST10 714 · SAVE5 674 · none 7,674.

A defensible recommendation: *keep a smaller first-order incentive but test it against a holdout, and cut the
always-on SAVE5*, which gives margin away with no loyalty evidence. Different conclusions are fine if the
numbers support them.
</details>

---

## Grading rubric (reviewer: score each 1–4)

| Criterion | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| **Answers the question** | Describes data, no recommendation | Vague recommendation | Clear recommendation up front | Recommendation + sized impact (₹/yr) + what would change their mind |
| **Correctness** | Major errors (double-counted revenue, cancelled orders included) | Minor errors | Numbers reconcile to known totals | Also reconciles and documents checks |
| **Analytical depth** | One overall comparison | Splits by coupon code | Tests the loyalty claim with a cohort comparison | Addresses confounding, proposes an experiment design |
| **Communication** | Wall of text / code dump | Findings buried | One-page summary a manager can read in 2 min | Crisp headlines ("Coupons don't buy loyalty"), charts with takeaway titles |
| **Reproducibility** | Can't be rerun | Runs with effort | Runs top-to-bottom, assumptions listed | Clean structure, README, parameterised queries |

**Pass:** average ≥ 3 with *Correctness* ≥ 3. The most common failure is not a technical one: it's skipping the
recommendation, or burying it on page 3.

## The 20-minute debrief (interviewer questions)

1. "Walk me through your recommendation in 60 seconds."
2. "Marketing will push back: 'WELCOME15 is why people sign up at all.' How do you respond?" *(Fair: this data
   can't rule it out, because we don't observe sign-ups that never happen. That's exactly why the holdout test is
   the recommendation.)*
3. "What's the biggest weakness of your analysis?"
4. "If you had one more week, what would you do?"
5. "Which chart would you put on the first slide, and why?"

→ See the portfolio project's [presentation tips](../portfolio/shopkart-growth-analysis/README.md) and chapter 07's
STAR method for the storytelling side.
