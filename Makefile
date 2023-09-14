.PHONY: default
default: sdist bdist_wheel

.PHONY: sdist
sdist:
	python3 ./setup.py sdist

.PHONY: bdist_wheel
bdist_wheel:
	python3 ./setup.py bdist_wheel

.PHONY: dist
dist: sdist bdist_wheel

clean: cleandist
	rm -rf build 
	rm -rf doc/build
	rm -rf *.egg-info
	rm -rf .eggs

.PHONY: distclean
distclean: clean
	rm -rf .tox
	rm -rf .pytest_cache
	find -type d -name __pycache__ | xargs rm -rf 

.PHONY: cleandist
cleandist:
	rm -rf dist

.PHONY: twine
twine: cleandist sdist bdist_wheel
	twine upload dist/*

.PHONY: stwine
stwine: cleandist sdist bdist_wheel
	# Place your key-id after -i
	twine upload -s -i ACDFB08FDC962044D87FF00B512839863D487A87 dist/*

.PHONY: docs
docs:
	tox -e docs

.PHONY: tox
tox:
	tox -e py310
