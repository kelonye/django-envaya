test:
	@make --no-print-directory -C test

example:
	@make boot --no-print-directory -C test

deps:
	@pip install -r requirements.txt

publish:
	@python setup.py sdist upload

clean:
	@rm -rf build dist envaya.egg-info $(shell find -name ='*.pyc')

.PHONY: clean publish deps example test