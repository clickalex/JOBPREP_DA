# Mock interviews

Reading notes isn't the same as performing under a clock with someone watching. This folder holds **ready-to-run
interview scripts**: hand one to a friend, a study partner, or a mentor, and they can play the interviewer without
knowing any SQL. Every number in the answer keys was produced by running queries against `data/shopkart.db`.

| Round | Format | Time | What it simulates |
|---|---|---|---|
| [01 · Live SQL round](01-live-sql-round.md) | Shared screen, you write queries out loud | 45 min | The technical screen at most companies |
| [05 · Live SQL round 2: product & marketing](05-live-sql-round-2.md) | Same format, new questions | 45 min | Coupons, AOV, cohort value, churn, a fan-out trap |
| [06 · Live SQL round 3: advanced](06-live-sql-round-3.md) | Same format, harder | 45 min | Medians, event sequences, rolling windows, the `NOT IN` NULL trap |
| [02 · Case round](02-case-round.md) | Whiteboard / conversation, then a few queries | 40 min | "Metric X dropped, what happened?" |
| [03 · Take-home assignment](03-take-home-assignment.md) | Async, 4-hour time box | 4 h + 20 min review | The take-home many analyst loops include |
| [04 · Stats & concepts rapid-fire](04-stats-rapid-fire.md) | Quick questions, 60–90 s each | 20 min | The "do you actually understand this" round |
| [07 · Data analyst interview Q&A](07-interview-qa.md) | Recruiter, project, technical and situational judgement questions | 45–60 min | Practise concise, credible answers across the interview loop |

## How to run a mock

1. **Book it like a real interview.** Put it on the calendar, camera on, 5 minutes early. The nerves are part of the
   practice.
2. **The interviewer reads only the script.** Every question has hints to give if you're stuck and follow-ups to push
   when you're doing well. The answer keys are collapsed, so the interviewer can peek without you seeing.
3. **Think out loud.** Silence is the #1 reason candidates fail rounds they "knew". Say what you're about to do before
   you type it.
4. **Score honestly with the rubric below**, then write down the *one* thing to fix before the next mock.
5. **Repeat weekly** from week 6 of the [8-week plan in the main README](../README.md). Swap roles with a study partner;
   interviewing others teaches you what good answers sound like.

Solo? All three live SQL rounds have **timed, auto-graded versions in the
[SQL Playground](https://clickalex.github.io/JOBPREP_DA/playground/#m1)** (pick the round next to the timer; hints,
follow-ups and a scorecard included). Do them in order: round 1 → 2 → 3.
For the other rounds, record yourself (screen + voice), set a timer, and grade the recording the next day with the rubric.

## Universal scoring rubric (1–4 per dimension)

| Dimension | 1: Not yet | 2: Borderline | 3: Hire | 4: Strong hire |
|---|---|---|---|---|
| **Problem framing** | Starts typing immediately | Asks one clarifying question | Clarifies grain, filters, edge cases before starting | Also states assumptions and how they'd validate them |
| **Technical correctness** | Wrong or doesn't run | Runs, but off (double counting, wrong filter) | Correct | Correct, readable, handles NULLs/ties/empty results unprompted |
| **Communication** | Silent, or narrates keystrokes | Explains *what* but not *why* | Clear reasoning, checks in with the interviewer | Structured, concise, adapts to hints gracefully |
| **Business sense** | Reports numbers only | Some interpretation | Says what the numbers mean for the business | Recommends an action and a next analysis, sized in ₹ or % |
| **Verification** | Never checks results | Checks when prompted | Sanity-checks row counts/totals | Reconciles against a known total, spots anomalies |

**Rough bar:** 3+ on average with no 1s is a pass at most entry-level loops. A 1 in *technical correctness* or
*communication* usually ends the loop, even if everything else is strong.

## After the mock: debrief template

```text
Round / date:
Scores (framing / technical / communication / business / verification):
What went well (keep doing):
Biggest miss (fix before next mock):
Concept to review (link to study-guide section):
Question I'd answer differently now:
```
