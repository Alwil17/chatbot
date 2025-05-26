# by default, we settle down in this region
AWS_REGION ?= eu-west-3
AWS_PROFILE ?= "esgis_profile"

.PHONY: clean .venv install build deploy-local deploy serve test test-endpoint format lint type-check quality

clean:
	rm -rf .venv
	rm -rf __pycache__
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf htmlcov

venv: clean
	python3 -m venv .venv

install:
	.venv/bin/pip install -r requirements.txt

build:
	sam build --use-container -t infrastructure/template.yaml

deploy-local:
	sam local start-api

deploy:
	@echo "Deploying to " ${env}
	# Extract env from the branch name

	sam deploy --resolve-s3 --template-file .aws-sam/build/template.yaml --stack-name multi-stack-${env} \
         --capabilities CAPABILITY_IAM --region ${AWS_REGION} --parameter-overrides EnvironmentName=${env} --no-fail-on-empty-changeset


serve:
	.venv/bin/fastapi dev src/main.py

test:
	@echo "Running tests..."
	.venv/bin/pytest

test-endpoint:
	@echo "Running endpoint tests..."
	aws cloudformation describe-stacks --stack-name multi-stack-${env} --region ${AWS_REGION} \
		--query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text | xargs -I {} curl -X GET {}

format:
	@echo "Formatting code with black..."
	.venv/bin/black src/ tests/

lint:
	@echo "Linting code with flake8..."
	.venv/bin/flake8 src/ tests/

type-check:
	@echo "Type checking with mypy..."
	.venv/bin/mypy src/ tests/

quality: format lint type-check
	@echo "All quality checks passed!"