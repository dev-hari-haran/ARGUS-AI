<div align="center">

<img src="assets/banner.svg" alt="IK-ML — 2DOF Planar Manipulator Inverse Kinematics" width="100%"/>

<br/>

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![scikit--learn](https://img.shields.io/badge/scikit--learn-Baselines-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-Native%20Multi--Output-EB0028?style=for-the-badge)](https://xgboost.readthedocs.io/)
[![Optuna](https://img.shields.io/badge/Optuna-HP%20Search-2C5BB4?style=for-the-badge)](https://optuna.org/)
[![License](https://img.shields.io/badge/License-MIT-34d399?style=for-the-badge)](LICENSE)
[![Execution](https://img.shields.io/badge/Execution-Manual%20CMD%20Only-f472b6?style=for-the-badge)](#-execution-guide)

**Learning inverse kinematics instead of solving it.**
Five tree-based regressors predict joint angles **(θ₁, θ₂)** directly from a target position **(X, Y)** and robot geometry **(L1, L2)** —
every prediction verified against ground-truth forward kinematics.

[Quick Start](#-quick-start) · [Architecture](#-architecture) · [The Branch Problem](#-the-branch-problem) · [Models](#-models) · [Execution Guide](#-execution-guide) · [Results](#-evaluation--metrics)

</div>

---

## ✦ Overview

A 2DOF planar manipulator has a closed-form IK solution — which is precisely why it makes an ideal, fully-verifiable benchmark for **learned** inverse kinematics. Because forward kinematics is exact, every model prediction can be pushed back through FK and scored in **task space** (millimetres of Cartesian error), not just in joint space.

<div align="center">
<img src="assets/pipeline.svg" alt="End-to-end pipeline" width="100%"/>
</div>

### What this project is — and is not

| ✅ In scope | ❌ Out of scope |
|---|---|
| Supervised ML regression for IK | Optimization-based IK solvers (Jacobian, CCD, FABRIK) |
| Hyperparameter search (Grid / Random / Optuna) | Metaheuristics applied to IK (GA, PSO, DE, SA) |
| FK-verified Cartesian error evaluation | ML vs. optimization comparisons *(future project)* |
| Single-branch dataset by construction | Multi-solution / redundant manipulators |

> **Note on Optuna.** Optuna is used **strictly for hyperparameter search** — a standard part of ML model development. It is never applied to the IK problem itself.

---

## ⚡ Quick Start

```bat
:: 1 — Clone and enter
git clone https://github.com/<you>/ik-ml-2dof.git
cd ik-ml-2dof

:: 2 — Environment
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

:: 3 — Generate the dataset (elbow-down branch, 50k samples)
python -m src.dataset.generate_dataset

:: 4 — Train one model
python -m src.training.train_random_forest

:: 5 — Predict a point for a specific robot geometry and verify with FK
python src\inference\predict.py --x 1.2 --y 0.8 --l1 1.0 --l2 1.0 --model random_forest
```

> ⚠️ **Nothing in this repository runs automatically.** No auto-training, no auto-tuning, no hidden entry points. Every stage is a deliberate, manual command — see the [Execution Guide](#-execution-guide).

---

## 🧭 The Branch Problem

**The single most important design decision in this repository.**

For almost every reachable point, a 2-link arm admits **two** valid solutions — *elbow-up* and *elbow-down*. A regressor trained on both learns their **average**: a joint configuration that reaches *neither*.

```
            elbow-up ●
           ╱        ╲
   base ●──          ● target        ← both are "correct"...
           ╲        ╱
            elbow-down ●             ← ...their average is garbage.
```

**Resolution — enforced at data generation, not patched afterward:**

| Policy | Mechanism |
|---|---|
| One branch per dataset | Joint angles sampled *within* branch-defining limits |
| Default: **elbow-down** | `θ₂ ∈ [0, π]` in `configs/robot.yaml` |
| Switchable | `solution_branch: elbow_up` → `θ₂ ∈ [−π, 0]` |
| Verified | Data-generation report asserts 100% branch compliance |

---

## 🏗 Architecture

<div align="center">
<img src="assets/architecture.svg" alt="Modular architecture" width="100%"/>
</div>

<details>
<summary><b>📁 Full folder tree</b></summary>

```
project/
├── assets/                     # README figures (SVG)
├── configs/
│   ├── robot.yaml              # L1, L2, joint limits, solution branch
│   ├── dataset.yaml            # sample count, seed, densification
│   ├── features.yaml           # engineered-feature toggles
│   ├── preprocessing.yaml      # scaler selection
│   ├── split.yaml              # 70/15/15 ratios, k-fold settings
│   ├── models/                 # one YAML per model
│   └── tuning/                 # one search-space YAML per model
├── data/
│   ├── raw/ · generated/ · processed/
├── models/                     # saved artifacts + fitted scalers
├── outputs/
│   ├── reports/ · metrics/ · plots/ · logs/
├── src/
│   ├── kinematics/             # the single FK authority
│   ├── dataset/ · features/ · preprocessing/ · splitting/
│   ├── training/ · evaluation/ · robustness/ · comparison/
│   ├── visualization/ · tuning/ · explainability/ · inference/
│   └── utils/
├── tests/
├── README.md · requirements.txt · environment.yml · .gitignore
```
</details>

**Design guarantees**

- 🔩 **One FK implementation.** `src/kinematics/` is imported everywhere; never re-derived.
- 🧾 **Zero hardcoding.** Every tunable lives in `configs/` behind a validated, typed loader.
- 🚱 **No leakage.** Scalers fit on the training split only. The test set is touched **exactly once**.
- 🧱 **Vertical independence.** Every module runs standalone via `python -m`.

---

## 🤖 Models

| # | Model | Multi-Output Strategy | Why |
|---|---|---|---|
| 1 | Decision Tree | Native | Interpretable floor baseline |
| 2 | Random Forest | Native | Variance-reduced ensemble |
| 3 | Extra Trees | Native | Faster, more randomized splits |
| 4 | HistGradientBoosting | `MultiOutputRegressor` wrapper | No native multi-output support |
| 5 | XGBoost ≥ 2.0 | **Native** — `multi_strategy="multi_output_tree"` | θ₁ and θ₂ are physically coupled; independent per-output estimators discard that structure |

> A config fallback (`use_multioutput_wrapper: true`) exists for XGBoost < 2.0.

**Validation strategy.** 5-fold cross-validation (configurable) runs on the *training split* during development and tuning. The held-out validation set selects models; the test set delivers the final verdict, once.

---

## 🕹 Execution Guide

**Every command below is typed by a human, in a Windows CMD terminal, in dependency order.** The codebase contains no automatic execution paths — by design.

<table>
<tr><th>Stage</th><th>Command</th></tr>
<tr><td>1 · Generate dataset</td><td><code>python -m src.dataset.generate_dataset</code></td></tr>
<tr><td>2 · Feature engineering</td><td><code>python -m src.features.build_features</code></td></tr>
<tr><td>3 · Preprocess + split</td><td><code>python -m src.preprocessing.run_preprocessing</code></td></tr>
<tr><td rowspan="2">4 · Train (pick one / all)</td><td><code>python -m src.training.train_random_forest</code></td></tr>
<tr><td><code>python -m src.training.train_all</code></td></tr>
<tr><td>5 · Evaluate</td><td><code>python -m src.evaluation.evaluate --model random_forest</code></td></tr>
<tr><td>6 · Robustness suite</td><td><code>python -m src.robustness.run_robustness --model random_forest</code></td></tr>
<tr><td>7 · Compare all models</td><td><code>python -m src.comparison.compare_models</code></td></tr>
<tr><td>8 · Tune (never automatic)</td><td><code>python -m src.tuning.tune_random_forest --method optuna</code></td></tr>
<tr><td>9 · Explainability</td><td><code>python -m src.explainability.explain --model random_forest</code></td></tr>
<tr><td>10 · Inference</td><td><code>python -m src.inference.predict --x 1.2 --y 0.8 --model random_forest</code></td></tr>
<tr><td>11 · Batch inference</td><td><code>python -m src.inference.predict --csv targets.csv --model random_forest</code></td></tr>
</table>

During training, a live terminal dashboard reports: current model, stage, progress %, CV fold, elapsed / ETA, CPU %, RAM %, latest CV score, and log-file path.

---

## 📏 Evaluation & Metrics

**Joint space** — MAE · MSE · RMSE · Median AE · R² *(per angle and averaged)*

**Task space — the headline metric:**

$$\text{Cartesian Error} = \left\| \, FK(\hat{\theta}_1, \hat{\theta}_2) - (X_{target}, Y_{target}) \, \right\|_2$$

Reported as **mean · median · max · p95**. Defined once; there is deliberately no second, differently-named duplicate of this quantity.

**Cost** — training time · per-sample & batch inference time · peak training memory · model size on disk.

### 🛡 Robustness suite

| Scenario | Probe |
|---|---|
| Outer workspace boundary | `r ≈ L1 + L2` — arm near full extension |
| Inner boundary | `r ≈ \|L1 − L2\|` — arm near full fold |
| Near-singular regions | `θ₂ ≈ 0` or `≈ π` (tolerance in config) |
| Unseen positions | Uniform random samples never in training |
| Noisy inputs | Gaussian noise on (X, Y), σ configurable |

### 📊 Visual reports

Every figure exported in **PNG (300 dpi) · PDF · SVG**: predicted-vs-actual angles, residual distributions, workspace error heatmaps, end-effector scatter, Cartesian error CDF, learning curves, feature importance, CV-spread bias-variance plots.

---

## 🔍 Explainability

- Impurity + permutation feature importance for all tree models
- **SHAP** — one explainer **per output** (θ₁, θ₂); wrapped models get per-sub-estimator explainers. Gracefully skipped if SHAP is not installed.
- Residual analysis, prediction distributions, error-vs-feature diagnostics

---

## 🧪 Testing

```bat
python -m pytest tests\ -v
```

Coverage includes: FK correctness against hand-computed cases · branch-policy enforcement in generated data · scaler fit-on-train-only guarantee · split reproducibility · (θ₁, θ₂) → FK → dataset round-trip consistency.

---

## ⚙️ Configuration

Everything tunable lives in `configs/`:

```yaml
# configs/robot.yaml
link_lengths:
  l1: [0.5, 2.0]  # Min/Max length of first link
  l2: [0.5, 2.0]  # Min/Max length of second link
joint_limits:
  q1: [-3.14159, 3.14159]
  q2: [-3.14159, 3.14159]
```

```yaml
# configs/split.yaml
ratios: { train: 0.70, val: 0.15, test: 0.15 }
random_seed: 42
cross_validation: { enabled: true, k_folds: 5 }
```

---

## 🤝 Contributing · 📄 License

PRs welcome — see `CONTRIBUTING.md`. All code requires type hints, Google-style docstrings, and passing tests. Released under the **MIT License**.

<div align="center">
<br/>

**`(X, Y, L1, L2)` → Universal Model → `(θ₁, θ₂)` → FK-verified → ✓**

<sub>Built as a research-grade benchmark for learned inverse kinematics · CPU-only · Manually executed, always</sub>

</div>
