The integration test can be performed as follows:

```
# 1. Start docker-compose:
docker-compose -f tests/integration/targets/keycloak_role/docker-compose.yml stop
docker-compose -f tests/integration/targets/keycloak_role/docker-compose.yml rm -f -v
docker-compose -f tests/integration/targets/keycloak_role/docker-compose.yml up -d

# 2. Wait for keycloak to finish starting (see http://localhost:8080/auth/)
sleep 30

# 3. Run the integration tests:
ansible-test integration keycloak_role --allow-unsupported -v
```
