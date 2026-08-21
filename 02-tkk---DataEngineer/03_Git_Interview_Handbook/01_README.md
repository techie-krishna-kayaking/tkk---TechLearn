# 🌳 Git Interview Handbook

> **Master Git for Interviews** — The most comprehensive, hands-on, interview-focused guide to Git.
> Learn every command with real examples, alternatives, common mistakes, and the exact questions
> interviewers ask about version control, branching strategies, and collaboration workflows.

---

## 📖 Table of Contents

1. [Git Fundamentals](#git-fundamentals)
2. [Local Repository Operations](#local-repository-operations)
3. [Branching & Merging](#branching--merging)
4. [Remote Repositories](#remote-repositories)
5. [Undoing Changes](#undoing-changes)
6. [Advanced Git Workflows](#advanced-git-workflows)
7. [Merge Conflicts](#merge-conflicts)
8. [Interview Q&A](#interview-qa)
9. [Practice Scenarios](#practice-scenarios)

---

## 🎯 Git Fundamentals

### What is Git?

**Interview Q:** *"What is Git and why is it essential in software development?"*

Git is a **distributed version control system (DVCS)** that allows multiple developers to:
- Track changes to code over time
- Work independently on different features
- Merge work safely
- Revert to previous versions if needed
- Maintain a complete history of the project

**Key Point:** Every developer has a complete copy of the repository (unlike centralized VCS like SVN).

```bash
# Check Git version
git --version
```

### The Three States of Git

```
┌─────────────────────────────────────────────────────────┐
│  Working Directory  │  Staging Area  │  Local Repository │
│  (Untracked files)  │  (Index)       │  (Commit history) │
│                                                           │
│  git add ──────────>  git commit ──────>  git push      │
└─────────────────────────────────────────────────────────┘
```

**Interview Q:** *"Explain the three states of Git files."*

| State | Description | Command |
|---|---|---|
| **Untracked** | File exists but Git doesn't know about it | `git add` |
| **Staged** | File is marked for commit (in staging area) | `git commit` |
| **Committed** | File is saved in the repository | `git push` |

---

## 🚀 Local Repository Operations

### 1. Initialize a Repository

**Interview Q:** *"How do you start tracking a project with Git?"*

```bash
# Create a new Git repository
git init

# Check Git status
git status

# What's the difference?
# git init   → creates a NEW repo in current folder
# git clone  → copies an EXISTING repo from a server
```

**INTERVIEW TIP:** Know when to use `git init` (starting fresh) vs `git clone` (joining existing project).

---

### 2. Configuring Git

**Interview Q:** *"How do you set up Git for the first time? What configuration is critical?"*

```bash
# Global configuration (applies to all repos on your machine)
git config --global user.name "Krishna Kayaking"
git config --global user.email "krishna@example.com"

# Local configuration (applies to current repo only)
git config --local user.name "Local User"
git config --local user.email "local@example.com"

# Check your configuration
git config --list
git config --list --global
git config --list --local

# View a specific setting
git config user.name
```

**Priority order:** Local > Global > System

**INTERVIEW TIP:** Always configure `user.name` and `user.email` — every commit needs this metadata!

---

### 3. Staging & Committing

**Interview Q:** *"What is the staging area and why is it important?"*

The **staging area (index)** is a middle ground between your working directory and your repository. It lets you:
- **Selectively commit** — stage only certain files/changes
- **Review before committing** — see exactly what you're committing
- **Organize related changes** into atomic commits

```bash
# Stage all changes
git add .

# Stage specific file(s)
git add src/main.py

# Stage only parts of a file (interactive)
git add -p   # or --patch

# Check what's staged vs unstaged
git status
git diff              # unstaged changes
git diff --staged     # staged changes

# Commit with message
git commit -m "Add user authentication"

# Commit with detailed message (opens editor)
git commit   # without -m

# Stage and commit tracked files in one command (skip untracked)
git commit -am "Fix bug in user login"

# Amend the last commit (add forgotten changes)
git commit --amend --no-edit           # add to last commit without changing message
git commit --amend -m "New message"    # change the message too
```

**INTERVIEW TRAP:** `git commit -am` does NOT stage untracked files — only modifications to tracked files.

**INTERVIEW Q:** *"What does `git commit --amend` do? When would you use it?"*

```bash
# Forgot to add a file in the last commit?
git add forgotten_file.py
git commit --amend --no-edit

# This REPLACES the last commit with a new one (includes the forgotten file).
# ⚠️ ONLY do this if you haven't pushed yet!
```

---

### 4. Viewing Commit History

**Interview Q:** *"How do you inspect the project history? What are the different ways to view commits?"*

```bash
# Simple commit log
git log

# One commit per line (compact)
git log --oneline

# Show last N commits
git log -n 5
git log -5

# Show commits with file changes
git log --name-status

# Show commits with diff (verbose)
git log -p

# Show commits on a specific branch
git log main
git log main --oneline

# Show commits NOT in another branch (useful for understanding what's unique)
git log main ^develop   # commits in main but NOT in develop

# Show commits by author
git log --author="Krishna"

# Show commits since/until a date
git log --since="2 weeks ago"
git log --until="2024-01-01"

# Search commit messages for a keyword
git log --grep="bug fix"

# Show all commits, including unreachable ones (useful for recovery)
git reflog

# Graph visualization (shows branch structure)
git log --graph --oneline --all --decorate
```

**Pro tip:** Create an alias for the graph view:
```bash
git config --global alias.lg "log --graph --oneline --all --decorate"
git lg   # now much shorter!
```

**INTERVIEW TIP:** Know `git reflog` — it's a lifesaver for recovering "lost" commits.

---

### 5. Inspecting Changes

**Interview Q:** *"How do you see what changed between commits or branches?"*

```bash
# Diff between working directory and last commit
git diff

# Diff between staged changes and last commit
git diff --staged

# Diff between two commits
git diff <commit1> <commit2>
git diff abc123 def456

# Diff between branches
git diff main develop

# Diff for a specific file
git diff main develop -- src/app.py

# Show summary of changes (not the full diff)
git diff --stat

# Show changed files only
git diff --name-only

# Show which lines were changed (blame = who changed what)
git blame src/main.py
```

**INTERVIEW Q:** *"What is `git blame` and when would you use it in a team?"*

`git blame` shows which commit (and author) modified each line. Useful for:
- Finding who introduced a bug
- Understanding why a line of code exists
- Code review and historical context

```bash
git blame file.py
git blame -L 10,20 file.py   # show lines 10-20 only
```

---

## 🌿 Branching & Merging

### 1. Understanding Branches

**Interview Q:** *"What is a branch? Why is branching important for team development?"*

A **branch** is a pointer to a specific commit. It allows developers to:
- Work on features independently without affecting the `main` branch
- Experiment safely (changes are isolated)
- Maintain multiple versions of the code in parallel

```bash
# List all branches (local)
git branch

# List all branches (including remote)
git branch -a

# Show which branch is currently active (has *)
git branch

# Create a new branch
git branch feature/user-auth    # creates but doesn't switch

# Create and switch to a new branch (shorter)
git checkout -b feature/user-auth

# Modern way (Git 2.23+, preferred)
git switch -c feature/user-auth

# Switch to an existing branch
git checkout main

# Modern way (Git 2.23+, preferred)
git switch main

# Delete a branch
git branch -d feature/user-auth          # safe delete (warns if not merged)
git branch -D feature/user-auth          # force delete (no warnings)

# Rename current branch
git branch -m new-branch-name

# Rename a different branch
git branch -m old-name new-name
```

**INTERVIEW TIP:** Know both `git checkout -b` (older, but still widely used) and `git switch -c` (newer, clearer).

---

### 2. Merging Branches

**Interview Q:** *"How do you merge branches? What's the difference between merge and rebase?"*

#### Merging (creates a merge commit)

```bash
# Switch to the branch you want to merge INTO
git switch main

# Merge feature branch INTO main
git merge feature/user-auth

# What happens:
# ✓ All commits from feature/user-auth are brought into main
# ✓ A NEW "merge commit" is created (has two parents)
# ✓ History is preserved (you can see feature branch clearly)
```

**Merge visualized:**
```
      feature/user-auth
             |
      C3 -- C4
     /        /
C1 -- C2 ----M (merge commit)
     \        \
      main
```

#### Merging with Options

```bash
# No Fast-Forward (always creates a merge commit, even if linear)
git merge --no-ff feature/user-auth

# Squash (combines all feature commits into ONE commit, then merges)
git merge --squash feature/user-auth
git commit -m "Merge feature branch"

# Abort a merge if conflicts arise
git merge --abort
```

**INTERVIEW Q:** *"What's the difference between `--squash` and regular merge?"*

| Option | Result | Use Case |
|---|---|---|
| `git merge` | Merge commit created; full history preserved | Feature branches with multiple commits |
| `--squash` | Feature commits condensed to 1; cleaner history | Cleaning up messy feature branches |
| `--no-ff` | Always creates merge commit, even if no conflicts | Enforcing branch visibility in main |

---

### 3. Rebasing (Rewrite History)

**Interview Q:** *"What is rebasing? How is it different from merging? When would you use one over the other?"*

**Rebasing** replays commits from one branch onto another, creating a linear history (no merge commit).

```bash
# Rebase current branch onto main
git rebase main

# What happens:
# ✓ Git temporarily "saves" commits from your branch
# ✓ Resets your branch to main
# ✓ Replays your commits on top of main
# ✓ Result: a clean, linear history
```

**Rebase visualized:**
```
BEFORE:
      feature/user-auth
             |
      C3 -- C4
     /
C1 -- C2
     \
      main

AFTER (git rebase main):
      feature/user-auth
             |
      C3' -- C4'
            /
C1 -- C2 --
      \
       main
```

**Merge vs Rebase:**

| Operation | History | Merge Commit | Use Case |
|---|---|---|---|
| `merge` | Non-linear (shows branch) | Yes | Preserve feature branch history; team features |
| `rebase` | Linear (cleaner) | No | Keep history clean; personal branches |

**⚠️ GOLDEN RULE:** Never rebase commits that have been pushed! It rewrites history.

```bash
# ✅ OK: rebase a local branch
git rebase main

# ❌ NO: rebase a branch already on GitHub
# If you've pushed, other developers have the "old" commits → chaos!
# If you MUST, force push VERY carefully:
git push --force-with-lease
```

**INTERVIEW TIP:** Mention both merge and rebase, and when to use each. Shows deep understanding.

---

### 4. Cherry-Pick (Select Specific Commits)

**Interview Q:** *"What if you want to apply just ONE commit from another branch?"*

```bash
# Copy a specific commit from one branch onto another
git cherry-pick abc123

# Cherry-pick multiple commits
git cherry-pick abc123 def456 ghi789

# Cherry-pick a range of commits
git cherry-pick abc123..ghi789   # includes abc123 to ghi789

# Continue cherry-pick after resolving conflicts
git cherry-pick --continue

# Abort cherry-pick
git cherry-pick --abort
```

**Use case:** You have a bug fix on `develop` but need it on `main` urgently.

```bash
git switch main
git cherry-pick abc123   # commits the fix to main
```

---

## 🔄 Remote Repositories

### 1. Setting Up Remotes

**Interview Q:** *"What are remotes? How do you manage connections to GitHub/GitLab?"*

A **remote** is a reference to a repository hosted on a server (GitHub, GitLab, Bitbucket, etc.).

```bash
# View all configured remotes
git remote -v

# Add a new remote
git remote add origin https://github.com/user/repo.git

# Common remote names:
# origin   → your main remote (usually GitHub/GitLab)
# upstream → the original repo you forked from
# backup   → a backup location

# Change a remote URL
git remote set-url origin https://github.com/user/new-repo.git

# Remove a remote
git remote remove origin

# Show details about a remote
git remote show origin
```

---

### 2. Pushing Changes

**Interview Q:** *"How do you send your commits to the server? What does `git push` do?"*

```bash
# Push current branch to remote (assumes remote-tracking branch exists)
git push

# Push to a specific remote and branch
git push origin main

# Push a new branch to remote (and set tracking)
git push -u origin feature/user-auth
# -u sets upstream, so 'git push' alone works next time

# Push all branches
git push --all

# Push a specific commit (not the whole branch)
git push origin abc123:refs/heads/temp-branch

# Delete a remote branch
git push origin --delete feature/user-auth
# or
git push origin :feature/user-auth

# Push tags
git push origin --tags

# Force push (dangerous! use --force-with-lease)
git push --force-with-lease    # ✅ safer than --force
git push --force               # ❌ can lose others' work
```

**INTERVIEW TRAP:** `git push --force` can delete colleagues' commits. Use `--force-with-lease` instead.

---

### 3. Fetching & Pulling

**Interview Q:** *"What's the difference between `git fetch` and `git pull`?"*

```bash
# Fetch updates from remote WITHOUT merging (safe)
git fetch origin

# Check what changed
git log origin/main
git diff main origin/main

# Now merge manually
git merge origin/main

# Pull = Fetch + Merge (in one command)
git pull origin main
# Equivalent to:
# git fetch origin
# git merge origin/main

# Pull with rebase (avoid merge commits)
git pull --rebase origin main
# Equivalent to:
# git fetch origin
# git rebase origin/main
```

**Fetch vs Pull:**

| Command | What Happens | Risk | Use |
|---|---|---|---|
| `fetch` | Downloads remote changes, doesn't merge | None | See what changed before merging |
| `pull` | Fetch + Merge automatically | Merge conflicts | Get latest code quickly |
| `pull --rebase` | Fetch + Rebase | Rewrites history | Clean, linear history |

**INTERVIEW Q:** *"Why would you use `git fetch` instead of `git pull`?"*

`git fetch` is safer because:
- You can inspect changes before merging
- You can decide whether to merge or rebase
- You won't accidentally introduce merge conflicts into your working directory

```bash
# Best practice workflow:
git fetch origin
git log origin/main        # see what changed
git diff main origin/main  # see the actual changes
git merge origin/main      # merge when ready
```

---

## ↩️ Undoing Changes

### 1. Unstaging Files

**Interview Q:** *"You staged the wrong file. How do you unstage it without losing changes?"*

```bash
# Unstage a file (file remains in working directory, unmodified)
git restore --staged file.py

# Older way (still works):
git reset HEAD file.py
```

---

### 2. Discarding Changes

**Interview Q:** *"How do you discard changes in your working directory?"*

```bash
# Discard changes to a file (CANNOT be undone)
git restore file.py

# Older way:
git checkout -- file.py

# Discard ALL changes in working directory
git restore .

# Discard changes to specific directory
git restore src/
```

**⚠️ WARNING:** `git restore` discards changes permanently (use `git diff` first to confirm).

---

### 3. Undoing Commits

**Interview Q:** *"You committed the wrong code. How do you undo the commit without losing work?"*

```bash
# Undo last commit, keep changes staged
git reset --soft HEAD~1

# Undo last commit, keep changes unstaged
git reset --mixed HEAD~1    # default
git reset HEAD~1

# Undo last commit, discard changes (dangerous!)
git reset --hard HEAD~1

# Undo multiple commits
git reset --soft HEAD~3     # undo last 3 commits
```

**Reset modes:**

| Mode | Staging Area | Working Dir | Use |
|---|---|---|---|
| `--soft` | Kept | Kept | Re-stage and recommit |
| `--mixed` (default) | Cleared | Kept | Undo commit, keep changes to edit |
| `--hard` | Cleared | Cleared | Completely undo (⚠️ dangerous) |

**INTERVIEW Q:** *"What's the difference between `git reset` and `git revert`?"*

```bash
# reset = rewrite history (only for local, unpushed commits)
git reset --soft HEAD~1

# revert = create a NEW commit that undoes the change (safe for pushed commits)
git revert abc123    # creates a new commit that undoes abc123
```

---

### 4. Reverting Commits (Safe Undo for Pushed Code)

**Interview Q:** *"You pushed bad code to production. How do you safely undo it?"*

```bash
# Create a new commit that reverses an old commit
git revert abc123

# The NEW commit undoes abc123, but history is preserved
# Safe to push (doesn't rewrite history)

# Revert multiple commits
git revert abc123 def456

# Revert with custom message
git revert -m 1 merge-commit-hash   # -m specifies which parent
```

**Git Reset vs Revert:**

| Command | Type | Pushed OK? | History | Use Case |
|---|---|---|---|---|
| `reset` | Rewrite | ❌ No | Erased | Local commits only |
| `revert` | New commit | ✅ Yes | Preserved | Undo pushed commits |

---

### 5. Finding & Recovering Lost Commits

**Interview Q:** *"I accidentally deleted a commit. Can I recover it?"*

```bash
# View all commits, even deleted ones
git reflog

# Reset to a commit that no longer appears in log
git reset --hard abc123    # abc123 from reflog

# OR create a new branch from it
git checkout -b recovery abc123
```

**INTERVIEW TIP:** `git reflog` is a lifesaver. Git keeps references for ~90 days.

---

## 🔀 Advanced Git Workflows

### 1. Stashing Work-in-Progress

**Interview Q:** *"You're in the middle of work but need to switch branches. What do you do?"*

```bash
# Save changes temporarily (without committing)
git stash

# List all stashes
git stash list

# Apply the most recent stash
git stash apply

# Apply a specific stash
git stash apply stash@{0}

# Apply and delete the stash
git stash pop

# Delete a stash
git stash drop stash@{0}

# Create a branch from a stash
git stash branch feature-branch   # stash becomes the new branch
```

**Use case:**
```bash
# You're on feature/a, want to help with urgent bug on main
git stash                    # save your work
git switch main
git switch -c hotfix/urgent  # fix the bug
git add . && git commit -m "Fix urgent bug"
git switch feature/a
git stash pop                # resume your work
```

---

### 2. Interactive Rebase (Rewrite History)

**Interview Q:** *"You made 5 commits but they should be squashed into 1. How do you fix this?"*

```bash
# Interactive rebase on last 5 commits
git rebase -i HEAD~5

# An editor opens showing the commits:
# pick abc123 Commit 1
# pick def456 Commit 2
# pick ghi789 Commit 3
# pick jkl012 Commit 4
# pick mno345 Commit 5

# Change 'pick' to 'squash' (or 's') to combine commits:
# pick abc123 Commit 1
# squash def456 Commit 2
# squash ghi789 Commit 3
# squash jkl012 Commit 4
# squash mno345 Commit 5

# Save and exit (editor closes)
# You'll be prompted for a combined commit message

# Result: 5 commits → 1 commit
```

**Interactive rebase commands:**
- `pick` — use this commit
- `reword` — use but change the commit message
- `squash` — combine with previous commit
- `fixup` — combine without keeping the message
- `drop` — delete this commit
- `reorder` — rearrange the lines to reorder commits

**⚠️ WARNING:** Only do interactive rebase on LOCAL, UNPUSHED commits!

---

### 3. Tags (Marking Releases)

**Interview Q:** *"How do you mark important versions like v1.0, v2.0?"*

```bash
# Create a lightweight tag
git tag v1.0

# Create an annotated tag (has metadata: author, date, message)
git tag -a v1.0 -m "Release version 1.0"

# List tags
git tag

# Show tag details
git show v1.0

# Tag a past commit
git tag v1.0 abc123

# Push tags to remote
git push origin --tags
git push origin v1.0    # push specific tag

# Delete a local tag
git tag -d v1.0

# Delete a remote tag
git push origin --delete v1.0
```

**Lightweight vs Annotated:**

| Type | Storage | Use Case |
|---|---|---|
| Lightweight | Just a pointer | Quick markers |
| Annotated | Full metadata | Production releases |

---

## 🛑 Merge Conflicts

### What is a Merge Conflict?

**Interview Q:** *"What causes merge conflicts? How do you resolve them?"*

A **conflict** occurs when:
- The same file was changed in different ways on different branches
- Git can't automatically merge the changes

**Example conflict:**
```bash
# Branch A changed line 5 to: print("Hello A")
# Branch B changed line 5 to: print("Hello B")
# Git can't choose, so it marks it as a conflict
```

### Resolving Conflicts

```bash
# Start merge
git merge feature/user-auth

# Git reports conflicts in file(s)
# CONFLICT (content): Merge conflict in app.py

# Open the conflicted file in your editor:
```

**Conflicted file looks like:**
```python
<<<<<<< HEAD
print("Hello from main")
=======
print("Hello from feature")
>>>>>>> feature/user-auth
```

**Manually resolve:**
1. Decide which code to keep
2. Delete the conflict markers (`<<<<`, `====`, `>>>>`)
3. Save the file

```python
# Choose to keep BOTH versions:
print("Hello from main")
print("Hello from feature")
```

**Then:**
```bash
# Stage the resolved file
git add app.py

# Complete the merge
git commit -m "Resolve merge conflict in app.py"
```

### Conflict Resolution Tools

```bash
# Use a merge tool (if configured)
git mergetool

# Common merge tools: VSCode, Beyond Compare, Kdiff3, Meld

# Configure VSCode as merge tool:
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd "code --wait --merge \$LOCAL \$REMOTE \$BASE \$MERGED"
```

### Aborting a Merge

```bash
# Change your mind? Abort the merge
git merge --abort

# Your working directory returns to pre-merge state
```

---

## 💬 Interview Q&A

### Core Concepts

**Q1: Explain the difference between Git and GitHub.**

**A:** 
- **Git** is version control software (runs locally)
- **GitHub** is a hosting service for Git repositories (cloud platform)
- Git works on your machine; GitHub is where you push/store code

**Q2: What are the main differences between centralized VCS (like SVN) and distributed VCS (like Git)?**

**A:**
| Feature | Centralized (SVN) | Distributed (Git) |
|---|---|---|
| Repository | One central repo | Each developer has full repo |
| Branching | Slow, cumbersome | Fast, easy |
| Offline work | Limited | Full functionality |
| Merging | Manual, error-prone | Built-in, reliable |
| Backup | Single point of failure | Every clone is a backup |

**Q3: What is the purpose of `.gitignore`?**

**A:** Specifies files/folders that Git should NOT track. Common examples:
```
node_modules/
*.pyc
.env
__pycache__/
.DS_Store
```

**Q4: How would you recover a deleted branch?**

**A:**
```bash
git reflog                          # find the commit hash
git checkout -b recovered-branch abc123
```

---

### Branching & Merging

**Q5: Describe a Git branching strategy (e.g., Git Flow, GitHub Flow).**

**A: Git Flow** (complex projects):
```
main       ←  production releases (v1.0, v2.0)
  ↑
release/   ← prepare for release
  ↑
develop    ← integration branch (always working)
  ↑
feature/*  ← individual features
bugfix/*   ← bug fixes
```

**A: GitHub Flow** (simpler, continuous deployment):
```
main       ← production code (always deployable)
  ↑
feature/*  ← branches for features/fixes
```

**Q6: When would you use `git rebase` vs `git merge`?**

**A:**
- Use `merge` when: feature branch should be visible in history; team collaboration
- Use `rebase` when: want clean, linear history; local branch not yet pushed

**Q7: What is a fast-forward merge?**

**A:** When the branch being merged is directly ahead of the current branch, Git simply moves the pointer forward (no merge commit created).

```bash
# Fast-forward (no merge commit)
main: A -- B -- C
feature:       C -- D
# After merge: A -- B -- C -- D

# To force a merge commit even on fast-forward:
git merge --no-ff feature/branch
```

---

### Undoing & Recovery

**Q8: When would you use `git reset` vs `git revert`?**

**A:**
- `reset`: For LOCAL, unpushed commits. Rewrites history.
- `revert`: For PUSHED commits. Creates new commit that undoes the change.

**Q9: How do you completely discard a commit from a pushed branch?**

**A:**
```bash
git revert abc123         # creates new commit that undoes abc123
git push origin main      # push the revert to share with team
```

**Q10: I pushed the wrong commit. What's the safest way to fix it?**

**A:** Use `git revert` (doesn't rewrite history):
```bash
git revert abc123
git push origin main

# Colleagues' local branches aren't affected
```

**DANGEROUS alternative (only if no one else pulled):**
```bash
git reset --hard HEAD~1
git push --force-with-lease
# Use --force-with-lease (not --force) to be safer
```

---

### Collaboration

**Q11: How do you keep your fork in sync with the upstream repo?**

**A:**
```bash
# Add upstream remote
git remote add upstream https://github.com/original/repo.git

# Fetch upstream changes
git fetch upstream

# Merge into your main branch
git merge upstream/main

# Push to your fork
git push origin main
```

**Q12: Describe a pull request workflow.**

**A:**
```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make commits
git add . && git commit -m "Add new feature"

# 3. Push to your fork
git push origin feature/new-feature

# 4. Go to GitHub → create Pull Request
# 5. Team reviews and discusses
# 6. Make changes if requested
git add . && git commit -m "Address review feedback"
git push origin feature/new-feature

# 7. PR is merged on GitHub
# 8. Delete branch
git branch -d feature/new-feature
git push origin --delete feature/new-feature
```

---

### Performance & Optimization

**Q13: What is `git gc` (garbage collection)?**

**A:** Optimizes the repository by:
- Compressing objects
- Removing unreachable objects
- Defragmenting

```bash
git gc
# Usually run automatically, but can be triggered manually
```

**Q14: How would you handle a very large file that shouldn't be in Git?**

**A:**
```bash
# Remove from all history (nuclear option)
git filter-branch --tree-filter 'rm -f large-file' HEAD

# Or use git-lfs (Git Large File Storage)
git lfs install
git lfs track "*.mp4"
git add .gitattributes large-file.mp4
git commit -m "Add video with LFS"
git push
```

---

## 🎮 Practice Scenarios

### Scenario 1: Oops! Wrong Branch

**Situation:** You made 3 commits on `main` but they should have been on a new branch `feature/new-stuff`.

**Solution:**
```bash
# Create new branch pointing to current commits
git branch feature/new-stuff

# Reset main back to before your commits
git reset --hard origin/main

# Switch to feature branch
git switch feature/new-stuff

# Verify your commits are there
git log
```

---

### Scenario 2: Messy Commit History

**Situation:** You have 5 commits on your feature branch, but 3 of them are "WIP" or "Fix typo". Clean it up before merging.

**Solution:**
```bash
# Interactive rebase on last 5 commits
git rebase -i HEAD~5

# In the editor:
# pick abc123 Initial feature
# squash def456 Add more stuff
# squash ghi789 Fix bug
# squash jkl012 WIP
# squash mno345 Final touches

# Save. Combine message. Done!
# Result: 1 clean commit instead of 5

# Push (force push if already pushed once locally)
git push origin feature/branch
```

---

### Scenario 3: Emergency Hotfix

**Situation:** Production bug found. You're on `feature/new-stuff`. Need to hotfix on `main` ASAP.

**Solution:**
```bash
# Save your work
git stash

# Switch to main
git switch main

# Create hotfix branch
git switch -c hotfix/critical-bug

# Fix the bug
echo "fix" >> app.py

# Commit and push
git add . && git commit -m "Fix production bug"
git push origin hotfix/critical-bug

# Create Pull Request on GitHub
# After merge:

# Get back to your feature
git switch feature/new-stuff
git stash pop

# Resume work
```

---

### Scenario 4: Merge Conflict

**Situation:** Merging `feature/a` into `main` has conflicts.

**Solution:**
```bash
git merge feature/a

# CONFLICT: Merge conflict in app.py

# Open editor and resolve:
# - Remove conflict markers
# - Keep correct code
# - Save

git add app.py
git commit -m "Resolve merge conflict"
git push origin main
```

---

### Scenario 5: Recovering Deleted Branch

**Situation:** You deleted `feature/important` but realize you need it.

**Solution:**
```bash
# Find the commit in reflog
git reflog

# You see: abc123 HEAD@{2}: checkout: moving from feature/important to main

# Recover it
git switch -c feature/important abc123

# Or just reset to it
git reset --hard abc123
```

---

## 📝 Key Git Commands Cheat Sheet

| Task | Command |
|---|---|
| Initialize repo | `git init` |
| Clone repo | `git clone <url>` |
| Check status | `git status` |
| Stage changes | `git add .` |
| Commit | `git commit -m "message"` |
| View log | `git log --oneline` |
| Create branch | `git switch -c branch-name` |
| Switch branch | `git switch branch-name` |
| Merge branch | `git merge branch-name` |
| Push changes | `git push origin main` |
| Pull changes | `git pull origin main` |
| Fetch updates | `git fetch origin` |
| Undo commit | `git reset --soft HEAD~1` |
| Revert commit | `git revert abc123` |
| Stash changes | `git stash` |
| View diff | `git diff main feature/branch` |
| Interactive rebase | `git rebase -i HEAD~5` |

---

## 🎓 Interview Tips

1. **Know the difference:** `merge` vs `rebase`, `fetch` vs `pull`, `reset` vs `revert`
2. **Show depth:** Mention why certain decisions (like `--force-with-lease`) matter
3. **Discuss workflows:** Git Flow, GitHub Flow, understand team collaboration
4. **Recovery stories:** Know how to recover from mistakes (reflog, stash, etc.)
5. **Performance:** Mention `git gc`, large files, shallow clones
6. **Practice:** Create a test repo and try all scenarios

---

## 🚀 Going Further

- **[Pro Git Book](https://git-scm.com/book/en/v2)** — Comprehensive, free resource
- **[Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials)** — Clear, visual explanations
- **[Git Docs](https://git-scm.com/docs)** — Official reference

---

**Created by Krishna Kayaking** | [LinkedIn](https://www.linkedin.com/in/krishnakayaking/) | [YouTube](https://www.youtube.com/@TechieKrishnaKayaking) | [Website](https://www.techiekrishnakayaking.com/)
