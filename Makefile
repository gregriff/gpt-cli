
# turns requirements.in into the lockfile requirements.txt
# requires a venv to be active in order to use `pip-compile`
# this should only be used by a developer updating the lockfile
lock:
	./scripts/activate_venv.sh && \
	python -m pip install -U pip pip-tools && \
	pip-compile -U --generate-hashes --output-file requirements.txt requirements.in


# install python packages from lockfile
.PHONY: install
install:
	python -m pip install -U pip && \
	python -m pip install --require-hashes -r requirements.txt


run:
	python src/gpt-cli/main.py

# run the cheapest model available for debugging
run-test:
	python src/gpt-cli/main.py "claude-3-haiku-20240307"

format:
	python -m black -t py312 .