# Git Commands Reference & Practice Exercises

## 📋 Quick Command Reference

### Initialize & Clone
```bash
git init                          # Start a new repo
git clone <url>                   # Copy a repo
git clone --depth 1 <url>        # Shallow clone (faster for large repos)
```

### Configuration
```bash
git config --global user.name "Name"
git config --global user.email "email@example.com"
git config --list                 # View all config
```

### Checking Status
```bash
git status                        # Current state
git log                           # Commit history
git log --oneline -10             # Last 10 commits (compact)
git diff                          # Unstaged changes
git diff --staged                 # Staged changes
git diff main feature/branch      # Compare branches
```

### Staging & Committing
```bash
git add .                         # Stage all changes
git add file.py                   # Stage specific file
git add -p                        # Interactive stage (by hunk)
git commit -m "message"           # Commit with message
git commit --amend                # Modify last commit
git commit -am "msg"              # Stage + commit tracked files
```

### Branching
```bash
git branch                        # List branches
git branch -a                     # All branches (local + remote)
git branch new-branch             # Create branch
git switch -c new-branch          # Create and switch (Git 2.23+)
git checkout -b new-branch        # Create and switch (older)
git switch branch-name            # Switch branch (Git 2.23+)
git checkout branch-name          # Switch branch (older)
git branch -d branch              # Delete branch
git branch -D branch              # Force delete
git branch -m old new             # Rename branch
```

### Merging & Rebasing
```bash
git merge branch-name             # Merge branch
git merge --no-ff branch          # Merge, force merge commit
git merge --squash branch         # Combine commits, then merge
git merge --abort                 # Cancel merge
git rebase main                   # Rebase onto main
git rebase -i HEAD~5              # Interactive rebase (last 5 commits)
```

### Remote Operations
```bash
git remote -v                     # List remotes with URLs
git remote add origin <url>       # Add remote
git remote set-url origin <url>   # Change remote URL
git remote remove origin          # Remove remote
git push origin main              # Push to remote
git push -u origin main           # Push and set upstream
git push --all                    # Push all branches
git push origin --tags            # Push tags
git pull origin main              # Fetch + merge
git fetch origin                  # Fetch only (no merge)
git fetch upstream                # Fetch from upstream remote
```

### Undoing Changes
```bash
git restore file.py               # Discard changes (Git 2.23+)
git checkout -- file.py           # Discard changes (older)
git restore --staged file.py      # Unstage (Git 2.23+)
git reset HEAD file.py            # Unstage (older)
git reset --soft HEAD~1           # Undo commit, keep changes staged
git reset --mixed HEAD~1          # Undo commit, keep changes unstaged
git reset --hard HEAD~1           # Undo commit, discard changes
git revert abc123                 # Create commit that undoes abc123
```

### Stashing
```bash
git stash                         # Save work temporarily
git stash list                    # View all stashes
git stash apply                   # Apply most recent stash
git stash apply stash@{0}         # Apply specific stash
git stash pop                     # Apply and delete stash
git stash drop stash@{0}          # Delete stash
git stash branch feature          # Create branch from stash
```

### Tags
```bash
git tag v1.0                      # Create lightweight tag
git tag -a v1.0 -m "message"      # Create annotated tag
git tag                           # List tags
git show v1.0                     # Show tag details
git push origin --tags            # Push all tags
git push origin v1.0              # Push specific tag
git tag -d v1.0                   # Delete local tag
git push origin --delete v1.0     # Delete remote tag
```

### Searching & Inspection
```bash
git log --grep="keyword"          # Search commit messages
git log --author="Name"           # Filter by author
git log --since="2 weeks ago"     # Time filter
git blame file.py                 # See who changed each line
git show abc123                   # Show specific commit
git reflog                        # Show all reference changes (recovery)
```

---

## 🎯 Practice Exercises

### Exercise 1: Basic Workflow

**Objective:** Learn init, add, commit, and log.

```bash
# 1. Create a new folder and initialize Git
mkdir git-practice
cd git-practice
git init

# 2. Create a file
echo "Hello World" > hello.txt

# 3. Check status
git status

# 4. Stage the file
git add hello.txt

# 5. Check status again (notice it's now staged)
git status

# 6. Commit
git commit -m "Initial commit: add hello.txt"

# 7. View commit log
git log --oneline

# 8. Modify the file
echo "Hello Git" > hello.txt

# 9. View changes
git diff

# 10. Commit again
git add . && git commit -m "Update hello.txt greeting"

# 11. View full history
git log --oneline
git log  # detailed view
```

**Interview Q:** *"What's the difference between `git status` before and after `git add`?"*

---

### Exercise 2: Branching & Merging

**Objective:** Create branches, make changes, and merge.

```bash
# 1. Create a feature branch
git switch -c feature/greeting

# 2. Make changes
echo "Feature: Personalized greeting" > feature.txt
git add . && git commit -m "Add personalized greeting feature"

# 3. Create another branch from main
git switch main
git switch -c feature/logging

# 4. Make different changes
echo "Feature: Logging system" > logging.txt
git add . && git commit -m "Add logging feature"

# 5. Check branches
git branch

# 6. Merge feature/greeting into main
git switch main
git merge feature/greeting

# 7. Merge feature/logging into main
git merge feature/logging

# 8. View merged history
git log --oneline

# 9. Delete branches
git branch -d feature/greeting
git branch -d feature/logging
```

**Interview Q:** *"What does a merge commit look like in the log?"*

---

### Exercise 3: Merge Conflicts

**Objective:** Create and resolve a merge conflict.

```bash
# 1. Create initial commit on main
git switch -c conflict-test
echo "Line 1" > file.txt
git add . && git commit -m "Add file.txt"

# 2. Create feature branch and modify line
git switch -c feature/modify-line
sed -i 's/Line 1/Line 1 - Feature Version/' file.txt
git add . && git commit -m "Modify line (feature version)"

# 3. Switch back to main and modify the same line differently
git switch main
sed -i 's/Line 1/Line 1 - Main Version/' file.txt
git add . && git commit -m "Modify line (main version)"

# 4. Try to merge (will conflict)
git merge feature/modify-line

# You'll see:
# CONFLICT (content): Merge conflict in file.txt
# Automatic merge failed; fix conflicts and then commit the result.

# 5. View the conflicted file
cat file.txt

# 6. Resolve manually (pick one version or combine)
# Edit to: Line 1 - Both Versions
echo "Line 1 - Main Version\nLine 1 - Feature Version" > file.txt

# 7. Stage and commit
git add file.txt
git commit -m "Resolve merge conflict in file.txt"

# 8. Verify
git log --oneline
```

**Interview Q:** *"How would you abort this merge if you changed your mind?"*

---

### Exercise 4: Undoing Commits

**Objective:** Practice `reset` and `revert`.

```bash
# 1. Create 3 commits
echo "Commit 1" > file1.txt
git add . && git commit -m "Commit 1"

echo "Commit 2" > file2.txt
git add . && git commit -m "Commit 2"

echo "Commit 3" > file3.txt
git add . && git commit -m "Commit 3"

# 2. View history
git log --oneline

# 3. Undo last commit (keep changes)
git reset --soft HEAD~1
git status  # changes are staged

# 4. Re-commit with better message
git commit -m "Commits 2 and 3 combined"

# 5. Undo that commit (keep changes, unstaged)
git reset --mixed HEAD~1
git status  # changes are unstaged

# 6. Undo multiple commits
git reset --hard HEAD~2  # go back 2 commits, lose all changes

# 7. Use reflog to recover
git reflog
git reset --hard abc123  # restore using reflog
```

**Interview Q:** *"When would you use `reset --soft` vs `reset --hard`?"*

---

### Exercise 5: Interactive Rebase

**Objective:** Squash multiple commits.

```bash
# 1. Create messy commit history
echo "v1" > app.py
git add . && git commit -m "Initial app"

echo "v2" >> app.py
git add . && git commit -m "WIP"

echo "v3" >> app.py
git add . && git commit -m "Fix bug"

echo "v4" >> app.py
git add . && git commit -m "Typo"

echo "v5" >> app.py
git add . && git commit -m "Final"

# 2. View messy history
git log --oneline

# 3. Interactive rebase on last 5 commits
git rebase -i HEAD~5

# 4. In editor, change to:
# pick abc123 Initial app
# squash def456 WIP
# squash ghi789 Fix bug
# squash jkl012 Typo
# squash mno345 Final

# 5. Save, editor opens for commit message
# Type: "Complete app implementation"

# 6. Verify clean history
git log --oneline
```

**Interview Q:** *"Why would you squash commits before pushing to main?"*

---

### Exercise 6: Stashing

**Objective:** Practice stashing for context switching.

```bash
# 1. Start work on feature
echo "New feature code" > feature.py
git add feature.py
echo "WIP" >> feature.py

# 2. You're not done, but need to switch branches urgently
git status  # modified: feature.py

# 3. Stash your work
git stash

# 4. Verify stash
git stash list
git status  # clean!

# 5. Do urgent work
echo "Hotfix" > hotfix.py
git add . && git commit -m "Urgent hotfix"

# 6. Resume your feature work
git stash pop
git status  # feature.py is back with WIP

# 7. Continue and commit
git add . && git commit -m "Complete feature"
```

**Interview Q:** *"What's the difference between `git stash apply` and `git stash pop`?"*

---

### Exercise 7: Remote Operations

**Objective:** Practice push, pull, fetch.

```bash
# 1. Add a remote (you'll need an actual GitHub repo for this)
git remote add origin https://github.com/user/repo.git

# 2. View remote
git remote -v

# 3. Push to remote
git push -u origin main

# 4. Simulate colleague's change (on GitHub)
# (For practice, create a new branch on GitHub via web)

# 5. Fetch updates
git fetch origin

# 6. See what changed
git log --oneline origin/main
git diff main origin/main

# 7. Pull and merge
git pull origin main

# 8. Push your changes
git push origin main
```

**Interview Q:** *"Why would you fetch before pull?"*

---

### Exercise 8: Cherry-Pick

**Objective:** Copy a specific commit from another branch.

```bash
# 1. Create two branches with different commits
git switch -c feature-a
echo "Feature A" > a.txt
git add . && git commit -m "Feature A"

git switch main
git switch -c feature-b
echo "Feature B" > b.txt
git add . && git commit -m "Feature B"

# 2. Switch to main
git switch main

# 3. Copy only the "Feature A" commit from feature-a
git cherry-pick feature-a

# 4. Verify main now has Feature A's commit
git log --oneline
cat a.txt  # exists!
cat b.txt  # doesn't exist
```

**Interview Q:** *"When is cherry-pick useful?"*

---

## 🔍 Debugging & Troubleshooting

### "I committed on the wrong branch"

```bash
# Branch A (wrong place)
git log --oneline  # see your commits

# Get the commit hash: abc123
git reset --hard HEAD~1  # undo the commit

# Go to correct branch
git switch correct-branch

# Apply the commit
git cherry-pick abc123
```

### "I deleted a file and want to recover it"

```bash
# Find which commit deleted it
git log --oneline -- deleted-file.py

# Restore from before the deletion
git show abc123^:deleted-file.py > deleted-file.py
git add deleted-file.py && git commit -m "Restore deleted-file.py"
```

### "I need to undo a pushed commit"

```bash
# SAFE: use revert
git revert abc123
git push origin main

# DANGEROUS (only if no one else pulled):
git reset --hard HEAD~1
git push --force-with-lease
```

### "I committed sensitive info (password/key)"

```bash
# Remove file from all history
git filter-branch --tree-filter 'rm -f sensitive-file' HEAD

# Or use git-filter-repo (better, modern approach)
pip install git-filter-repo
git filter-repo --path sensitive-file --invert-paths

# Force push
git push --force-with-lease
```

---

## 🏆 Interview Prep Checklist

- [ ] Understand the three Git states (working, staging, committed)
- [ ] Know basic commands: add, commit, push, pull, merge
- [ ] Explain branching strategy (Git Flow, GitHub Flow)
- [ ] Difference between merge and rebase
- [ ] Difference between reset and revert
- [ ] Difference between fetch and pull
- [ ] How to resolve merge conflicts
- [ ] How to recover deleted commits (reflog)
- [ ] Stashing use cases
- [ ] Cherry-pick vs merge
- [ ] Interactive rebase for squashing commits
- [ ] Tags and versioning
- [ ] Pull request workflow
- [ ] Handling large files (git-lfs)

---

**Created by Krishna Kayaking** | [LinkedIn](https://www.linkedin.com/in/krishnakayaking/) | [YouTube](https://www.youtube.com/@TechieKrishnaKayaking)
