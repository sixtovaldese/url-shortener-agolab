# Despliegue

## Pipeline CI/CD

El despliegue es automático mediante GitHub Actions:

1. Lint (ruff)
2. Security scan (bandit, pip-audit)
3. Tests (22 tests)
4. Build Docker image
5. Deploy automático a servidor

## Secrets Requeridos

- `VPS_HOST`
- `VPS_USER`
- `VPS_SSH_KEY`
- `PRODUCTION_ENV`

## Proceso

Cada push a `main` dispara el pipeline. Si todos los tests pasan, se despliega automáticamente.
