# Fixing GitHub Push HTTP 400 Error

## The Problem

You're getting an HTTP 400 error when pushing to GitHub. This is usually caused by:

1. **Authentication issues** - GitHub no longer accepts passwords, requires Personal Access Token
2. **Large files** - Some binary files in SimplerEnv might be causing issues
3. **Network/timeout** - Large repository size (135MB) might timeout

## Solution 1: Use Personal Access Token (Most Likely Fix)

GitHub requires a Personal Access Token instead of password:

1. **Create a Personal Access Token:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Give it a name (e.g., "VLA Project")
   - Select scopes: `repo` (full control of private repositories)
   - Click "Generate token"
   - **Copy the token immediately** (you won't see it again!)

2. **Push using the token:**
   ```bash
   git push -u origin main
   ```
   When prompted:
   - Username: `SeoyoonYum`
   - Password: **Paste your Personal Access Token** (not your GitHub password)

## Solution 2: Use SSH Instead of HTTPS

If you have SSH keys set up:

```bash
git remote set-url origin git@github.com:SeoyoonYum/VLA-Semantic-Robustness-Test.git
git push -u origin main
```

## Solution 3: Increase Git Buffer Size

The repository is large (135MB). Try increasing the buffer:

```bash
git config http.postBuffer 524288000  # 500MB
git push -u origin main
```

## Solution 4: Push in Smaller Chunks

If still failing, we can exclude some large binary files temporarily:

```bash
# Add large .glb and .dae files to .gitignore temporarily
echo "*.glb" >> .gitignore
echo "*.dae" >> .gitignore
git add .gitignore
git commit -m "Exclude large binary files"
git push -u origin main
```

## Verify Push Success

After pushing, verify:
```bash
git ls-remote origin
```

You should see your commits listed.

## Most Common Fix

**99% of the time, it's Solution 1** - you need to use a Personal Access Token instead of your password.

