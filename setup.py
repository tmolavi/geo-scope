from setuptools import setup, find_packages

setup(
    name="geo-scope",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "geo_scope": ["static/*", "data/*"],
    },
    install_requires=[
        "fastapi>=0.110.0",
        "uvicorn>=0.28.0",
        "pydantic>=2.5.0",
        "httpx>=0.26.0",
        "requests>=2.31.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scikit-learn>=1.3.0",
    ],
    entry_points={
        "console_scripts": [
            "geo-scope=geo_scope.cli:main",
        ],
    },
)
