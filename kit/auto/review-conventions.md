# Source review conventions

Read this after the technical review, with only the diff in view. These are
maintainer conventions learned from actual review comments. They apply to new
or changed lines and their immediate siblings, never as permission for a
repository-wide cleanup.

## Source documentation

- Use semantic Sphinx roles for Python objects in prose: `:class:`, `:meth:`,
  `:func:`, and `:mod:`. Double backticks are for literal syntax, not a
  substitute for a cross-reference.
- Format distribution names such as **passagemath-plot** as prose emphasis.
  Keep an installation command, requirement specifier, or extra such as
  ``passagemath-plot[tachyon]`` as literal syntax when that distinction
  matters.
- Use one spelling and capitalization for a product throughout the touched
  documentation. The project spelling is **Three.js**, not ``three.js``.
- Treat nearby and recently merged code as evidence, not authority. A copied
  sentence still gets checked against the current convention.

## Configuration files

- Compare a new entry with the whole local block, including conditioned
  entries. In a tox `commands` block, align an unconditional command with the
  command column used after factor conditions when the entries form one
  visual group.
- Check both syntax and presentation. A command that parses and passes CI can
  still draw a review comment for breaking the block's visual structure.

## Final source-editorial pass

1. Freeze the implementation and tests.
2. Run `checks/source-style.sh` on the task.
3. Read every added prose and configuration line without the implementation
   notes open.
4. Scan the touched documentation for sibling occurrences of every warning.
5. Record what was checked and how each warning was resolved in the task's
   `source-style` red-team entry.

The checker deliberately reports warnings where context decides the right
markup. A warning is not permission to ignore the line; the task record is
where the reviewer records the decision.
