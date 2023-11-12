update_conteiners:
	sudo docker-compose stop && \
	sudo docker-compose rm -f && \
	sudo docker volume rm infra_frontend_value && \
	sudo docker-compose pull && \
	sudo docker-compose up -d && \
	sudo docker-compose exec -T backend python manage.py makemigrations && \
	sudo docker-compose exec -T backend python manage.py migrate && \
	sudo docker-compose exec -T backend python manage.py collectstatic --no-input && \
	sudo docker-compose exec -T backend python manage.py compilemessages && \
	sudo docker-compose restart
