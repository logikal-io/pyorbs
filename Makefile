.PHONY: tests clean_docs docs clean_dist dist clean

tests:
	pytest

clean_docs:
	rm -rf docs/_build

docs: clean_docs
	cd docs && make

clean_dist:
	rm -rf build dist *.egg-info

dist: clean_dist
	./setup.py sdist bdist_wheel
	twine check dist/*

clean: clean_docs clean_dist
