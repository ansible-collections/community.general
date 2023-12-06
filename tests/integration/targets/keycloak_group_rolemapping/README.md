# `keycloak_group_rolemapping` Integration Tests

## Test Server

Prepare a development server, tested with Keycloak 22.0:

```sh
docker run -p 8080:8080 -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=password --rm quay.io/keycloak/keycloak start-dev
```

## Run Tests

```sh
ansible localhost --module-name include_role --args name=keycloak_group_rolemapping
```
