# i. Overview
   This repo configures Flask to run on Docker with Postgres on development and production servers. Contains a static file with a static .txt file and a media folder containing user-uploaded media content via Nginx. Postgres is used to store a SQL database of user information, Gunicorn is used for the production environment. Nginx handles user-uploaded content to add it to the media folder.
![]()

# ii. Build Instructions
   Development servers are brought up with ``docker-compose build`` and ``docker-compose up`` commands. The former will use docker-compose.yml to build the container, and the latter will start the services. Production servers are implemented through ``docker-compose -f docker-compose.prod.yml up -d --build``, which will build the production containers through docker-compose.prod.yml and start the services. You can bring down the containers and volumes using ``docker-compose down -v``. 
