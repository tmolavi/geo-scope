# Packaging & PyPI Readiness Roadmap

**Author**: [Taghi Molavi](https://molavi.pro)  
**Status**: Pre-Publish Verification  
**Scope**: `sage-audit`, `siteprobe`, `answerpath-geo`, `geo-scope`

---

## 1. PyPI Readiness Assessment

| Package Name | Current Version | Build System | Target Command | Dependencies | Readiness |
| :--- | :---: | :---: | :--- | :--- | :---: |
| **`sage-audit`** | `2026.1.1` | `hatchling` | `pip install sage-audit` | `trafilatura`, `httpx`, `pydantic` | **Ready for PyPI** |
| **`siteprobe`** | `2026.1.1` | `setuptools` | `pip install siteprobe` | `httpx`, `beautifulsoup4`, `rich`, `pydantic` | **Ready for PyPI** |
| **`answerpath-geo`**| `2026.1.1` | `setuptools` | `pip install answerpath-geo`| `pydantic`, `fastapi`, `uvicorn` | **Ready for PyPI** |
| **`geo-scope`** | `2026.1.1` | `setuptools` | `pip install geo-scope` | `httpx`, `pandas`, `pydantic`, `rich` | **Ready for PyPI** |

---

## 2. Build Verification Checklist

Before publishing to PyPI:
1. **Source & Wheel Build**:
   ```bash
   python -m build
   # Verify that dist/*.tar.gz and dist/*.whl are created without missing modules
   ```
2. **Twine Validation**:
   ```bash
   twine check dist/*
   # Verify valid long_description markdown rendering and metadata compliance
   ```
3. **Clean Environment Test**:
   ```bash
   python -m venv test_env
   test_env/bin/pip install dist/*.whl
   test_env/bin/<command> --version
   ```

---

## 3. Safe Release Timeline

1. **Phase 1 (Current)**: Local and GitHub release tag verification (`v2026.1.1`).
2. **Phase 2 (Staging)**: Build verification on TestPyPI (`test.pypi.org`).
3. **Phase 3 (Production)**: Automated GitHub Actions trusted publishing to PyPI via OIDC token authentication.
