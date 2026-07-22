## What does this PR change?

<!-- e.g. "Add a per-cover open-percentage ramp", "Fix the away-mode condition" -->

## Checklist

- [ ] I ran `python scripts/validate_examples.py` locally and it passed
- [ ] Any entity ids I added/changed are generic (`cover.<generic_room>`), not real device names
- [ ] If I changed any YAML under `examples/`, I updated `docs/home-assistant-setup.md` (and `docs/architecture.md` if relevant) in the same PR
- [ ] I didn't hardcode a cover list anywhere that should instead discover covers dynamically via the `azimuth` attribute
