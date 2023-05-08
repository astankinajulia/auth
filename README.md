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
Run
```
docker-compose up --build -d
```
### Create superuser
```
flask create_superuser 
```

## Local development
___
Run
```
docker-compose -f docker-compose.yml -f docker-compose-dev.yml up -d
```

### Run tests
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