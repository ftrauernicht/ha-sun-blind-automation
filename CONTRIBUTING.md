# Contributing

Thanks for wanting to improve this!

## Ground rules

- All changes land via Pull Request. Direct pushes to `main` are blocked
  for everyone, including the maintainer — enforced by branch protection,
  not just convention.
- Keep PRs focused: one logical change per PR.
- The automated `Validate examples` check must pass before a PR can be
  merged.

## How to contribute

1. Fork the repo and create a branch.
2. Make your change under `examples/` and/or `docs/`.
3. Validate locally before opening the PR:
   ```bash
   pip install pyyaml jinja2
   python scripts/validate_examples.py
   ```
4. If you changed any example YAML, update `docs/home-assistant-setup.md`
   (and `docs/architecture.md` if relevant) in the same PR — the docs and
   the examples must never drift apart.
5. Open a Pull Request against `main`. Fill in the PR template checklist.

## Naming convention

Use generic entity ids in any example you contribute — `cover.<generic_room>`
(e.g. `cover.kitchen`, `cover.guest_room`), never your own real device
names or room names. This repo is meant to be copy-pasted and adapted, not
to accumulate real household details over time.
