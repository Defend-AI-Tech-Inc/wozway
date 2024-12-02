.PHONY:	all wauzeway adminsvc publish run stop

all:	wauzeway \
		adminsvc

publish:	publish_wauzeway \
			publish_adminsvc

wauzeway:
	cd apisix;\
	make

adminsvc:
	cd adminsvc;\
	make

publish_wauzeway:
	cd apisix;\
	make publish

publish_adminsvc:
	cd adminsvc;\
	make publish

run:
	docker compose up

stop:
	docker compose down -v
