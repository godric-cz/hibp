.PHONY: build-passwords
.ONESHELL:
build-passwords:
	@PYTHON=python3
	if type pypy3 > /dev/null; then
		PYTHON=pypy3
	fi
	echo "python interpreter: $$PYTHON"
	7z x pwned-passwords-sha1-ordered-by-hash-v7.7z -so | $$PYTHON build.py &&
	mv passwords-wip.bin passwords.bin &&
	mv index-wip.bin index.bin
