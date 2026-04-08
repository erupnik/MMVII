# Least Squares and Uncertainty Estimation

---

## Notation and formulation

### System of equations

Consider a system of $M$ equations in $N$ unknowns with $M \geq N$:

$$\forall j : \sum_{i=1}^N l_{i,j}\, x_i = b_j$$

Writing $L_j = (l_{i,j})$ and $X = (x_i)$ as vectors in $\mathbb{R}^N$:

$$\forall j : L_j \cdot X = b_j$$

### Least squares solution

When $M > N$ there is generally no exact solution, so we minimise the sum of squared residuals:

$$R(X) = \sum_{j=1}^M \bigl(L_j \cdot X - b_j\bigr)^2$$

Expanding:

$$R(X) = X \cdot A X - 2\, B \cdot X + C$$

where the **normal matrix** $A$, right-hand side $B$, and constant $C$ are:

$$A = \sum_j L_j\, {}^t\!L_j \qquad B = \sum_j L_j\, b_j \qquad C = \sum_j b_j^2$$

The minimiser $\bar{X}$ satisfies:

$$\bar{X} = A^{-1} B$$

and the minimum residual is:

$$R(\bar{X}) = C - B \cdot \bar{X}$$

---

## Weighting

Observation weighting is non-trivial in MMVII because many heterogeneous observations are
combined and some may be faulty.

### Constant weighting — `cResidualWeighter`

The default weighter assigns a constant weight to all observations in a set. It corresponds
to classical least squares and is appropriate when residuals follow a Gaussian distribution
with no outliers.

### Simulated L1 weighting

Classical least squares is very sensitive to outliers. L1 optimisation (minimising the sum
of absolute residuals) is more robust but harder to compute. A weighted least squares
formulation can approximate L1 behaviour by making the weight a function of the residual.

Minimising:

$$\sum_j w_j\!\left(r_j(X)\right) r_j(X)^2 \quad \text{with} \quad w_j(r) = \frac{1}{|r|}$$

is equivalent to L1. Since this weight diverges near zero, MMVII uses the attenuated form:

$$w_j(r) = \frac{1}{1 + \sqrt{r^2}}$$

which behaves like classical least squares for small residuals and like L1 for large ones.

### Residual-based weighting — `cStdWeighterResidual`

`cStdWeighterResidual` is MMVII's standard weighter for datasets with possible outliers.
It is parametrised by $\sigma$, $\sigma_{\text{att}}$, $\text{Exp}$, and a threshold
$\text{Thrs}$:

$$w(r) = \begin{cases}
0 & \text{if } |r| > \text{Thrs} \\[6pt]
\dfrac{1}{\sigma^2} \cdot \dfrac{1}{\displaystyle 1 + \left(\dfrac{r^2}{\sigma_{\text{att}}^2}\right)^{\!\text{Exp}/2}} & \text{otherwise}
\end{cases}$$

Default values:

| Parameter | Default | Effect |
|-----------|---------|--------|
| $\sigma_{\text{att}}$ | $-1$ | Attenuation disabled — pure $1/\sigma^2$ weighting |
| $\text{Exp}$ | $1$ | Attenuated L1 behaviour |
| $\text{Thrs}$ | $-1$ | No threshold — observations are never cancelled |

![Weight function $w(r)$ for various parameter combinations](images/cStdWeighterResidual.png)

---

## Uncertainty estimation

### Gauss-Markov theorem

If the residuals $L_j \cdot X - b_j$ are independent realisations of a zero-mean random
variable with common variance $\sigma^2$, then the
[Gauss-Markov theorem](https://en.wikipedia.org/wiki/Gauss-Markov_theorem) states that
$\bar{X} = A^{-1}B$ is the **best linear unbiased estimator** (BLUE) of $X$.

The variance-covariance matrix $\Sigma$ of $\bar{X}$ is estimated by:

$$\Sigma = A^{-1} \sigma_0^2 \qquad \text{where} \qquad \sigma_0^2 = \frac{R(\bar{X})}{N} \cdot \frac{M}{M - N}$$

When the minimisation includes $m^C$ hard constraints, the denominator is adjusted:

$$\Sigma = A^{-1} \cdot \frac{R(\bar{X})}{N} \cdot \frac{M + m^C}{M + m^C - N}$$

The variance-covariance estimator remains correct for variables not involved in the
constraints.

### Efficient computation

Forming $A^{-1}$ explicitly is expensive for large systems. In most practical cases only
partial information is needed:

**Single variable** — to estimate the uncertainty of the $k$-th variable only, solve
$A\, c' = e_k$ (where $e_k$ is the $k$-th unit vector) and read off $(c')_k$.

**Set of variables** — for a set $S = \{k_1, \dots, k_l\}$, solve $A\, \mathcal{C}' =
\mathcal{C}(S)$ where $\mathcal{C}(S)$ is the $N \times l$ matrix of the corresponding
unit vectors.

**Linear combinations** — for vectors $V_1, \dots, V_m$, the covariance of
$\bar{V}_{k_1} = V_{k_1} \cdot \bar{X}$ and $\bar{V}_{k_2} = V_{k_2} \cdot \bar{X}$ is:

$$\text{Cov}(\bar{V}_{k_1}, \bar{V}_{k_2}) = {}^t\!V_{k_1}\, A^{-1} V_{k_2}\, \sigma_0^2$$

Again, only the solve $A\, V'_{k_2} = V_{k_2}$ is needed, not the full inverse.

**All at once** — to compute $\bar{X}$, $l$ variable uncertainties, and $m$ linear
combination uncertainties in a single solve, assemble the $(1 + l + m) \times N$ matrix $M$
whose columns are $B$, the $l$ unit vectors, and the $m$ direction vectors, then solve $A
M' = M$.

---

## MMVII implementation

### Timing

Uncertainty computation must happen when the normal matrix is complete — after all
observations and constraints have been added, including any Levenberg-Marquardt
stabilisation. This is inside `SolveUpdateReset`. Computing before this point gives an
incomplete system; after it, the matrix has been reset and the information is lost.

The design choice is to pass an optional result structure into `SolveUpdateReset`, which
fills it during the solve.

### `cResult_UC_SUR`

The structure `cResult_UC_SUR` carries the uncertainty request and receives the results.
Its constructor takes:

- a boolean: compute var/covar for **all** variables;
- a boolean: compute the full normal matrix (rarely needed);
- a list of variable indices for which var/covar is required;
- a list of sparse vectors for linear combination var/covar.

After `SolveUpdateReset` returns, the structure exposes:

- covariance between requested variables;
- covariance between requested linear combinations;
- $\sigma_0$ (useful for quality checks);
- the full solution matrix $M'$ (for advanced use).

### Validation

A bench test in `Bench/BenchPropagUncert.cpp` validates the implementation by exhaustive
enumeration. For a random system with $M$ observations of dimension $N$:

1. Generate $M$ random observation vectors $V_1, \dots, V_M$ and a random true solution $P$.
2. For each observation $V_k$, generate a discrete uniform law centred on $V_k \cdot P$
   with a small number of values $n_k$ and variance $\sigma$.
3. Enumerate all $\mathcal{N} = n_1 \cdots n_M$ possible combinations; for each, compute
   the least squares solution $S_c$ and its covariance estimate $\Sigma_c$.
4. Compare the empirical covariance $\mathcal{E}^\mathcal{C}$ of the $S_c$ against
   $\bar{\Sigma} = \frac{1}{\mathcal{N}} \sum \Sigma_c$.

The Gauss-Markov theorem predicts $\bar{\Sigma} = \mathcal{E}^\mathcal{C}$, which is
confirmed by the bench.
