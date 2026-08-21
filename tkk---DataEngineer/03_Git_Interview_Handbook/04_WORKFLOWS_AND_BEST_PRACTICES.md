# Git Workflows & Team Collaboration Strategies

> This document covers the most common Git workflows used in real-world projects,
> branching strategies that interviewers ask about, and best practices for team collaboration.

---

## 📊 Git Workflows

### 1. Git Flow (Vincegt Flow)

**Used for:** Complex projects with scheduled releases (traditional software, mobile apps).

**Branch Structure:**
```
main          ← Production code (tagged releases: v1.0, v2.0, etc.)
    ↑
release/*     ← Release candidate branch (bug fixes only)
    ↑
develop       ← Integration branch (always "working")
    ↑
feature/*     ← Individual features / stories
bugfix/*      ← Maintenance bugs
hotfix/*      ← Production hotfixes
```

**Workflow Example:**

```bash
# 1. Start a new feature
git switch -c feature/user-authentication develop

# 2. Work and commit
git add . && git commit -m "Add user auth"
git push origin feature/user-authentication

# 3. Create Pull Request on GitHub (feature → develop)
# 4. Code review and merge

# 5. When ready for release, create release branch
git switch -c release/v1.0.0 develop

# 6. Bug fixes only (no new features)
git add . && git commit -m "Fix release bug"

# 7. Merge to main with version tag
git switch main
git merge release/v1.0.0
git tag -a v1.0.0 -m "Release version 1.0.0"

# 8. Merge back to develop
git switch develop
git merge release/v1.0.0

# 9. Production hotfix (if bug found in main)
git switch -c hotfix/critical-bug main
git add . && git commit -m "Fix critical production bug"
git switch main
git merge hotfix/critical-bug
git tag -a v1.0.1 -m "Hotfix v1.0.1"
git switch develop
git merge hotfix/critical-bug
```

**Interview Q:** *"When would you use Git Flow over GitHub Flow?"*

**A:** Git Flow is better for:
- Scheduled, versioned releases
- Large teams with formal QA/testing
- Complex projects with strict release cycles
- Mobile apps, packaged software

**Pros:**
- Clear separation of concerns
- Handles hotfixes separately
- Good for teams with formal release process

**Cons:**
- Complex workflow (many branches)
- Harder to learn
- More merge overhead

---

### 2. GitHub Flow (Simpler Alternative)

**Used for:** Continuous deployment, fast-moving projects (web apps, SaaS).

**Branch Structure:**
```
main          ← Production code (always deployable)
    ↑
feature/*     ← Individual features
bugfix/*      ← Bug fixes
```

**Workflow Example:**

```bash
# 1. Create feature branch
git switch -c feature/new-feature

# 2. Work and commit
git add . && git commit -m "Add new feature"

# 3. Push and create Pull Request
git push origin feature/new-feature

# 4. Code review and merge to main
# 5. Deploy to production immediately
# 6. Delete branch
git branch -d feature/new-feature
```

**Interview Q:** *"What does 'main is always deployable' mean?"*

**A:** Every commit on `main` should:
- Pass all tests
- Be production-ready
- Be immediately deployable

This requires:
- Automated testing (CI/CD)
- Code reviews before merge
- Quick feedback loop

**Pros:**
- Simple to understand and execute
- Continuous deployment friendly
- Fewer merge conflicts

**Cons:**
- Requires robust CI/CD
- Less formal for large teams
- All features go through main

---

### 3. Trunk-Based Development

**Used for:** High-velocity teams, continuous deployment, microservices.

**Principle:** Developers commit directly to `main` (or very short-lived branches).

```bash
# Most commits go directly to main
git switch main
git commit -m "Small, incremental change"
git push origin main

# OR very short branches (hours, not days)
git switch -c feature-xyz
git commit -m "Feature"
git push origin feature-xyz
# Merge immediately, branch deleted
```

**Interview Q:** *"How do you keep `main` stable with trunk-based development?"*

**A:** Through:
- Feature flags (toggle features on/off without code changes)
- Aggressive automated testing
- Code reviews pre-commit or post-commit
- Quick feedback and rollback capability

**Pros:**
- Minimal merge conflicts
- Simple workflow
- Continuous integration

**Cons:**
- Requires excellent CI/CD
- Feature flags complexity
- Higher risk if safeguards fail

---

## 🔄 Common Merge Strategies

### 1. Merge Commit (Default)

```bash
git merge feature-branch
# Creates a merge commit with two parents
```

**Pros:** Full history preserved, can see feature branch clearly
**Cons:** Non-linear history

**Use:** Feature branches with multiple commits

---

### 2. Squash & Merge

```bash
git merge --squash feature-branch
git commit -m "Feature description"
# All feature commits become ONE commit
```

**Pros:** Clean history, each feature is one commit
**Cons:** Loses individual commit history

**Use:** Cleaning up messy feature branches before merging

---

### 3. Rebase & Fast-Forward

```bash
git switch feature-branch
git rebase main        # Replay feature commits on main
git switch main
git merge feature-branch --ff-only
# Linear history, no merge commit
```

**Pros:** Clean, linear history
**Cons:** Rewrites history (unsafe if pushed)

**Use:** Local branches not yet pushed

---

### 4. No Fast-Forward

```bash
git merge --no-ff feature-branch
# Always creates a merge commit, even if linear
```

**Pros:** Clear branch structure in history
**Cons:** Extra commit for linear changes

**Use:** Enforcing branch visibility for documentation

---

## 👥 Pull Request Best Practices

### Creating a PR

**Interview Q:** *"What makes a good pull request?"*

```bash
# 1. Create feature branch
git switch -c feature/user-profile

# 2. Make focused, atomic commits
git add . && git commit -m "Add user profile model"
git add . && git commit -m "Add profile API endpoint"
git add . && git commit -m "Add profile tests"

# 3. Push
git push -u origin feature/user-profile

# 4. On GitHub: Create PR with:
#    - Clear title: "Add user profile feature"
#    - Description: What changed, why, how to test
#    - Reference issue: "Closes #123"
#    - Link related PRs
```

### PR Description Template

```markdown
## Description
Brief summary of what this PR does.

## Why?
Explain the motivation and context.

## How?
Describe the implementation approach.

## Changes
- Bullet point 1
- Bullet point 2
- Bullet point 3

## Testing
How to test these changes:
```bash
npm test
npm run test:integration
```

## Screenshots (if UI changes)
[Add before/after screenshots]

## Closes
Closes #123

## Checklist
- [ ] Tests pass
- [ ] Code is documented
- [ ] No breaking changes
- [ ] Reviewed by at least one person
```

### Reviewing a PR

```bash
# 1. Fetch and check out the PR branch
git fetch origin pull/123/head:pr-123
git switch pr-123

# 2. Run tests
npm test

# 3. Review code
# - Is logic correct?
# - Are there edge cases?
# - Is code readable?
# - Are tests adequate?

# 4. Suggest changes via GitHub comments
# 5. Request changes or approve
```

### Addressing PR Feedback

```bash
# Make requested changes
git add . && git commit -m "Address PR feedback: simplify logic"

# Push (don't force, just push normally)
git push origin feature/user-profile

# GitHub automatically updates the PR
# Don't create a new PR!
```

---

## 🌍 Working with Forks (Open Source)

**Interview Q:** *"Describe the fork and pull request workflow for open source."*

### Workflow

```bash
# 1. Fork repository on GitHub (creates your copy)

# 2. Clone YOUR fork (not the original)
git clone https://github.com/your-username/repo.git
cd repo

# 3. Add upstream remote (original repo)
git remote add upstream https://github.com/original-owner/repo.git

# 4. Create feature branch
git switch -c fix/issue-123

# 5. Make changes and commit
git add . && git commit -m "Fix: resolve issue #123"

# 6. Push to your fork
git push origin fix/issue-123

# 7. Go to GitHub, create Pull Request (your fork → original repo)

# 8. Keep your fork in sync
git fetch upstream
git merge upstream/main

# 9. If maintainers ask for changes
git add . && git commit -m "Address review feedback"
git push origin fix/issue-123
# GitHub PR auto-updates

# 10. After merge, clean up
git switch main
git pull upstream main
git branch -d fix/issue-123
```

### Syncing Forked Repo

```bash
# Fetch upstream changes
git fetch upstream

# Merge into your main
git switch main
git merge upstream/main

# Push to your fork
git push origin main
```

---

## 🏢 Team Collaboration Best Practices

### 1. Commit Message Conventions

**Interview Q:** *"What makes a good commit message?"*

#### Bad Commit Messages
```
git commit -m "fix"
git commit -m "stuff"
git commit -m "changes"
git commit -m "asdf"
```

#### Good Commit Messages (Conventional Commits)

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` — new feature
- `fix` — bug fix
- `docs` — documentation
- `style` — formatting (no logic change)
- `refactor` — code restructure (no behavior change)
- `perf` — performance improvement
- `test` — add/modify tests
- `chore` — build, dependencies, etc.

**Examples:**

```bash
# Good
git commit -m "feat(auth): add JWT authentication"
git commit -m "fix(login): resolve password validation bug"
git commit -m "docs(readme): update installation instructions"
git commit -m "refactor(api): simplify request handler"
git commit -m "perf(query): add database index for faster lookups"
git commit -m "test(user): add unit tests for user model"
```

### 2. Branch Naming Conventions

```bash
feature/user-authentication    # New feature
fix/login-bug                  # Bug fix
docs/api-docs                  # Documentation
refactor/simplify-logic        # Refactoring
hotfix/production-error        # Production hotfix
```

### 3. Code Review Checklist

Before approving a PR:
- [ ] Tests pass and coverage is adequate
- [ ] No hardcoded values (passwords, IPs, tokens)
- [ ] Code follows style guidelines
- [ ] Comments explain complex logic
- [ ] No console.log or debug statements
- [ ] No unreachable code
- [ ] No performance regressions
- [ ] Documentation updated if needed
- [ ] Commit messages are clear

### 4. CI/CD Integration

**Interview Q:** *"How does Git integrate with CI/CD pipelines?"*

Most teams use GitHub Actions, GitLab CI, Jenkins, etc. Typical flow:

```
Feature branch pushed
    ↓
Webhook triggers CI
    ↓
Run tests, linting, build
    ↓
If all pass → PR can be merged
    ↓
If merged to main → Auto-deploy to staging/production
```

---

## ⚠️ Common Mistakes & How to Avoid

### Mistake 1: Committing to Main Directly

❌ **Wrong:**
```bash
git switch main
git add . && git commit -m "Add feature"
git push
```

✅ **Right:**
```bash
git switch -c feature/new-feature
git add . && git commit -m "Add feature"
git push origin feature/new-feature
# Create PR
```

---

### Mistake 2: Large, Unfocused Commits

❌ **Wrong:**
```bash
# One huge commit with 20 unrelated changes
git add .
git commit -m "Stuff"
```

✅ **Right:**
```bash
# Multiple focused commits
git add src/auth.py && git commit -m "feat(auth): add password validation"
git add src/api.py && git commit -m "feat(api): add user endpoint"
git add tests/ && git commit -m "test: add auth tests"
```

---

### Mistake 3: Pushing Sensitive Data

❌ **Wrong:**
```bash
echo "API_KEY=super-secret-123" > .env
git add . && git commit -m "Add environment config"
git push  # OMG, API key is public!
```

✅ **Right:**
```bash
# Add to .gitignore
echo ".env" >> .gitignore

# Commit only .env.example
echo "API_KEY=" > .env.example
git add . && git commit -m "Add environment config template"
git push
```

---

### Mistake 4: Force Pushing to Shared Branches

❌ **Wrong:**
```bash
git rebase main
git push --force origin main  # Destroys colleagues' commits!
```

✅ **Right:**
```bash
# Only force push to YOUR personal branches
git push --force-with-lease origin my-personal-branch
# Or just merge/rebase if pushing shared branches
```

---

### Mistake 5: Ignoring Merge Conflicts

❌ **Wrong:**
```bash
git merge feature-branch  # Conflict!
# Just commit without resolving
```

✅ **Right:**
```bash
git merge feature-branch
# Carefully resolve each conflict
git diff  # Review changes
git add .
git commit -m "Resolve merge conflict"
```

---

## 🎯 Interview Scenarios

### Scenario 1: Production Hotfix

**Situation:** Critical bug in production. How do you handle it?

**Answer:**
```bash
# 1. Create hotfix branch from main
git switch -c hotfix/critical-bug main

# 2. Fix the bug
echo "fix" >> app.py

# 3. Commit and push
git add . && git commit -m "hotfix: fix production bug"
git push origin hotfix/critical-bug

# 4. Create PR, merge to main ASAP
# 5. Tag the release
git tag -a v1.0.1 -m "Hotfix"
git push origin --tags

# 6. Deploy to production
# 7. Merge back to develop to keep it in sync
git switch develop
git merge hotfix/critical-bug
git push origin develop
```

---

### Scenario 2: Rebasing Before Merge

**Situation:** Your feature branch is behind main. Should you rebase or merge?

**Answer:**
```bash
# Option 1: Rebase (if not pushed or team agrees)
git fetch origin
git rebase origin/main
git push origin feature/branch

# Option 2: Merge (if already pushed)
git fetch origin
git merge origin/main
git push origin feature/branch

# Preference: depends on team style (discuss in PR)
```

---

### Scenario 3: Accidental Commit to Main

**Situation:** You committed directly to main instead of creating a feature branch.

**Answer:**
```bash
# 1. See what you committed
git log --oneline
# abc123 My feature
# def456 Previous main

# 2. Create feature branch at current commit
git branch feature/my-feature

# 3. Reset main back
git reset --hard def456

# 4. Main is now clean, feature branch has your commits
git switch feature/my-feature
git log  # your commits are here
```

---

### Scenario 4: Recovering Deleted Branch

**Situation:** You deleted a branch and realize you needed it.

**Answer:**
```bash
# 1. Check reflog
git reflog

# 2. Find the deleted branch commit
# abc123 HEAD@{3}: checkout: moving from feature/important to main

# 3. Recover it
git switch -c feature/important abc123
# OR
git reset --hard abc123
```

---

## 📚 Additional Resources

- **[Git Book](https://git-scm.com/book/en/v2)** — Comprehensive guide
- **[Conventional Commits](https://www.conventionalcommits.org/)** — Commit standard
- **[GitHub Flow Guide](https://guides.github.com/introduction/flow/)** — Simple workflow
- **[Semantic Versioning](https://semver.org/)** — Version tagging

---

**Created by Krishna Kayaking** | [LinkedIn](https://www.linkedin.com/in/krishnakayaking/) | [YouTube](https://www.youtube.com/@TechieKrishnaKayaking)
