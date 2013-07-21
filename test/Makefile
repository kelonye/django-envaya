test:
	@./manage.py test --failfast

boot: core.sqlite3
	@python manage.py runserver 8005

core.sqlite3:
	@./manage.py syncdb --noinput
	@./manage.py loaddata core/fixtures/*

clean:
	@rm -rf core.sqlite3

.PHONY: clean