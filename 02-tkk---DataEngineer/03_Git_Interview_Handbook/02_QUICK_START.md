# 🌳 Git Interview Handbook — Quick Start Guide

Welcome to the **Git Interview Handbook**! This folder contains everything you need to master Git
for interviews and real-world development.

---

## 📂 What's Inside?

### 1. **README.md** — Complete Git Guide
   - **Best for:** Learning all concepts from scratch
   - **Contains:** 
     - Git fundamentals (3 states, what is Git)
     - Local operations (init, staging, committing, viewing history)
     - Branching & merging (creating, switching, merging, rebasing)
     - Remote operations (push, pull, fetch)
     - Undoing changes (reset, revert, restore)
     - Advanced workflows (stash, interactive rebase, tags)
     - Merge conflicts and resolution
     - 14 detailed interview Q&A
   - **How to use:** Read top-to-bottom as comprehensive reference

### 2. **COMMANDS_AND_PRACTICE.md** — Quick Reference + Exercises
   - **Best for:** Hands-on learning and quick lookups
   - **Contains:**
     - Command cheat sheet (50+ commands organized by task)
     - 8 progressive practice exercises (from basic to advanced)
     - Debugging & troubleshooting guide
     - Interview prep checklist
   - **How to use:** 
     - Use first 100 lines as quick command reference
     - Follow exercises step-by-step to build confidence
     - Check troubleshooting section when stuck

### 3. **WORKFLOWS_AND_BEST_PRACTICES.md** — Team Collaboration
   - **Best for:** Understanding real-world workflows
   - **Contains:**
     - 3 major Git workflows (Git Flow, GitHub Flow, Trunk-Based)
     - Merge strategies comparison
     - Pull request best practices
     - Fork/open source workflow
     - Commit message conventions
     - Code review checklist
     - Common mistakes and how to avoid them
     - Real interview scenarios (4 detailed walkthroughs)
   - **How to use:** Learn the workflow your team uses, practice the scenarios

---

## 🎯 How to Use This Handbook

### For Beginners (Never Used Git)
1. Read **README.md** sections 1-3 (Fundamentals → Local Operations)
2. Run the **Exercise 1: Basic Workflow** from COMMANDS_AND_PRACTICE.md
3. Practice **Exercise 2: Branching & Merging** 
4. Try **Exercise 3: Merge Conflicts** in a safe environment

### For Intermediate (Know Basics)
1. Skim **README.md** for anything you missed
2. Focus on **Undoing Changes** and **Advanced Git Workflows** sections
3. Do **Exercises 4-6** from COMMANDS_AND_PRACTICE.md
4. Read **WORKFLOWS_AND_BEST_PRACTICES.md** — learn your team's workflow

### For Advanced (Preparing for Interview)
1. Review **Interview Q&A** section in README.md
2. Go through **Real Interview Scenarios** in WORKFLOWS_AND_BEST_PRACTICES.md
3. Use COMMANDS_AND_PRACTICE.md as quick reference during practice
4. Focus on explaining the "why" not just the "how"

---

## 🔥 Most Important Interview Topics

**These come up in almost every interview:**

1. **Branching strategies** (Git Flow vs GitHub Flow)
   - Read: WORKFLOWS_AND_BEST_PRACTICES.md → Git Workflows section

2. **Merge vs Rebase**
   - Read: README.md → Branching & Merging section (Q6)

3. **Reset vs Revert**
   - Read: README.md → Interview Q&A (Q8, Q9, Q10)

4. **Pull Request workflow**
   - Read: WORKFLOWS_AND_BEST_PRACTICES.md → Pull Request Best Practices

5. **Merge conflicts**
   - Read: README.md → Merge Conflicts section
   - Practice: COMMANDS_AND_PRACTICE.md → Exercise 3

6. **Recovering lost commits**
   - Read: README.md → Finding & Recovering Lost Commits
   - Key command: `git reflog`

7. **Stashing**
   - Read: README.md → Stashing Work-in-Progress
   - Practice: COMMANDS_AND_PRACTICE.md → Exercise 6

---

## 💡 Pro Tips

### Tip 1: Use Aliases for Long Commands
```bash
git config --global alias.lg "log --graph --oneline --all --decorate"
git lg  # Much shorter!
```

### Tip 2: Practice Commands Locally
```bash
# Create a test repo
mkdir git-test && cd git-test
git init

# Run commands from COMMANDS_AND_PRACTICE.md exercises
# Safe place to experiment before touching real projects
```

### Tip 3: Explain the "Why"
In interviews, don't just say the command. Explain:
- **What:** What does the command do?
- **Why:** Why would you use it?
- **When:** In what situation?
- **Alternative:** Is there another way?

**Example:**
```
Q: "How do you undo a pushed commit?"
❌ Bad: "git revert abc123"
✅ Good: "I'd use `git revert abc123` because it creates a new commit 
         that undoes the change. This is safe for pushed commits because 
         it doesn't rewrite history. If it was only local, I'd use 
         `git reset --hard` instead, but that rewrites history so it's 
         only safe for unpushed commits."
```

### Tip 4: Know Your Team's Workflow
Each team has conventions:
- Which branching strategy? (Git Flow or GitHub Flow)
- How to name branches? (feature/X or feat-X)
- Squash or merge commits?
- Who can force push?

Ask this in your interview!

---

## 📋 Interview Checklist

Before your interview, make sure you can:

### Concepts
- [ ] Explain what Git is and why it's important
- [ ] Draw or describe the 3 Git states
- [ ] Compare centralized vs distributed VCS
- [ ] Explain HEAD, branches, tags

### Commands
- [ ] Clone and init a repo
- [ ] Create, switch, delete branches
- [ ] Commit and push changes
- [ ] Merge and handle conflicts
- [ ] Rebase and understand linear history
- [ ] Reset, revert, and restore
- [ ] Stash changes temporarily
- [ ] Use cherry-pick for specific commits

### Workflows
- [ ] Describe Git Flow (multiple environments)
- [ ] Describe GitHub Flow (continuous deployment)
- [ ] Explain pull request workflow
- [ ] Fork and contribute to open source

### Troubleshooting
- [ ] Recover deleted commits using reflog
- [ ] Undo commits without losing work
- [ ] Resolve merge conflicts
- [ ] Sync forked repository with upstream

### Best Practices
- [ ] Write good commit messages
- [ ] Use meaningful branch names
- [ ] Know when to squash commits
- [ ] Understand when to use force push (rarely!)

---

## 🚀 Next Steps

1. **Pick your starting point:** Beginner / Intermediate / Advanced (see above)
2. **Read one section** from the relevant file
3. **Practice the commands** in a test repository
4. **Do one exercise** from COMMANDS_AND_PRACTICE.md
5. **Review one interview scenario** from WORKFLOWS_AND_BEST_PRACTICES.md
6. **Repeat** until confident

---

## ❓ Frequently Asked Questions

**Q: Do I need to memorize all commands?**
A: No! Know the common ones (add, commit, push, pull, merge, branch). Use this guide for reference.

**Q: Should I use Git CLI or GUI?**
A: Start with CLI to understand concepts. GUI tools are fine once you understand.

**Q: Git Flow or GitHub Flow?**
A: Ask your team! Both are valid. Understand the tradeoffs.

**Q: How often should I commit?**
A: Small, logical chunks. One feature per commit if possible.

**Q: Is force push ever OK?**
A: Only on YOUR personal branches. On shared branches, use `--force-with-lease` at minimum.

**Q: How do I learn more?**
A: Check the resources links at the end of each file!

---

## 📊 Quick Reference Table

| Task | Command | Alternative |
|---|---|---|
| Create branch | `git switch -c name` | `git checkout -b name` |
| Merge | `git merge branch` | `git pull origin branch` |
| Undo commit | `git reset --soft HEAD~1` | `git revert` (if pushed) |
| See history | `git log --oneline` | `git reflog` (includes deletes) |
| Stash | `git stash` | `git stash apply` |
| Rebase | `git rebase main` | `git merge main` |
| Push | `git push origin main` | `git push -u origin main` (first time) |
| View diff | `git diff main feature` | `git show abc123` (single commit) |

---

## 🎓 Learning Path (Recommended)

```
Week 1: Fundamentals
  → README.md sections 1-3
  → COMMANDS_AND_PRACTICE.md Exercise 1-2
  → Time: 3-4 hours

Week 2: Intermediate
  → README.md sections 4-6
  → COMMANDS_AND_PRACTICE.md Exercise 3-6
  → Time: 4-5 hours

Week 3: Advanced
  → README.md sections 7-8
  → WORKFLOWS_AND_BEST_PRACTICES.md (all)
  → COMMANDS_AND_PRACTICE.md Exercise 7-8
  → Time: 4-5 hours

Week 4: Practice & Interview Prep
  → Review all Interview Q&A
  → Practice real scenarios
  → Mock interview
  → Time: 3-4 hours

Total: ~16 hours to mastery
```

---

## 💬 Final Tips

1. **Git is about collaboration.** Understand how your team uses it.
2. **History matters.** Good commit messages help future developers (and you in 6 months).
3. **Small commits are better.** Easier to review, easier to revert if needed.
4. **Practice safely.** Use test repositories, don't panic on your real projects.
5. **Ask questions.** In interviews, show you think about edge cases and team practices.

---

**Good luck with your interview prep!** 🚀

For questions or suggestions, reach out on:
- 📺 [YouTube](https://www.youtube.com/@TechieKrishnaKayaking)
- 💼 [LinkedIn](https://www.linkedin.com/in/krishnakayaking/)
- 🌐 [Website](https://www.techiekrishnakayaking.com/)

**Created by Krishna Kayaking** 💙
