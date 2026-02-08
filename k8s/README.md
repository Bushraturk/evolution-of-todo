# Kubernetes Deployment for Todo Chatbot

This directory contains all Kubernetes deployment artifacts for the Todo Chatbot application (Phase V).

## 📁 Directory Structure

```
k8s/
├── dockerfiles/          # Docker multi-stage build files
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
├── helm-charts/          # Helm chart for Kubernetes deployment
│   └── todo-chatbot/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-dev.yaml
│       ├── values-prod.yaml
│       └── templates/
├── scripts/              # Automation scripts
│   ├── build-images.sh
│   ├── deploy-minikube.sh
│   ├── validate-chart.sh
│   └── cleanup.sh
└── docs/                 # Documentation
    ├── DEPLOYMENT.md
    ├── TROUBLESHOOTING.md
    └── AI_TOOLS_GUIDE.md
```

## 🚀 Quick Start

### Prerequisites

- Docker Desktop 4.53+ (with Gordon AI optional)
- Minikube 1.30+
- kubectl 1.28+
- Helm 3.12+
- kubectl-ai (optional)
- Kagent (optional)

### Deploy to Minikube

```bash
# 1. Start Minikube
minikube start --memory=4096 --cpus=2

# 2. Build and load images
cd k8s
./scripts/build-images.sh
./scripts/load-images.sh

# 3. Create secrets
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="your-db-url" \
  --from-literal=GROQ_API_KEY="your-api-key" \
  --from-literal=JWT_SECRET="your-jwt-secret"

# 4. Deploy with Helm
helm install todo-chatbot ./helm-charts/todo-chatbot/

# 5. Access application
minikube tunnel  # In separate terminal
# Visit http://localhost
```

## 📖 Documentation

- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)**: Complete deployment guide
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)**: Common issues and solutions
- **[AI_TOOLS_GUIDE.md](docs/AI_TOOLS_GUIDE.md)**: Using Gordon, kubectl-ai, Kagent

## 🎯 Features

- **Multi-stage Docker builds**: Optimized images (<500MB backend, <200MB frontend)
- **Helm charts**: Declarative Kubernetes deployment management
- **Health checks**: Liveness and readiness probes for all pods
- **Resource limits**: CPU and memory constraints for efficient scheduling
- **Security**: Non-root users, dropped capabilities
- **AI-assisted operations**: Gordon, kubectl-ai, Kagent integration
- **Rolling updates**: Zero-downtime deployments
- **Horizontal scaling**: Scale backend pods on demand

## 🔧 Development

### Build Images Locally

```bash
# Backend
docker build -t todo-backend:latest \
  -f dockerfiles/backend.Dockerfile \
  ../phase4-chatbot/backend/

# Frontend
docker build -t todo-frontend:latest \
  -f dockerfiles/frontend.Dockerfile \
  ../phase4-chatbot/frontend/
```

### Test Images Locally

```bash
# Backend
docker run -p 8000:8000 --env-file .env todo-backend:latest

# Frontend
docker run -p 3000:3000 --env-file .env.local todo-frontend:latest
```

### Validate Helm Chart

```bash
# Lint chart
helm lint ./helm-charts/todo-chatbot/

# Dry-run installation
helm install todo-chatbot ./helm-charts/todo-chatbot/ --dry-run --debug

# Template rendering
helm template todo-chatbot ./helm-charts/todo-chatbot/
```

## 🧪 Testing

### Verify Deployment

```bash
# Check pod status
kubectl get pods

# Check services
kubectl get services

# Check logs
kubectl logs -l app=todo-chatbot,component=backend
kubectl logs -l app=todo-chatbot,component=frontend

# Test health checks
kubectl exec -it deployment/backend -- curl http://localhost:8000/health
kubectl exec -it deployment/frontend -- curl http://localhost:3000/api/health
```

### Scale Application

```bash
# Scale backend
kubectl scale deployment backend --replicas=3

# Scale frontend
kubectl scale deployment frontend --replicas=2

# Verify scaling
kubectl get pods
```

### Rolling Update

```bash
# Update image tag
helm upgrade todo-chatbot ./helm-charts/todo-chatbot/ \
  --set backend.image.tag=v1.0.1

# Watch rollout
kubectl rollout status deployment/backend

# Rollback if needed
helm rollback todo-chatbot
```

## 🧹 Cleanup

```bash
# Uninstall Helm chart
helm uninstall todo-chatbot

# Delete secrets
kubectl delete secret todo-secrets

# Stop Minikube
minikube stop

# Delete Minikube cluster (optional)
minikube delete
```

## 📊 Resource Requirements

### Minimum

- **CPU**: 2 cores
- **RAM**: 4GB
- **Disk**: 20GB free space

### Recommended

- **CPU**: 4 cores
- **RAM**: 8GB
- **Disk**: 40GB free space

## 🔐 Security

- All containers run as non-root users
- Secrets stored in Kubernetes Secrets (not in code)
- No hardcoded credentials in Dockerfiles or Helm charts
- Minimal base images to reduce attack surface
- Capabilities dropped for enhanced security

## 📈 Performance

- **Docker build time**: <5 minutes
- **Deployment time**: <3 minutes
- **Pod startup time**: <30 seconds
- **Health check response**: <2 seconds

## 🆘 Support

For issues and troubleshooting:

1. Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Review pod logs: `kubectl logs <pod-name>`
3. Check pod events: `kubectl describe pod <pod-name>`
4. Verify secrets: `kubectl get secrets`

## 📝 License

MIT License - See main project README for details

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to Kubernetes deployment artifacts.

---

**Phase**: V - Local Kubernetes Deployment
**Status**: Implementation in progress
**Next Phase**: VI - Cloud Kubernetes Deployment
