---
name: deploy
description: Build and deploy all services with verification
---

# Deploy

## Full Deploy
```bash
docker-compose build --no-cache
docker-compose up -d
```

## Frontend Only
```bash
docker-compose build --no-cache frontend
docker-compose up -d
```

## Backend Only
```bash
docker-compose build --no-cache backend
docker-compose up -d
```

## Verify
```bash
# Check all services are running
docker-compose ps

# Check backend started and migrations ran
docker-compose logs --tail 20 backend

# Test backend health
curl -s http://localhost:8000/api/health

# Test frontend serves
curl -s -o /dev/null -w "%{http_code}" http://localhost:80

# Test auth works
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@propertymanager.com","password":"Admin@123"}'
```

## Reset Database (Destructive)
```bash
docker-compose down -v
docker-compose up -d
```
Note: This deletes all data. Admin account will be recreated by migration.
