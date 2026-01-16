# GitHub Upload Guide

Your repository is ready to be pushed to GitHub! Follow these steps:

## Step 1: Create a GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Fill in the details:
   - **Repository name**: `vla-semantic-robustness-stress-test` (or your preferred name)
   - **Description**: "Research project to evaluate VLA model robustness to linguistic instruction variations"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click **"Create repository"**

## Step 2: Connect and Push

After creating the repository, GitHub will show you commands. Use these:

```bash
# Navigate to your project directory
cd "/Users/gilbertyum/Desktop/개별연구 svgr lab/VLA Semantic Robustness Stress Test"

# Add the remote repository (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Push to GitHub
git push -u origin main
```

## Alternative: Using SSH (if you have SSH keys set up)

```bash
git remote add origin git@github.com:YOUR_USERNAME/REPO_NAME.git
git push -u origin main
```

## What's Included

✅ All project files (683 files, ~1.2M lines)  
✅ Research manifesto and documentation  
✅ Model download script  
✅ SIMPLER environment  
✅ Installation guides  
✅ README.md  

## What's Excluded (via .gitignore)

❌ Model weights (`weights/` folder - too large for GitHub)  
❌ Log files  
❌ Python cache files  
❌ Virtual environments  
❌ IDE files  

## Note About Model Weights

The `weights/` folder containing OpenVLA-7B model files (~15GB) is excluded from git because:
- GitHub has a 100MB file size limit
- Large files should use Git LFS or be downloaded separately

Users can download the weights using:
```bash
python download_model.py
```

## Troubleshooting

If you get authentication errors:
- Use a Personal Access Token instead of password
- Or set up SSH keys for GitHub

If the push is too large:
- The repository is large but should be fine for GitHub
- If issues occur, consider using Git LFS for large files

