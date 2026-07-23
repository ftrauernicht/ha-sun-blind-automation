# CLAUDE.md

Guidance for Claude Code (or any AI coding agent) working in this repository.

## What this repo is

A reference implementation/template for a sun-aware Home Assistant blind
automation system, meant for other Home Assistant users to adapt to their
own home. Nothing here is live-polled by anything — unlike some other
`ha-*` repos, this one is pure documentation/example YAML, not a data
source any running Home Assistant instance pulls from at runtime.

## Hard rules

- **Never commit directly to `main`.** Always work on a branch and open a
  Pull Request. Branch protection enforces this for everyone including the
  repo owner — do not attempt to bypass it even if you technically have
  the access to do so.
- Keep `docs/home-assistant-setup.md` (and `docs/architecture.md`, where
  relevant) in sync with any change to `examples/**/*.yaml` in the same PR
  — this repo's only value is the docs matching the example code exactly.
- Entity ids and names in every example must stay generic and in English
  — no real device names, no real people's names, no real addresses. See
  the PR template checklist.
- Automations must keep using dynamic discovery (`selectattr('attributes.azimuth', 'defined')`
  or equivalent) instead of a hardcoded per-cover list, wherever Home
  Assistant's templating actually allows it — that dynamic-discovery
  property is the whole point of this pattern. The one automation whose
  trigger can't be templated (`manual-override-detect.yaml`) is a known,
  documented exception — don't try to "fix" it by hardcoding lists
  elsewhere instead.
- Run `python scripts/validate_examples.py` after any YAML edit — the same
  check gates merging in CI.

## Repo layout

- `examples/customize.yaml` — per-cover metadata block.
- `examples/helpers.yaml` — the `input_boolean`/`input_number` helpers the
  metadata points at.
- `examples/automations/*.yaml` — the five automations (sun-based
  auto-close, optional away-mode variant, manual-override detection,
  nightly reset, heat-warning notification).
- `docs/home-assistant-setup.md` — step-by-step adoption guide.
- `docs/architecture.md` — deep-dive on why the manual-override detector
  works the way it does.
- `scripts/validate_examples.py` — YAML/Jinja-syntax validation, used
  locally and in CI (see its docstring for what it does and doesn't catch).
- `.github/workflows/validate.yml` — CI job (`Validate examples`) required
  by branch protection before merge.
