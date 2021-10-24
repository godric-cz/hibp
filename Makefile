SHELL := /bin/bash

.PHONY: build-passwords
.ONESHELL:
build-passwords:
	@cd data
	PYTHON=python3
	if type pypy3 > /dev/null; then
		PYTHON=pypy3
	fi
	echo "python interpreter: $$PYTHON"
	if [ ! -f pwned-passwords-sha1-ordered-by-hash-v7.7z ]; then
		echo "password archive not found, exiting" && exit
	fi
	7z x pwned-passwords-sha1-ordered-by-hash-v7.7z -so | $$PYTHON ../build.py &&
	mv passwords-wip.bin passwords.bin &&
	mv index-wip.bin index.bin

.venv: requirements.txt
	rm -rf .venv
	python3 -m venv .venv
	source .venv/bin/activate && pip install -r requirements.txt

.PHONY: run
run: .venv
	source .venv/bin/activate && uvicorn main:app --reload
