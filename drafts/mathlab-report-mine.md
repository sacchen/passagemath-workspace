# Davis Math Lab Project Report, Spring 2026

**[Your Name], Undergraduate Scholar**
**Matthias Köppe, Faculty Mentor**

---

## Introduction

Passagemath is a math software. It is modular and pip installable and can be used on Colab. Educators and students use it as a teaching and learning tool for things like the simplex method in linear programming. Math researchers use it to work with combinatorics and algebraic objects.

The main purpose of the passagemath group is to add features or fix bugs in the software and use passagemath as a tool for math interests.

I made code contributions, made onboarding documents and exercises, and explored the idea of making linear programming easier to use in passagemath.

---

## Progress

### Code contributions

I made 13 pull requests that were merged into the passagemath codebase. The code contributions fall into four themes.

**Modular installation.** Since Sage installs everything, but passagemath only imports packages you need, a common bug was a function trying to import an optional package, but the import doesn't happen, and the function is called but was never assigned. I fixed this pattern for different files relating to combinatorics, number theory, and others. To help with this, I made `check_unbound_imports.py`, an abstract syntax tree tool that scans the codebase for this pattern, and categorized things into things that needed attention or just false positives.

**Build and CI infrastructure.** A newer version of setuptools deprecated a thing and this caused Linux build crashes. I replaced it with the `importlib.metadata` API. I also discovered a Windows CI failure caused by an invalid path format that affects multiple packages across many releases. Professor Köppe made the fix based on this diagnosis.

**Plotting in Python kernels.** In Colab and JupyterLite, passagemath plots used to show up as text (`Graphics object consisting of 1 graphics primitive`) instead of as images. The fix was to add a method to the `Graphics` class so Python knew where to get the images.

**LP ergonomics.** I documented dual values in the passagemath linear programming guide. This is described in more detail in the LP ergonomics section below.

### Research approach and experience

My approach was choosing high-leverage things based on scale, neglectedness, and fit. This included infrastructure problems that affected many areas and bugs from passagemath being modular. Using AI tools was helpful to run analysis for hundreds of files and investigate CI logs to find root causes. This was very good for getting to know the codebase and getting contributions.

Later, my approach was to help my teammates get started fast. This looked like making a list of shovel-ready issues with detailed descriptions of the problem and a potential solution, making onboarding documents, and exercises.

Eventually the returns leveled out. I didn't feel like I was learning generalized software engineering skills or math.

### Onboarding documents and exercises

When students joined the group at the beginning of Spring 2026, I made documents to help teammates set up the passagemath environment and also made exercises that introduced generalized bug patterns as a way to get teammates touching the codebase fast.

A common problem was getting the environment set up. This involved jupyter and git, and things tended to get messy.

I also helped a teammate, Runze (Tony) Yu, navigate the codebase and git workflow while he worked on a pull request.

### pm-explore

The first assignment Professor Köppe gave us was to make a notebook exploring some part of passagemath. Getting the environment to work with the right kernel got a lot of people stuck and a lot of time was spent on debugging environment problems. This inspired me to make pm-explore, which automates this.

Given any passagemath file, pm-explore automatically generates a Jupyter notebook with the environment set up so people can see what methods the file has and can immediately run and modify them. It uses an abstract syntax tree to look at the text, so it works even when the environment is broken. Afterwards, I learned that this is similar to the runnable code in the passagemath documentation website. The pm-explore tool is good for having it work on your own computer like a student researcher who wants to explore the codebase would use. It is also interactive and you can make changes to play around with the methods.

### LP ergonomics

I was taking MAT 168 Optimization and tried to use passagemath instead of cvxpy. You had to write nested loops and keep track of indices often, which made it difficult to use. Some methods you would like easy access to, like getting dual values, had to be found in the backend (Issue #2347).

I thought it could be worth working on because this was a place where passagemath could really be improved. Passagemath can handle symbolics and is integrated with other math things. This whole idea is very big though. There would be architectural and frontend changes that would take careful design considerations. I would have to familiarize myself with what was currently going on. My plan was to edit the documentation so it would be easier to find the dual values (PR #2353). Next, I tried tracing through the backend with the goal of understanding what was going on. It was very difficult. The files were scattered. The next step was to work through linear programming problems myself to identify specific pain points to eventually bring up and propose potential solutions. This was something I wasn't naturally doing. I was doing cvxpy for class, and doing it in passagemath was difficult.

I also presented the plotting fix to the group.

---

## Future Plans

The main thread to continue is LP ergonomics — working through LP problems directly in passagemath, identifying specific pain points, and proposing targeted improvements before implementing them.

I also plan to present this work at the Math Lab poster session in Fall 2026.

---

## References
