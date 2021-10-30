The integration test can be performed as follows:

```
# 1. Start docker-compose:
docker-compose -f tests/integration/targets/keycloak_client/docker-compose.yml stop
docker-compose -f tests/integration/targets/keycloak_client/docker-compose.yml rm -f -v
docker-compose -f tests/integration/targets/keycloak_client/docker-compose.yml up -d

# 2. Run the integration tests:
ansible-test integration keycloak_client --allow-unsupported -v
```
