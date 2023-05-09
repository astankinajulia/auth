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
## Run server
___
#### Add environment variables
In the folder `/app/config` create `.env` file (look `/app/config/.env.example` as example and `settings.py`
for other env params)
#### Run command
```
docker-compose up --build -d
```
#### Create superuser
```
flask create_superuser 
```

## Local development
___
### Run
```
docker-compose -f docker-compose.yml -f docker-compose-dev.yml up -d
```
### DB migrations
Create new migration version locally:
`alembic revision -m "create account table"`

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