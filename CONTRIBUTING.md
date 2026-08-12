# Contributing to GEO-Scope

We welcome contributions from researchers, SEO engineers, data scientists, and developers worldwide! Whether you want to add new AI engine adapters, contribute fresh prompt datasets, improve statistical attribution models, or fix bugs, your help is appreciated.

---

## 🧭 How You Can Contribute

1. **Submit New Industry Benchmark Datasets**:
   - Add prompt templates and competitor taxonomies to `geo_scope/engine/query_generator.py` or `geo_scope/data/`.
2. **Add Custom AI Engine Adapters**:
   - Integrate local models (Ollama, DeepSeek, vLLM) or emerging search engines in `geo_scope/engine/model_runner.py`.
3. **Enhance Feature Extraction**:
   - Improve regex/NLP parsing for footnotes, Markdown citations, and multi-language entity aliases in `geo_scope/engine/feature_extractor.py`.
4. **Refine Statistical & ML Attribution**:
   - Enhance SHAP/regression attribution algorithms in `geo_scope/engine/algo_analyzer.py`.
5. **UI & Visualization Improvements**:
   - Enhance dashboard UI components in `geo_scope/static/index.html`.

---

## 🛠️ Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/your-username/geo-scope.git
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

4. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

5. **Start local development dashboard**:
   ```bash
   geo-scope serve --host 0.0.0.0 --port 8000 --reload
   ```

---

## 📋 Pull Request Workflow

1. Create a descriptive branch (`git checkout -b feature/gemini-pro-adapter`).
2. Implement your changes with clean commit messages.
3. Ensure all tests pass (`pytest`) and code follows PEP 8.
4. Push to your fork and submit a Pull Request.

Thank you for helping build the open science foundation for AI Visibility and GEO!
