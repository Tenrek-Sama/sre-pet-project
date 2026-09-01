
# SRE Pet Project: отказоустойчивый веб-сервис

Полный цикл SRE-инфраструктуры: от кода до мониторинга.

## Стек

- **FastAPI** + **PostgreSQL** — приложение
- **Docker** — контейнеризация
- **Kubernetes (k3s)** — оркестрация
- **Terraform/OpenTofu** — инфраструктура как код (KVM)
- **Ansible** — конфигурация серверов
- **GitHub Actions** — CI/CD
- **Prometheus** + **Grafana** — мониторинг

## Структура

| Папка | Назначение |
|-------|------------|
| `app/` | Код FastAPI-приложения |
| `k8s/` | Kubernetes-манифесты |
| `ansible/` | Playbook для настройки VM |
| `tofu/` | Terraform-конфигурация для KVM |
| `scripts/` | Python-скрипты автоматизации |
| `.github/workflows/` | CI/CD пайплайн |

## Развёртывание

### 1. Локально (Docker Compose)
```bash
docker compose up -d --build

### 2. На VM через Terraform + Ansible
cd tofu && tofu apply
cd ../ansible && ansible-playbook playbook.yml

### 3. В Kubernetes
kubectl apply -f k8s/

## CI/CD

Пайплайн в GitHub Actions:

    Сборка и тест при пуше в main

    Деплой в k3s через self-hosted runner

Мониторинг

Prometheus + Grafana на портах 30900/30300.
Метрики приложения: /metrics (Prometheus format).
