# 03 · Statistics & A/B testing for data analysts

You don't need to derive formulas. You need to **choose the right method, run it, interpret it correctly and explain
it to a non-technical stakeholder.** Interviewers probe *understanding*: "what does a p-value mean?", "why might this
A/B result be misleading?"

**Practice:** pandas exercises p19–p22 · SQL Q35 · the [portfolio A/B readout](../portfolio/shopkart-growth-analysis/README.md#6-experiment-new-checkout)

---

## 1. Descriptive statistics

| Concept | What to know |
|---|---|
| Mean vs median | The mean is pulled by outliers/skew. Order values and incomes are right-skewed, so **report the median** (ShopKart: median order ₹2,297 vs mean ₹3,015) |
| Mode | Most frequent value; the only "average" for categorical data |
| Variance / standard deviation | Spread around the mean; SD is in the original units |
| Percentiles / IQR | IQR = Q3 − Q1. The outlier rule: below Q1 − 1.5·IQR or above Q3 + 1.5·IQR |
| Skewness | Right skew: mean > median (long right tail). Log-transform to analyse |
| Coefficient of variation | SD ÷ mean, to compare variability across different scales |

**Always look at the distribution** (histogram / box plot) before summarising. *Anscombe's quartet* is four datasets
with identical means, variances and correlations but completely different shapes.

## 2. Distributions you should recognise

* **Normal**: symmetric bell. About 68% / 95% / 99.7% of values fall within 1 / 2 / 3 SDs.
* **Binomial**: number of successes in n yes/no trials (conversions out of visitors). Mean np, variance np(1−p).
* **Poisson**: counts of events per interval (orders per hour, support tickets per day). Mean = variance = λ.
* **Log-normal**: positive and right-skewed (order values, session length, income).
* **Exponential**: time between events (time to next order).

## 3. Sampling, CLT and confidence intervals

* **Central Limit Theorem:** the *sampling distribution of the mean* is approximately normal for large n (≈30+), whatever the data's shape. That's why z/t-tests work on skewed order values when n is large.
* **Standard error** = SD / √n. It's the uncertainty of the *estimate*, not the spread of the data. It shrinks with √n, so 4x the data halves the SE.
* **95% CI** ≈ estimate ± 1.96 × SE. Interpretation: *if we repeated the study many times, 95% of intervals built this way would contain the true value.* (Not "95% probability the true value is in this interval". That's the Bayesian credible interval.)
* **Bias** beats sample size: a huge biased sample (survivorship, self-selection, non-response) is still wrong.

## 4. Hypothesis testing

1. **H₀** (null): no difference/effect. **H₁** (alternative): there is one.
2. Choose **α** (usually 0.05) *before* looking.
3. Compute a test statistic and its **p-value**.
4. If p < α, reject H₀ ("statistically significant"); otherwise, *fail to reject* (which is not proof of no effect).

**p-value** = the probability of seeing a result at least this extreme **if H₀ were true**. It is *not* the
probability that H₀ is true, and it says nothing about the *size* or *business value* of the effect.

| | H₀ true | H₀ false |
|---|---|---|
| Reject H₀ | **Type I error** (false positive), rate = α | Correct (power = 1 − β) |
| Don't reject | Correct | **Type II error** (false negative), rate = β |

### Which test?

| Question | Data | Test |
|---|---|---|
| Two conversion rates differ? | proportions | **two-proportion z-test** (or chi-square test) |
| Two means differ (e.g. AOV)? | continuous | **Welch's t-test** (don't assume equal variances) |
| Same users before/after? | paired | paired t-test |
| 3+ group means? | continuous | ANOVA (then post-hoc tests) |
| Two categorical variables related? | counts table | chi-square test of independence |
| Skewed data, small n, or outliers? | ranks | Mann-Whitney U, or bootstrap the difference |
| Relationship between two numeric variables? | continuous | Pearson (linear) / Spearman (monotonic) correlation |

## 5. A/B testing, end to end

**Design**
1. **Hypothesis** with a mechanism: "a shorter checkout reduces drop-off, so conversion rises."
2. **Primary metric** (one!) plus **guardrail metrics** (revenue per visitor, refunds, latency) and secondary metrics.
3. **Randomisation unit** (user, not session, to avoid the same person seeing both variants).
4. **Sample size** from the baseline rate, the minimum detectable effect (MDE), α and power. Rule of thumb for 80% power and α = 0.05:

   > **n per group ≈ 16 · p(1−p) / δ²**. Baseline 10%, detect +1 pp → 16 · 0.09 / 0.0001 ≈ **14,400 per group**

5. **Duration**: fixed in advance, at least one or two full weekly cycles.

**Run**: check for **sample ratio mismatch** (SRM). A 50/50 test that comes out 52/48 at large n signals a bucketing bug,
so run a chi-square goodness-of-fit test. Don't **peek** and stop early when it looks significant, because that inflates false positives.

**Analyse**: the worked example below uses ShopKart's checkout test.

| | Visitors | Conversions | Rate |
|---|---:|---:|---:|
| A (control) | 12,006 | 1,242 | 10.34% |
| B (new checkout) | 11,994 | 1,414 | 11.79% |

```
pooled p  = (1242 + 1414) / (12006 + 11994) = 0.1107
SE_pooled = √(0.1107 · 0.8893 · (1/12006 + 1/11994)) = 0.00405
z         = (0.1179 − 0.1034) / 0.00405 = 3.57      → p ≈ 0.0004 (two-sided)
95% CI    = 1.45 pp ± 1.96 · 0.00405  →  +0.65 to +2.24 pp   (unpooled SE)
relative lift = 1.45 / 10.34 ≈ +14%
```

```python
from statsmodels.stats.proportion import proportions_ztest   # or scipy, as in the practice solutions
z, p = proportions_ztest([1414, 1242], [11994, 12006])
```

**Interpret and decide**
* Is it **statistically** significant? (p, CI excludes 0)
* Is it **practically** significant? (Is +1.45 pp worth the engineering cost? What's the revenue impact?)
* Guardrails OK? Any segment where it *hurts*?
* The recommendation, framed for the business: "Ship to App; estimated ₹X/yr; follow-up test on web."

### Pitfalls interviewers love

| Pitfall | What goes wrong | Guard against it |
|---|---|---|
| **Peeking / early stopping** | Checking daily and stopping at p < 0.05 inflates false positives far above 5% | Fixed horizon, or sequential testing methods |
| **Multiple comparisons** | 20 metrics or segments → about one "significant" by chance | One primary metric; Bonferroni (α/k) or FDR control; treat segment findings as hypotheses |
| **Novelty / primacy effect** | Users react to the change itself, not to it being better | Run longer; look at the effect over time and for new vs returning users |
| **SRM** | Unequal split, meaning broken randomisation | Chi-square check before analysing |
| **Network effects / interference** | Treatment users affect control users (marketplaces, social) | Cluster or geo randomisation |
| **Simpson's paradox** | The aggregate trend reverses within every subgroup because the mix differs | Stratify / check segments; randomisation protects the *overall* comparison |
| **Underpowered test** | "No significant difference" when the test could never have detected the MDE | Do the sample-size calculation first |
| **Wrong unit of analysis** | Randomised by user but analysed per session, so SE is too small | Analyse at the randomisation unit |

## 6. Correlation, causation and regression

* **Correlation ≠ causation.** Confounders (a third variable drives both), reverse causality, selection bias and pure coincidence. *Example: customers who use coupons have lower AOV. Do coupons cause smaller baskets, or do price-sensitive shoppers do both?*
* Tools for causation without an experiment: difference-in-differences, regression discontinuity, matching / propensity scores, instrumental variables. For a junior role, knowing their names and when they apply is enough.
* **Linear regression:** `y = b₀ + b₁x₁ + … + ε`. b₁ = the expected change in y per unit of x₁ *holding the other variables constant*. R² = the share of variance explained (a high R² doesn't mean causal or a good forecast). Check residuals, multicollinearity and outliers.
* **Logistic regression** predicts probabilities for binary outcomes (churn yes/no); coefficients are log-odds.

## 7. Interview questions

<details><summary><b>Explain a p-value to a product manager.</b></summary>"If the new checkout truly made no difference, we'd see a gap this big less than 0.04% of the time just from random chance. So we're confident the difference is real. Whether it's big enough to matter is a separate question, and here it's worth about ₹14 L a year."</details>
<details><summary><b>Your test shows p = 0.06. What do you do?</b></summary>Don't call it a win, and don't extend the test just to get under 0.05 (that's p-hacking). Report the effect estimate and CI. If the CI includes business-relevant effects, it may be underpowered, so consider a properly sized re-run. Decide based on cost/risk: a cheap, reversible change can still ship.</details>
<details><summary><b>Conversion went up but revenue per user went down. Ship?</b></summary>Check the guardrail properly: did AOV drop (more small orders)? Was the discount mix different? Decide based on the business's primary objective (profit), and consider a segment-level look.</details>
<details><summary><b>How long should the test run?</b></summary>Long enough to reach the pre-computed sample size AND cover full weekly cycles (usually at least 1–2 weeks), decided in advance.</details>
<details><summary><b>Mean or median for delivery time?</b></summary>Median (and p90/p95). Delivery times are right-skewed, and a few extreme delays distort the mean. SLAs usually use percentiles.</details>
<details><summary><b>What is statistical power?</b></summary>The probability of detecting an effect of a given size if it really exists (1 − β), usually targeted at 80%. It increases with sample size, effect size and α, and falls as variance rises.</details>
<details><summary><b>What's the difference between standard deviation and standard error?</b></summary>SD describes the spread of individual data points; SE describes the uncertainty in an estimate (like the mean) and shrinks as n grows (SE = SD/√n).</details>
