# Quick Hugging Face Authentication Guide

## Step 1: Get Your Access Token

1. Open browser and go to: https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: `todo-app-deployment`
4. Type: Select "Write" (important!)
5. Click "Generate token"
6. **COPY THE TOKEN** (you won't see it again!)

## Step 2: Login via CLI

Open your terminal and run:

```bash
huggingface-cli login
```

When prompted, paste your token and press Enter.

## Step 3: Tell me when done

Once you see "Login successful", just say "done" and I'll automatically:
- Upload the fixed files
- Monitor the deployment
- Test the backend
- Verify everything works

---

**Total time: 2 minutes**
