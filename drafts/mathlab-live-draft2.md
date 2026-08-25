Contributions to passagemath: modular robustness, contributor tooling, and linear programming usability

[YOUR NAME], Undergraduate Scholar
Matthias Köppe, Faculty Mentor

Introduction
Passagemath is a modular, pip-installable repackaging of SageMath, the open-source math software. Rather than installing all of Sage, users can install just the parts of passagemath they need and run it in plain Python environments like Google Colab that can interact with other Python tools. Math researchers, educators, and students use it for symbolic computation, combinatorics, linear programming and more.

The passagemath undergraduate group, led by Professor Matthias Köppe, works on adding features or fixing bugs in the software to make it easier to use. The group also uses passagemath to explore math by writing notebooks and running experiments.

This quarter, I contributed to fixing bugs in the codebase, building tools and materials to help the group, and exploring how to make linear programming easier to use in passagemath.


Progress

Code contributions
I made 13 pull requests that were merged into the passagemath codebase. My approach to choosing what to work on was to prioritize based on scale, neglectedness, and fit. In the beginning, this looked like infrastructure problems that affected many areas and bugs from passagemath being modular. I used AI tools to find widespread codebase errors and read long CI logs that made it more feasible to work on the most important things. This was very helpful for getting to know the codebase. The code contributions fall into four themes.

Modular installation
Passagemath’s modular design means code that assumed a full SageMath install could break when dependencies were missing. A common bug was a function trying to import an optional package, but the import doesn’t happen, so the function errors when it is called but never assigned. I fixed this pattern for different files relating to combinatorics, number theory, and others. To help with this, I made check_unbound_imports.py, an abstract syntax tree tool that scans the codebase for this pattern, and categorized issues that needed attention or false positives.

Build and CI infrastructure
A newer version of setuptools deprecated pkg_resources and this caused Linux build crashes. I replaced it with importlib.metadata. I also discovered a Windows CI failure caused by an invalid path format that affects multiple packages across many releases. Professor Köppe made the fix based on that diagnosis.

Plotting in Python kernels
In Colab and JupyterLite, passagemath plots used to show up as text (Graphics object consisting of 1 graphics primitive) instead of images. The fix was to add the method (_repr_png_ and _repr_svg_) to the Graphics class so python knew where to get the images. Now plots render as images in Colab and JupyterLite. I presented the plotting fix in the mid-quarter presentations.

LP ergonomics
I documented dual values in the passagemath linear programming guide and describe this more in the ergonomics section.

Later, my approach was to be a multiplier and help teammates get started fast. 

Onboarding documents and exercises
When students joined the group at the beginning of Spring 2026, I made documents to help teammates set up their passagemath research environment, made a list of shovel-ready issues that described the problem and a potential approach, and also made exercises that introduced generalized bug patterns to familiarize teammates with the codebase.

I aimed for the exercise notebooks to be pedagogically great. I designed them so students could see the problem themselves, why it happens, and fix it. The goal was to give new contributors something concrete to do quickly by editing real code and fixing a real problem instead of reading documentation and files.

A common problem for teammates was getting the environment set up. This involved jupyter, git, and things tended to get messy so we spent a lot of time debugging. Several teammates used these docs to get their environment running.

I also helped a teammate, Runze (Tony) Yu, navigate the codebase and git workflow while he worked on a shovel-ready issue. His PR (#2358) was merged.

pm-explore
The first assignment Professor Köppe gave us was to make a notebook exploring some part of passagemath. Getting the environment to work with the right kernel got a lot of people stuck and a lot of time was spent on debugging environment problems. This inspired me to make pm-explore which automates this.

Given any passagemath file, pm-explore automatically generates a jupyter notebook with the environment set up so people can see what methods the file has and can immediately run and modify methods. It uses an abstract syntax tree to look at the text, so it works even when the environment is broken. Afterwards, I learned that this is similar to the runnable code in the passagemath documentation website. The pm-explore tool is good for having it work on your own computer like a student researcher who wants to explore the codebase would use. Students can also make changes to the notebook to explore the methods. One teammate, whose work was mainly exploring passagemath features, used pm-explore for that.

LP ergonomics
Eventually, I decided to work on LP ergonomics because I wanted to work on something in depth.

I was taking MAT 168 Optimization and tried to use passagemath instead of cvxpy. You had to write nested loops and keep track of indices often, which made it difficult to use. Some methods you would like easy access to like getting dual values had to be found in the backend. (Issue #2347).  

I thought it could be worth working on because this was a place where passagemath could really be improved. Passagemath can handle symbolics and is integrated with other math things. Passagemath can do exact arithmetic over rationals and number fields, while cvxpy only handles floats. This whole idea is very big though. There would be architectural and frontend changes that would take careful design considerations. I would have to familiarize myself with what was currently going on. My plan was to edit the documentation so it would be easier to find the dual values (PR #2353). Next, I tried tracing through the backend with the goal of understanding what was going on. It was very difficult. The files were scattered. The next step was to work through linear programming problems myself to identify specific pain points to eventually bring up and propose potential solutions. This was something I wasn’t naturally doing. I was doing cvxpy for class and doing it in passagemath was difficult. 

connection between backpropagation and linear programming
In backpropagation, gradients are computed using the chain rule. While doing LP in MAT 168, I noticed the simplex method gives dual values similar to the gradient. The dual value is how much the optimum moves if you loosen a constraint. Doing the forward pass in backpropagation is similar to using simplex to get the optimum and reading the dual values from the final simplex dictionary is similar to the backward pass.


Future Plans

I plan to present work at the Math Lab poster session in Fall 2026.

References
Modular installation robustness
#2253 — Fix NameError in Partitions.cardinality() when passagemath-flint is absent — https://github.com/passagemath/passagemath/pull/2253

#2282 — Fix unbound pari NameError in five modules; lazy-import sympy in calculus_method — https://github.com/passagemath/passagemath/pull/2282

#2283 — Fix unbound NameError in padic_extension_leaves and multi_polynomial_ideal; add AST checker — https://github.com/passagemath/passagemath/pull/2283

#2287 — Fix pickling regression introduced by lazy_import in calculus_method.py — https://github.com/passagemath/passagemath/pull/2287

#2293 — polynomial_quotient_ring: add # needs sage.modules doctest guards — https://github.com/passagemath/passagemath/pull/2293

#2292 — docs, tox: document check_unbound_imports and add tox env — https://github.com/passagemath/passagemath/pull/2292

#2354 — Add missing sage.libs.linbox doctest guards in modsym and geometry/cone — https://github.com/passagemath/passagemath/pull/2354

Build / CI
#2237 — build: replace pkg_resources with importlib.metadata in configure check — https://github.com/passagemath/passagemath/pull/2237

#2239 — PIP_FIND_LINKS=file://$SAGE_SPKG_WHEELS yields invalid uri on Windows — https://github.com/passagemath/passagemath/issues/2239

Plot display
#2351 — Fix plot display in plain Python Jupyter kernels — https://github.com/passagemath/passagemath/pull/2351

#2366 — plot: add _repr_svg_() for plain Python Jupyter kernels — https://github.com/passagemath/passagemath/pull/2366

#2368 — plot: fix circular import in plain Python by pre-importing sage.structure.element — https://github.com/passagemath/passagemath/pull/2368

LP ergonomics
#2353 — glpk_backend: document get_row_dual via MixedIntegerLinearProgram — https://github.com/passagemath/passagemath/pull/2353

#2347 — MIP workflow is harder than cvxpy for matrix-structured LP problems — https://github.com/passagemath/passagemath/issues/2347

lp-level2-prep notes — https://github.com/sacchen/passagemath-workspace/blob/main/projects/lp-level2-prep.md

Numerical correctness
#2356 — affine_homset: fix complex-tolerance comparison in numerical point filtering — https://github.com/passagemath/passagemath/pull/2356

External package
numerical-interactive-mip #6 — backends: correct exception types in dictionary constructors and pivot update — https://github.com/passagemath/passagemath-pkg-numerical-interactive-mip/pull/6

Onboarding
https://github.com/sacchen/passagemath-workspace/blob/main/onboarding.md
https://github.com/sacchen/passagemath-workspace/blob/main/setup.md

Exercise
https://github.com/sacchen/passagemath-workspace/blob/main/exercises/importerror-fix-pattern/importerror-fix-pattern.ipynb

Exercise notebook design
https://github.com/sacchen/passagemath-workspace/blob/main/exercises/DESIGN.md

Pm-explore
https://github.com/sacchen/passagemath-workspace/tree/main/tools/pm-explore

Getting started and shovel ready issues
https://github.com/passagemath/passagemath/issues/2269#issuecomment-4070368357

Runze (Tony) Yu
https://github.com/passagemath/passagemath/pull/2358
