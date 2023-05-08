# Auth

Service for authorisation and authentication

### AUTH API
API for register, login, logout, update user, refresh token, get user sessions.
http://127.0.0.1:5000/auth/doc

### ROLES API
API for create, delete, update role and get all roles.  
http://127.0.0.1:5000/roles/doc

### USER ROLES API
API for get, put, delete user roles by user_id and role_id.
http://127.0.0.1:5000/users/doc

### Run server
Run
```
docker-compose up --build -d
```
### Create superuser
```
flask create_superuser 
```

## Local development
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
