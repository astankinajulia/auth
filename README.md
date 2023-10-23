# Auth Service
___

Service for authorisation and authentication
## Features
* User register, login, logout, change user password or email
* Get active user sessions
* Access & Refresh JWT Tokens in cookies, user roles in access token
* Store active refresh tokens in Redis
* Roles API: Create, update, delete roles, get all roles
* User Roles API: add, delete role for user, get all user roles 
* Create superuser console command
* Check X-Request-Id in headers
* Google Authorization
## Tech Features
* Rate limit Token Bucket algorithm
* Jaeger Tracing
* Send errors to Sentry
## Run server
___
#### Add environment variables
In the folder `/app/config` create `.env` file (look `/app/config/.env.example` as example and `settings.py`
for other env params)
#### Add .crt and .key files
In the folder `/nginx` add `localhost.crt` and `localhost.key` files for ssl connection.
#### Run command
```
docker-compose up --build -d
```
#### Create superuser
Creates superuser role if it doesn't exist
```
flask create_superuser user_email@test.com user_pass
```

## Local development
___
### Run
```
docker-compose -f docker-compose.yml -f docker-compose-dev.yml up -d
```
### DB migrations
Create new migration version locally:
`alembic revision --autogenerate -m "create account table"`

Run migration (you don't need to do this, this step added in DOCKERFILE Entrypoint)
`docker-compose run app alembic upgrade head`

Downgrade migration
`docker-compose run app alembic downgrade <Revision ID>`


### Run tests
#### Add environments
In the folder `/tests` create `.env` file (look `/tests/.env.example` as example)

#### Functional tests 

Run in tests/functional 
```
docker-compose -f docker-compose-test.yml up -d
```

### Jaeger
UI link
http://127.0.0.1:16686/
## API docs
___
### AUTH API
API for register, login, logout, update user, refresh token, get user sessions.  
http://127.0.0.1:5000/auth/doc

### ROLES API
API for create, delete, update role and get all roles.   
http://127.0.0.1:5000/roles/doc

### USER ROLES API
API for get, put, delete user roles by user_id and role_id.  
http://127.0.0.1:5000/users/doc

### OAUTH2 API
API for google authentication.  
http://127.0.0.1:5000/oauth2/doc

### Miro docs
https://miro.com/app/board/uXjVMJU4K6w=/?share_link_id=718260316962

### async-api service
Service that uses Auth-service
https://github.com/astankinajulia/async_api

## Maintainer
___
Julia Astankina

## Technologies
___
- Flask
- SQL-Alchemy
- Alembic (migrations)
- Redis
- Docker
- Gunicorn, gevent
- Sentry
