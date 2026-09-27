# 07 · Behavioral interviews, resume & job search

## 1. The typical entry-level DA hiring process

1. **Resume screen** (ATS + recruiter, ~30 seconds) → 2. **Online assessment** (SQL / Excel / aptitude, 45–90 min) →
3. **Technical round** (live SQL + Python/Excel questions, possibly a case) → 4. **Case / take-home** (dataset → short
report or dashboard, 2–5 days) → 5. **Hiring manager round** (projects, business sense, behavioral) → 6. **HR / culture fit** (salary, notice period, relocation).

Service companies and GCCs (global capability centres) often run high-volume tests; product startups lean on take-homes and case rounds.

## 2. "Tell me about yourself" (60–90 seconds)

**Present → past → why this role.** Keep it tight and relevant.

> "I'm an aspiring data analyst. For the past few months I've been building hands-on skills in SQL, Python and Power
> BI. My most recent project analysed two years of e-commerce data: I cleaned 40,000 messy records, found that Fashion
> drove nearly half of gross profit despite high returns, and analysed an A/B test that pointed to a ₹14 lakh
> opportunity. Before that I [studied commerce / worked in operations at X], where I [built Excel MIS reports / handled
> customer data], and that's what got me interested in analytics. I'm excited about this role because [specific reason
> tied to the company's product/data]."

**Career switchers:** make your past an asset (domain knowledge!). Ops → "I know where operational data breaks";
sales → "I understand the funnel metrics"; finance → "I've reconciled numbers under deadlines."

## 3. STAR stories: prepare 6, reuse them everywhere

**S**ituation (1–2 lines) → **T**ask (your responsibility) → **A**ction (*you*, specific, ~60% of the answer) →
**R**esult (a number + what you learned).

| Theme | Questions it answers | Your story (fill in) |
|---|---|---|
| Insight that changed a decision | "Tell me about an impactful analysis" | |
| Messy / missing data | "How do you handle bad data?" | |
| Tight deadline | "Working under pressure", "prioritisation" | |
| Explaining to a non-technical audience | "Communication", "stakeholder management" | |
| A mistake you made | "Failure", "weakness" | |
| Disagreement / pushback | "Conflict", "influencing without authority" | |
| Learning something fast | "Learning agility", "new tool" | |

**Example (mistake):**
S: while building a sales dashboard, my revenue total didn't match finance's number. · T: find the gap before the
Monday review. · A: I reconciled step by step and found my join to order lines was double-counting shipping fees.
I fixed it with an order-level aggregation, added a row-count check to my workflow and documented the metric definition
with finance. · R: the numbers matched to the rupee; the reconciliation checklist became my habit for every project.

## 4. Questions they'll ask, with what they're really testing

| Question | Testing | Tip |
|---|---|---|
| Why data analytics? | Motivation | A specific moment that hooked you, not "data is the new oil" |
| Why our company? | Research | Mention their product, a metric they'd care about, a recent launch |
| Walk me through your project | Depth & ownership | Problem → data → method → insight → impact → what you'd do next |
| How do you ensure your analysis is accurate? | Rigor | Reconcile to a source of truth, sanity checks, row counts, peer review, documented definitions |
| A stakeholder asks for a report "by EOD" with unclear needs. | Stakeholder sense | Clarify the decision behind the ask, agree on a v1, iterate |
| Where do you see yourself in 3 years? | Retention | Growing into senior analyst / analytics engineering / product analytics, here |
| Salary expectations? | Negotiation | Research the range first; give a range; "open to discussing the full package" |

## 5. Questions to ask them (always have 3)

* What does a typical week look like for an analyst on this team? Which tools and data stack?
* What's a recent analysis that changed a decision here?
* How is success measured for this role in the first 90 days?
* Who are the main stakeholders, and how do requests come in?
* What's the biggest data challenge the team faces right now?

## 6. Resume that passes the ATS and the human

* **One page**, reverse-chronological, a clean single-column layout (ATS parsers struggle with tables and graphics), PDF.
* **Headline + skills** that mirror the job description's words: *SQL (joins, window functions, CTEs) · Python (pandas, matplotlib) · Power BI (DAX, Power Query) · Excel (XLOOKUP, PivotTables) · Statistics (A/B testing).*
* **Bullets = action + what + result (number).** "Analysed…", "Built…", "Automated…", "Reduced…".
  * ❌ "Responsible for creating dashboards."
  * ✅ "Built a Power BI dashboard tracking 12 KPIs for 3 regional managers, cutting weekly reporting from 4 hours to 15 minutes."
* **Projects section** (essential for freshers): 2–3 projects, each with a GitHub link + a one-line outcome. See the [resume bullets](../portfolio/shopkart-growth-analysis/README.md#resume-bullets-adapt-the-wording).
* Certifications help only at the margin (e.g. Microsoft PL-300 for Power BI, Google Data Analytics). **Projects beat certificates.**
* Tailor the top third for each application; keep a master resume.

## 7. Portfolio & LinkedIn

* **GitHub**: a pinned repo per project, each with a README that reads like a case study (question, findings with charts, how to reproduce).
* **Dashboard**: publish to Tableau Public / NovyPro, or add screenshots and a GIF to the README.
* **LinkedIn**: headline "Data Analyst | SQL · Python · Power BI"; *Open to Work* (recruiters only, if you're currently employed); post a short project write-up with one chart (it's often more visible than your resume).
* Write one blog-style post explaining an insight. It shows communication skills, which interviewers weigh heavily.

## 8. Job search in India: practical notes

* **Where to look:** LinkedIn Jobs, Naukri, Instahyre, Cutshort, Wellfound (startups), Hirist, iimjobs (for the MBA-analytics track), company career pages (GCCs: banks, retailers, tech), and campus/off-campus drives.
* **Titles to search:** Data Analyst, Business Analyst, MIS Analyst, Reporting Analyst, Product Analyst, BI Developer, Analytics Associate, Operations Analyst, Decision Scientist (junior).
* **Referrals** convert far better than cold applications: message alumni/analysts with a specific, short ask plus your project link.
* **Compensation** varies widely by city, company type and skills (service firms vs product/GCCs). Check current ranges on AmbitionBox, Glassdoor and LinkedIn Salary for the exact role and city rather than relying on averages.
* **Notice periods** (often 30–90 days in India) matter to recruiters: know yours and state it.

## 9. The week before the interview

- [ ] Re-solve 10 SQL questions (mix of window functions, joins, CTEs) without looking
- [ ] Rehearse your project walkthrough out loud in 3 minutes, and be ready for "why?" on every decision
- [ ] Six STAR stories written, each with a number
- [ ] Researched the company: product, business model, likely KPIs, recent news
- [ ] Three questions to ask them
- [ ] Test your setup for virtual rounds (camera, mic, a quiet room, a notebook/SQL environment ready)
