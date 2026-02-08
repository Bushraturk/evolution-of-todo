# Contributing to Kubernetes Deployment

**Phase V: Local Kubernetes Deployment**

Thank you for your interest in contributing to the Todo Chatbot Kubernetes deployment! This guide will help you get started.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Contribution Guidelines](#contribution-guidelines)
5. [Testing Requirements](#testing-requirements)
6. [Documentation Standards](#documentation-standards)
7. [Pull Request Process](#pull-request-process)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Expected Behavior

- Be respectful and considerate
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Acknowledge different perspectives and experiences

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

1. **Required Software**:
   - Docker Desktop 4.53+
   - Minikube 1.30+
   - kubectl 1.28+
   - Helm 3.12+
   - Git

2. **Development Environment**:
   - Text editor or IDE (VS Code recommended)
   - Terminal/command line access
   - Basic Kubernetes knowledge

3. **Accounts**:
   - GitHub account
   - Neon PostgreSQL account (for testing)
   - Groq API key (for testing)

### Setting Up Development Environment

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/evolution-of-todo.git
cd evolution-of-todo

# 3. Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/evolution-of-todo.git

# 4. Create development branch
git checkout -b feature/your-feature-name

# 5. Set up environment
cp k8s/.env.example k8s/.env
# Edit k8s/.env with your credentials

# 6. Deploy to test your setup
./k8s/scripts/deploy-minikube.sh
```

---

## Development Workflow

### Branch Strategy

- **main**: Production-ready code
- **feature/***: New features or enhancements
- **fix/***: Bug fixes
- **docs/***: Documentation updates
- **refactor/***: Code refactoring

### Making Changes

```bash
# 1. Ensure you're on the latest main
git checkout main
git pull upstream main

# 2. Create feature branch
git checkout -b feature/improve-helm-chart

# 3. Make your changes
# - Edit files
# - Test changes
# - Update documentation

# 4. Test thoroughly
./k8s/scripts/deploy-minikube.sh
./k8s/scripts/run-all-validations.sh

# 5. Commit changes
git add .
git commit -m "feat: improve Helm chart configuration"

# 6. Push to your fork
git push origin feature/improve-helm-chart

# 7. Create pull request on GitHub
```

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(helm): add support for custom annotations

Add ability to specify custom annotations for deployments
and services via Helm values.

Closes #123
```

```
fix(scripts): correct image loading in deploy script

The deploy script was not properly loading images to Minikube
when using Docker Desktop on Windows.

Fixes #456
```

---

## Contribution Guidelines

### What to Contribute

**Welcome Contributions**:
- Bug fixes
- Documentation improvements
- Performance optimizations
- New features (discuss first in an issue)
- Test coverage improvements
- Script enhancements
- Example configurations

**Please Discuss First**:
- Major architectural changes
- Breaking changes
- New dependencies
- Significant refactoring

### Code Standards

#### Bash Scripts

```bash
#!/bin/bash

# Script description
# Purpose: What this script does

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="default"

# Functions
function_name() {
    local param=$1
    # Function body
}

# Main script logic
echo -e "${GREEN}Starting...${NC}"
```

**Best Practices**:
- Use `set -e` to exit on errors
- Add comments for complex logic
- Use functions for reusable code
- Provide usage information (`--help`)
- Use color coding for output
- Validate inputs
- Handle errors gracefully

#### Helm Templates

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-chatbot.fullname" . }}-backend
  labels:
    {{- include "todo-chatbot.labels" . | nindent 4 }}
    app.kubernetes.io/component: backend
spec:
  replicas: {{ .Values.backend.replicaCount }}
  # ... rest of template
```

**Best Practices**:
- Use template helpers for common patterns
- Validate required values
- Provide sensible defaults
- Document all values in values.yaml
- Use consistent naming conventions
- Follow Kubernetes best practices

#### Documentation

```markdown
# Title

Brief description of what this document covers.

## Section

Content with examples:

\`\`\`bash
# Example command
kubectl get pods
\`\`\`

**Expected Output**:
\`\`\`
NAME                        READY   STATUS    RESTARTS   AGE
backend-7d8f9c5b-xk2p9      1/1     Running   0          2m
\`\`\`
```

**Best Practices**:
- Use clear, concise language
- Include examples for all procedures
- Show expected outputs
- Link to related documentation
- Keep formatting consistent
- Update table of contents

---

## Testing Requirements

### Before Submitting PR

All contributions must pass these tests:

#### 1. Deployment Test

```bash
# Clean environment
./k8s/scripts/cleanup.sh --all

# Fresh deployment
./k8s/scripts/deploy-minikube.sh

# Verify success
./k8s/scripts/verify-deployment.sh
```

**Expected**: All pods running, health checks passing

#### 2. Validation Tests

```bash
# Run all validations
./k8s/scripts/run-all-validations.sh

# Expected: Score ≥ 80/100
```

#### 3. Helm Chart Validation

```bash
# Lint chart
helm lint k8s/helm-charts/todo-chatbot/

# Template validation
helm template todo-chatbot k8s/helm-charts/todo-chatbot/ --debug

# Expected: No errors
```

#### 4. Script Testing

```bash
# Test all scripts
./k8s/scripts/build-images.sh
./k8s/scripts/load-images.sh
./k8s/scripts/scale-deployment.sh --component backend --replicas 2
./k8s/scripts/update-deployment.sh --component backend --tag latest
./k8s/scripts/rollback-deployment.sh --component backend

# Expected: All scripts execute successfully
```

#### 5. Documentation Review

- [ ] All new features documented
- [ ] README.md updated if needed
- [ ] Examples provided
- [ ] Links working
- [ ] Spelling and grammar checked

### Test Checklist

Before submitting PR, verify:

- [ ] Code follows style guidelines
- [ ] All scripts are executable (`chmod +x`)
- [ ] Helm chart validates successfully
- [ ] Deployment works from scratch
- [ ] All validation tests pass
- [ ] Documentation is updated
- [ ] Commit messages follow convention
- [ ] No secrets or credentials in code
- [ ] Changes are backwards compatible (or breaking changes documented)

---

## Documentation Standards

### File Organization

```
k8s/
├── docs/
│   ├── DEPLOYMENT.md          # How to deploy
│   ├── ARCHITECTURE.md        # System design
│   ├── LIFECYCLE_MANAGEMENT.md # Operations
│   ├── TROUBLESHOOTING.md     # Problem solving
│   ├── PRODUCTION_READINESS.md # Validation
│   └── *.md                   # Other guides
├── scripts/
│   └── *.sh                   # Automation scripts
└── README.md                  # Overview
```

### Documentation Requirements

**Every new feature must include**:
1. **README.md update**: Add to relevant section
2. **Usage examples**: Show how to use the feature
3. **Troubleshooting**: Common issues and solutions
4. **Architecture docs**: If architectural changes

**Documentation Style**:
- Use present tense ("Deploy the application" not "Deploys")
- Use active voice ("Run the script" not "The script is run")
- Be concise but complete
- Include code examples
- Show expected outputs
- Link to related docs

### Example Documentation

```markdown
## Feature Name

Brief description of what this feature does.

### Usage

\`\`\`bash
# Basic usage
./k8s/scripts/feature-script.sh --option value

# Advanced usage
./k8s/scripts/feature-script.sh --option1 value1 --option2 value2
\`\`\`

### Options

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `--option` | What it does | `default` | Yes |

### Examples

\`\`\`bash
# Example 1: Common use case
./k8s/scripts/feature-script.sh --option value

# Example 2: Advanced use case
./k8s/scripts/feature-script.sh --option1 value1 --option2 value2
\`\`\`

### Troubleshooting

**Issue**: Common problem

**Solution**: How to fix it
\`\`\`bash
# Fix command
kubectl fix-command
\`\`\`
```

---

## Pull Request Process

### Creating a Pull Request

1. **Ensure all tests pass** (see Testing Requirements)

2. **Update documentation**:
   - README.md (if needed)
   - Relevant docs in docs/
   - Inline code comments

3. **Write clear PR description**:
   ```markdown
   ## Description
   Brief description of changes

   ## Motivation
   Why this change is needed

   ## Changes
   - Change 1
   - Change 2

   ## Testing
   How you tested the changes

   ## Checklist
   - [ ] Tests pass
   - [ ] Documentation updated
   - [ ] Follows style guidelines
   - [ ] No breaking changes (or documented)
   ```

4. **Submit PR** to main repository

### PR Review Process

1. **Automated Checks**: CI/CD runs tests
2. **Code Review**: Maintainers review code
3. **Feedback**: Address review comments
4. **Approval**: At least one maintainer approval required
5. **Merge**: Maintainer merges PR

### After PR is Merged

1. **Delete branch**: Clean up your feature branch
2. **Update local**: Pull latest main
3. **Celebrate**: Your contribution is live! 🎉

---

## Getting Help

### Resources

- **Documentation**: Check docs/ directory
- **Issues**: Search existing issues on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Troubleshooting**: See TROUBLESHOOTING.md

### Asking Questions

When asking for help:

1. **Search first**: Check if question already answered
2. **Be specific**: Describe what you're trying to do
3. **Provide context**: Include relevant code, commands, outputs
4. **Show what you tried**: Demonstrate your debugging efforts

**Good Question**:
```
I'm trying to deploy with custom resource limits but getting an error.

Command:
helm install todo-chatbot k8s/helm-charts/todo-chatbot/ \
  --set backend.resources.limits.memory=2Gi

Error:
Error: UPGRADE FAILED: failed to create resource

I've tried:
- Checking Helm chart syntax
- Validating with helm lint
- Checking Minikube resources

Minikube has 8GB RAM allocated. What am I missing?
```

**Poor Question**:
```
Deployment doesn't work. Help!
```

---

## Recognition

Contributors will be:
- Listed in project contributors
- Mentioned in release notes (for significant contributions)
- Credited in documentation (for major features)

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

## Questions?

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check docs/ directory first

---

**Thank you for contributing to Todo Chatbot Kubernetes deployment!**

Your contributions help make this project better for everyone.

---

**Last Updated**: 2026-02-08
**Phase**: V - Local Kubernetes Deployment
**Status**: Production Ready
