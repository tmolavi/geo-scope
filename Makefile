.PHONY: install dev test lint run serve docker-build docker-up clean

install:
	pip install -e .

dev:
	pip install -r requirements-dev.txt
	pip install -e .

test:
	pytest tests/ -v

lint:
	flake8 geo_scope/ tests/ --max-line-length=120 --exclude=__pycache__

run:
	geo-scope run --count 1000 --out output/

serve:
	geo-scope serve --host 0.0.0.0 --port 8000

docker-build:
	docker build -t geo-scope .

docker-up:
	docker-compose up -d

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info .pytest_cache/
