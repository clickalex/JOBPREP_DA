# Mock 07 · Data analyst interview Q&A (35–45 minutes)

A practice set for the **recruiter, hiring-manager, project-discussion and verbal technical** parts of an entry-level data analyst loop. It complements the live SQL, case and stats mocks; it is not a coding test.

**How to use it:** Have a partner ask the questions in order, or record yourself. Aim for **45–90 seconds per answer** (up to 2 minutes for the project walkthrough). Answer first, then open the model answer. The examples are prompts, not scripts: replace them with your real experience and never present a practice project as paid work.

**Target:** Give a specific, structured answer to at least 22 of 30 questions. Score each answer ✓ (clear, specific, credible), ~ (partly answered or too long), or ✗ (unsupported, vague, or no answer to the question). For technical answers, also check correctness, assumptions and validation. Rehearse the ✗ answers again in your own words.

### A useful practice loop

1. **First pass:** answer without looking at the model answer. A partner should ask one follow-up, such as “How did you verify that?” or “What would you do next?”
2. **Score it:** use the quick rubric below; write one specific piece of evidence from your answer, not just a number.
3. **Second pass:** review the model answer, note one improvement, then answer again in your own words. Don't memorize the sample wording.

| Dimension | 0 · Missing | 1 · Partial | 2 · Strong |
|---|---|---|---|
| **Directness** | Didn't answer the question | Answered indirectly or rambled | Clear answer up front, appropriate length |
| **Evidence** | Unsupported claim or unclear ownership | Some example, but your contribution or outcome is vague | Specific, truthful example; clear individual contribution and result |
| **Reasoning & checks** | Guess or unsupported conclusion | Some method, but assumptions or checks are missing | Sound method; names relevant assumptions, edge cases or validation |
| **Relevance** | No connection to role or decision | Some relevance, limited implication | Connects the answer to the business decision or role |

Score each dimension 0–2 (maximum 8). **6–8:** ready to practise under pressure; **4–5:** tighten the evidence or checks; **0–3:** rebuild the answer. For experience questions, a clearly labelled portfolio or study example is valid; don't invent employment results.

---

## Introduction and motivation

<details><summary>1. Tell me about yourself.</summary>

Use **present → relevant past → why this role**. Keep it to about a minute: “I’m building my data-analysis skills in SQL, Python and Power BI. In a portfolio project, I analysed a fictional e-commerce dataset, checked the data quality, and translated the findings into recommendations. My background in [real study/work experience] taught me [relevant skill]. I’m interested in this role because [specific product, team or problem].” Swap every bracket for a true detail; don't recite your whole CV.
</details>

<details><summary>2. Why do you want to be a data analyst?</summary>

Connect curiosity to decisions: “I enjoy turning an unclear question into evidence someone can act on. In [a real example], I [what you did] and learned [what changed]. I’ve since practised [relevant tools/project], and I want to build that skill on real business problems.” Avoid relying on “I like numbers” alone.
</details>

<details><summary>3. Why this company and this role?</summary>

Show that you researched the company: name its product or customer, a plausible business question, and how the role fits your skills. For example: “I saw that [specific product/channel] is important to your business. I’d be interested in how the team measures [relevant funnel/retention/operations outcome]. This role’s mix of [actual job requirements] matches the work I’ve practised in [true example].” Don't claim inside knowledge or invent recent company news.
</details>

<details><summary>4. What are you looking for in your first analyst role?</summary>

“I’m looking for a role where I can own well-scoped analysis end to end: clarify the decision, prepare reliable data, communicate the result, and learn from feedback. I’d also like to build depth in [one or two skills relevant to this job].” Keep it focused on the work and contribution, not only training or promotion.
</details>

## Project discussion

<details><summary>5. Walk me through a project you’re proud of.</summary>

Use **question → data → method → finding → action → limitation**. Keep the setup short, be precise about what *you* did, and finish with a result or recommendation. For the ShopKart portfolio, say it is a synthetic dataset: one example is finding that the checkout-test improvement was concentrated in the App, so you would recommend a guarded rollout there and a separate investigation of the Web experience. Don't imply the recommendation was deployed in a real company.
</details>

<details><summary>6. How did you know the data was reliable enough to analyse?</summary>

“I checked the grain and key fields, duplicates, missing values, valid ranges and date coverage. I reconciled row counts and important totals before and after cleaning, then documented exclusions and assumptions. I’d still label any remaining limitations rather than calling the data perfect.” Give one concrete check from your project.
</details>

<details><summary>7. What was the most surprising finding in your project?</summary>

State the finding, why you didn't expect it, and how you validated it. Example: “The overall checkout result hid a device difference. I checked the segment counts and conversion definitions before recommending an App-focused follow-up. Because it is a subgroup result, I’d treat it cautiously and verify it in a planned test.” Use a genuine finding and do not overstate causality.
</details>

<details><summary>8. What would you do differently if you had another week?</summary>

Name a specific improvement and its value: validate the result on a new period, improve the metric definition, add a stakeholder review, test a recommendation, or automate a repeated step. Explain what risk it addresses. Avoid saying “nothing” or adding complexity without a purpose.
</details>

<details><summary>9. Tell me about a project limitation or assumption.</summary>

Be direct: identify the assumption, describe how it could bias the result, and say what data or test would reduce the uncertainty. For a synthetic portfolio, say explicitly that the data and business outcome are fictional; the project demonstrates a workflow, not a real-world impact claim.
</details>

## Working with data and stakeholders

<details><summary>10. A stakeholder says your number is wrong. What do you do?</summary>

Assume good intent. Ask which number and decision they mean, then compare definitions, date ranges, filters, status handling and join grain. Reconcile against a trusted source at row level if needed. Share what changed and document the agreed definition so the mismatch is less likely to recur.
</details>

<details><summary>11. How would you explain a technical result to a non-technical audience?</summary>

Lead with the decision and impact, then give the evidence and caveat in plain language. For example: “The new checkout increased App conversion in this test; the overall gain came mainly from App users. I recommend a guarded App rollout while we investigate Web. This result does not establish that the change will improve every device segment.” Invite questions and keep technical detail available, not in the headline.
</details>

<details><summary>12. You get a vague request for a dashboard by tomorrow. What do you do?</summary>

Ask what decision it supports, who will use it, which metric and timeframe matter, and what action follows. Agree on a small version-one scope and delivery time; share a sketch or sample early. Don't silently build a large dashboard from assumptions.
</details>

<details><summary>13. Two managers both say their requests are urgent. How do you prioritize?</summary>

Clarify each request’s decision, real deadline, impact and effort. Tell both stakeholders what you can deliver and when, and ask your manager to resolve the trade-off if priorities conflict. Offer a quick, clearly labelled partial answer when it unblocks a decision; don't promise two full deliverables at once.
</details>

<details><summary>14. What do you do when a dataset has missing or inconsistent values?</summary>

Profile where and how often the issue occurs, check whether it is concentrated by time, source or segment, and ask how the field is generated. Choose a treatment based on the analysis—fix at source, exclude, impute, or retain as unknown—then quantify the impact and document it. Don't automatically replace missing values with zero.
</details>

<details><summary>15. How do you make sure your analysis is accurate?</summary>

Use checks at several levels: validate inputs and definitions, inspect joins and row counts, test edge cases and NULLs, reconcile key totals to a trusted source, and have someone review critical logic. After delivery, monitor whether the metric behaves as expected. Name the checks you actually used rather than claiming analysis is error-free.
</details>

## Behaviour, growth and logistics

<details><summary>16. Tell me about a mistake you made.</summary>

Choose a real, bounded mistake. Explain the impact, how you surfaced it, the correction, and the safeguard you added. A strong answer takes ownership (“I double-counted a one-to-many join”), not blame, and does not pretend the mistake was secretly a success.
</details>

<details><summary>17. Tell me about difficult feedback you received.</summary>

Describe the feedback without arguing, the specific change you made, and what happened next. If you disagree with feedback, explain how you asked clarifying questions and tested the advice respectfully. Use an actual example from work, study or a project.
</details>

<details><summary>18. What is one skill you are currently improving?</summary>

Pick a real skill relevant to the job, explain what you're doing to improve it, and give a way you measure progress. Example structure: “I used to [specific gap]. I now [practice or feedback loop], and I can see progress when [observable result].” Avoid disguised strengths such as “I work too hard.”
</details>

<details><summary>19. What are your notice period, location and compensation expectations?</summary>

Answer logistics accurately and calmly. State your actual notice period and location constraints. For compensation, research the role, city and level; if asked first, give a realistic range based on that research and say you’re open to discussing the full package. If you need the employer’s range to calibrate, ask politely. Never invent a competing offer or current salary.
</details>

<details><summary>20. What questions do you have for us?</summary>

Ask two or three questions that help you understand the work: “What would a strong first 90 days look like?” “How does this team agree on metric definitions?” “Can you share an example of an analysis that changed a decision?” “What are the main stakeholders and data tools for this role?” Avoid questions answered clearly on the job page.
</details>

---

## Verbal technical and analytical questions

For each technical answer, try this order: **define the grain/metric → explain the method → name an edge case → say how you would validate → connect it to the decision.** Interviewers value clear reasoning and checks as much as terminology.

<details><summary>21. A join made your revenue total much larger. What might have happened?</summary>

Check the grain on both sides. Joining orders to multiple order-item rows repeats each order-level amount once per item: a one-to-many **fan-out**. Aggregate the item table to one row per order before joining, or compute order-level and item-level metrics separately. `COUNT(DISTINCT order_id)` can repair a count, but it does not generally repair an inflated `SUM`. Compare row counts and totals before and after the join. See the [SQL joins guide](../study-guide/01-sql.md).
</details>

<details><summary>22. Explain WHERE vs HAVING. How would you return the top three products in each category?</summary>

`WHERE` filters input rows before aggregation; `HAVING` filters grouped results after aggregation. For top three, first aggregate sales at product/category grain, then rank with `ROW_NUMBER()` or `DENSE_RANK() OVER (PARTITION BY category ORDER BY sales DESC)` and filter the rank in an outer query/CTE. Clarify whether ties should make more than three rows appear. See the [SQL guide](../study-guide/01-sql.md).
</details>

<details><summary>23. A source has blank values for customer age. Would you replace them with zero?</summary>

Not by default: zero is a real value and would distort averages and age bands. First determine whether blank means unknown, not collected, or not applicable; measure its rate and pattern by source or segment. Keep an explicit missing/unknown category or use a justified imputation only if the analysis calls for it, and report how the choice affects the result. See the [data-cleaning guide](../study-guide/04-python-pandas.md).
</details>

<details><summary>24. Conversion increased, but revenue per visitor fell. What would you investigate?</summary>

Confirm both metrics use the same population, attribution window and experiment assignment. Then decompose revenue per visitor into conversion × revenue per conversion, and inspect order value, discount, product mix, refunds and cancellations. Check pre-agreed guardrails and uncertainty before recommending a rollout. Don't choose whichever metric looks better; clarify the business objective. See the [metrics guide](../study-guide/06-business-metrics-and-case-studies.md).
</details>

<details><summary>25. A manager asks for a dashboard. How do you decide what to put on it?</summary>

Start with the audience and decisions: what action will they take, how often, and at what level of detail? Agree on a small set of defined KPIs, useful comparisons and filters; show context and trends, not just isolated totals. Prototype with users, check accessibility/readability, and validate displayed values against a trusted source. Don't start with chart types before understanding the use case. See the [BI guide](../study-guide/05-bi-powerbi-tableau.md).
</details>

<details><summary>26. What makes a metric definition trustworthy?</summary>

It specifies the numerator, denominator, grain, eligible population, time window, exclusions and source. For example, “monthly active customers” needs an agreed activity event, timezone, identity rule and calendar definition. Check that the implementation matches the written definition, test edge cases, and publish ownership/version changes so different dashboards don't silently redefine it.
</details>

<details><summary>27. In pandas, a merge unexpectedly doubled your rows. How do you debug it?</summary>

Inspect key uniqueness and the intended relationship on each side. A duplicate join key may make a many-to-many merge; check `duplicated` counts and row counts before/after. Use `merge(..., validate="one_to_one")` or the appropriate one-to-many validation when the data contract allows it, then resolve duplicates based on a documented rule instead of dropping them blindly. See the [pandas guide](../study-guide/04-python-pandas.md).
</details>

<details><summary>28. Two dashboards report different monthly revenue. What's your first debugging sequence?</summary>

Compare metric definitions, date field/timezone, order statuses, discounts/returns and filters. Then verify table grain and joins for fan-out, and trace one small set of orders through both calculations. Reconcile intermediate totals, agree on the source of truth, and document the resolution. Don't average the two answers or assume one chart is right because it looks familiar.
</details>

<details><summary>29. A SQL query is slow. What would you try before rewriting everything?</summary>

Use the query plan and table sizes to find the costly scan/join. Select only needed columns, filter early with predicates that can use indexes, check join keys and data types, and aggregate before joining when the grain permits. Measure changes on representative data and confirm the result is unchanged. Avoid claiming an index always helps: writes and storage have costs too. See the [SQL performance section](../study-guide/01-sql.md).
</details>

<details><summary>30. An A/B test is statistically significant. Is that enough to ship?</summary>

No. Check randomization and sample-ratio mismatch, the pre-specified primary metric, confidence interval/effect size, guardrails, duration and data quality. Ask whether the effect is practically valuable and whether the test was powered for the decision. Segment findings should be treated cautiously unless planned and adequately powered. Recommend a rollout or follow-up based on risk and evidence. See the [statistics guide](../study-guide/03-statistics.md).
</details>

---

## Before the interview: tailoring worksheet

Use this once for each role. It helps you tailor answers without pretending to have experience or company knowledge you don't have.

### Role and evidence

| Job requirement (quote or paraphrase) | My truthful evidence | What I still need to learn |
|---|---|---|
| 1. | | |
| 2. | | |
| 3. | | |

### Company and role research

```text
Company / product / customer:
One business outcome this team likely cares about:
Evidence for that assumption (job post, public product info, etc.):
Why this role fits my real interests and skills:
Two questions I want to ask the interviewer:
```

Treat business outcomes as informed hypotheses, not facts, unless the company has published them. Avoid inventing internal tools, metrics, or recent events.

### Build a reusable STAR story bank

Prepare six short examples you can adapt. An example may come from employment, volunteering, coursework or a clearly labelled portfolio project. Keep your personal contribution distinct from the team's work.

| Story theme | Situation / task (one line) | My actions (specific) | Result / evidence | Learning or follow-up |
|---|---|---|---|---|
| Insight that changed a decision | | | | |
| Messy data or quality issue | | | | |
| Tight deadline / prioritisation | | | | |
| Explaining analysis to someone | | | | |
| Mistake or difficult feedback | | | | |
| Disagreement / collaboration | | | | |

**Claim check before you rehearse:** Can I explain where each number came from? Did I personally do the action I'm describing? Is the result observed, estimated, or hypothetical? Have I labelled portfolio data as synthetic where relevant? If the answer to any is unclear, qualify the claim or leave it out.

---

## Debrief

```text
Date / role:
Answers I explained clearly:
Answers that were too vague or long:
One real example I should prepare:
One claim I need to make more precise:
Next practice date:
```

### Session scorecard

| Question group | Score (0–8) | Evidence to keep | One change for next time |
|---|---:|---|---|
| Introduction & motivation · Q1–4 | | | |
| Project discussion · Q5–9 | | | |
| Stakeholders & analysis · Q10–15 | | | |
| Behaviour & logistics · Q16–20 | | | |
| Verbal technical · Q21–30 | | | |

Choose **one** answer to repeat before your next mock. A useful debrief is: one thing to keep, one thing to change, and one follow-up question you want to handle better.

For hands-on technical follow-up, use the [live SQL rounds](README.md), [case round](02-case-round.md), and [stats rapid-fire](04-stats-rapid-fire.md). For STAR story planning and resume guidance, see the [behavioral interview chapter](../study-guide/07-behavioral-and-job-search.md).
