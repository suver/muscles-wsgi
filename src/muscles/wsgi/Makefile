# Makefile

start:
	docker-compose up -d
	docker exec -it butkoinfo_core_1 bash


stop:
	docker-compose up -d
	docker exec -it butkoinfo-core-1 bash


console:
	docker exec -it butkoinfo_core_1 bash


logs:
	docker-compose logs


develop:
	#docker exec -it butkoinfo_core_1 pipenv install
	pipenv run python setup.py develop
	pipenv install


