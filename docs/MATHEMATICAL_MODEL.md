# 📐 Mathematical Model: GEO Metrics & Factor Attribution

## 1. Share of Model (SoM) / Share of Voice

Let $\mathcal{Q} = \{q_1, q_2, \dots, q_N\}$ be the set of evaluation queries, and $\mathcal{M} = \{m_1, m_2, \dots, m_K\}$ be the set of evaluated AI models.

For a target brand $B$ and model $m$, the indicator function $\mathbb{I}(B \in R(q_i, m))$ equals $1$ if brand $B$ is explicitly recommended in the model response $R(q_i, m)$, and $0$ otherwise.

$$\text{Share of Model (SoM)}_{B, m} = \frac{1}{N} \sum_{i=1}^{N} \mathbb{I}(B \in R(q_i, m)) \times 100\%$$

Overall cross-model Share of Model:
$$\text{Overall SoM}_B = \frac{1}{K \cdot N} \sum_{j=1}^{K} \sum_{i=1}^{N} \mathbb{I}(B \in R(q_i, m_j)) \times 100\%$$

---

## 2. Top-1 Recommendation Probability

Let $\text{Rank}(B, R(q_i, m)) \in \{1, 2, 3, \dots, \infty\}$ represent the ordinal position of brand $B$ in the ordered recommendation list of the response.

$$\mathbb{P}(\text{Rank}_1)_{B, m} = \frac{1}{N} \sum_{i=1}^{N} \mathbb{I}(\text{Rank}(B, R(q_i, m)) = 1) \times 100\%$$

---

## 3. Citation Graph Centrality & Category Entropy

Let $\mathcal{C}(q_i, m)$ be the multiset of cited domains in response $R(q_i, m)$.

The domain citation frequency $f(d)$ for domain $d \in \mathcal{D}$ across all queries is:
$$f(d) = \sum_{i=1}^{N} \sum_{c \in \mathcal{C}(q_i, m)} \mathbb{I}(\text{Domain}(c) = d)$$

The **Source Diversity / Citation Entropy** $H(m)$ for an AI engine $m$ across $C$ source categories is:
$$H(m) = -\sum_{c=1}^{C} p_c \log_2(p_c) \quad \text{where} \quad p_c = \frac{\text{Count}(\text{Category } c)}{\sum_k \text{Count}(\text{Category } k)}$$

---

## 4. Ranking Factor Reverse-Engineering (SHAP & Regression)

To deduce the underlying factor weights vector $\mathbf{w}_m = [w_{\text{ugc}}, w_{\text{review}}, w_{\text{pr}}, w_{\text{wiki}}, w_{\text{struct}}, w_{\text{fresh}}]^T$ for each engine $m$, we formulate a logistic attribution model:

$$\log \left( \frac{\mathbb{P}(\text{Rank}_1)}{1 - \mathbb{P}(\text{Rank}_1)} \right) = \beta_0 + \sum_{j=1}^{F} w_j \cdot X_{ij} + \epsilon_i$$

Where $X_{ij}$ represents the normalized feature signal $j$ for prompt query $i$:
- $X_{i, \text{ugc}}$: Presence of brand in upvoted community discussions (Reddit/Quora).
- $X_{i, \text{review}}$: Brand 4.5+ star review volume and G2 Grid Leader presence.
- $X_{i, \text{pr}}$: Domain Authority & editorial PR coverage density.
- $X_{i, \text{wiki}}$: Brand presence in Wikidata entity graph and structured JSON-LD schema.
- $X_{i, \text{struct}}$: Markdown comparison tables, BLUF summary density, and quantitative statistics.
- $X_{i, \text{fresh}}$: Content publication date freshness ($t \le 180 \text{ days}$).
