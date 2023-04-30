# Auth

Service for authorisation and authentication

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
