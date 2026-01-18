# Updating Repository on SSH Server

If your SSH server has an older version, follow these steps:

## Step 1: Check Current Status

```bash
# Check what branch you're on
git branch

# Check if you have uncommitted changes
git status

# Check what commit you're on
git log --oneline -5
```

## Step 2: Pull Latest Changes

```bash
# Make sure you're on the main branch
git checkout main

# Pull the latest changes from GitHub
git pull origin main
```

## Step 3: If You Have Local Changes

If you have uncommitted local changes that conflict:

```bash
# Option 1: Stash your changes, pull, then reapply
git stash
git pull origin main
git stash pop

# Option 2: Commit your changes first
git add .
git commit -m "Local changes"
git pull origin main

# Option 3: Discard local changes (CAREFUL - you'll lose them!)
git reset --hard origin/main
```

## Step 4: Verify You Have Latest Files

```bash
# Check if new files exist
ls -la setup_ssh_env.sh SSH_SETUP_GUIDE.md

# Check the latest commit
git log --oneline -1
```

You should see commit: "Add SSH environment setup guide and script"

## Step 5: Force Update (if pull doesn't work)

If `git pull` doesn't update files:

```bash
# Fetch latest from GitHub
git fetch origin

# Reset to match GitHub exactly
git reset --hard origin/main

# Clean any untracked files (optional)
git clean -fd
```

## Troubleshooting

### "Your branch is behind"
```bash
git pull origin main
```

### "Your branch has diverged"
```bash
# See what's different
git log HEAD..origin/main

# Force update to match GitHub
git reset --hard origin/main
```

### "Permission denied" or authentication issues
```bash
# Check remote URL
git remote -v

# If using HTTPS, you may need to re-authenticate
# Or switch to SSH if you have keys set up
git remote set-url origin git@github.com:SeoyoonYum/VLA-Semantic-Robustness-Test.git
```

## Quick One-Liner Update

If you just want to force everything to match GitHub:

```bash
git fetch origin && git reset --hard origin/main && git clean -fd
```

**Warning:** This will discard any local uncommitted changes!

