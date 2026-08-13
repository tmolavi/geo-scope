# 🤝 Contributing to GEO-Scope

We welcome contributions from researchers, SEO engineers, data scientists, and developers worldwide!

Whether you want to **submit new prompt datasets**, **add an AI provider**, **reproduce or challenge findings**, or **improve statistical models**, your help is appreciated.

---

## ⚡ 5-Minute Quick Contribution Guide

### 1. Add a New Industry Prompt Dataset (Easiest!)
- Add a CSV or JSON file under `datasets/your_industry.csv`.
- Include 10 to 50 representative real-world queries.
- Submit a PR!

### 2. Submit or Challenge an Experiment
- Run a benchmark on your brand/niche:
  ```bash
  geo-scope run --brand "My Brand" --prompts datasets/saas_crm.csv --out results/my_study/
  ```
- Copy `experiments/templates/experiment_template.md` to `experiments/community/my_study.md`.
- Open a PR or submit via the **[Contradictory Finding / Experiment Issue Template](https://github.com/tmolavi/geo-scope/issues/new/choose)**.

### 3. Add a New AI Search Provider
- Subclass `BaseProvider` in `geo_scope/providers/`.
- See the step-by-step tutorial: **[`docs/ADD_A_PROVIDER.md`](docs/ADD_A_PROVIDER.md)**.

---

## 🛠️ Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/tmolavi/geo-scope.git
   cd geo-scope
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   pip install -e .
   ```

4. **Run the test suite**:
   ```bash
   pytest tests/ -v
   ```

5. **Run the 5-Minute Demo**:
   ```bash
   geo-scope demo
   ```

6. **Launch the Web Dashboard**:
   ```bash
   geo-scope serve --host 0.0.0.0 --port 8000 --reload
   ```

---

## 📋 Pull Request Checklist

- [ ] Code follows PEP 8 style standards (`flake8`).
- [ ] All tests pass (`pytest tests/ -v`).
- [ ] New functionality or datasets are documented.
- [ ] Commit message is clear and descriptive.

Thank you for helping build an empirical, open-science foundation for AI Search & GEO!
