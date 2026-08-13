# Home Assistant Setup Guide

Everything needed to adopt this sun-aware blind automation system: per-cover
metadata, the helpers it needs, and the five automations, in the order
you'd normally add them.

## Prerequisites

- Home Assistant Core/OS with YAML config access. No HACS, no custom
  integrations — everything here uses core Home Assistant.
- Covers whose position can be set numerically (`cover.set_cover_position`)
  — most modern cover integrations (Shelly, Zigbee, Z-Wave, etc.) support
  this.
- A temperature sensor for "how hot is it outside" (`sensor.outside_temperature`
  in the examples — point it at whatever outdoor temperature sensor or
  weather integration entity you actually have).

## 1. Per-cover metadata

Add a `homeassistant: customize:` block, one entry per cover you want this
system to manage — see [`examples/customize.yaml`](../examples/customize.yaml)
for the full example. Each cover needs:

```yaml
homeassistant:
  customize:
    cover.living_room:
      azimuth: 180
      friendly_direction: "South"
      override_helper: input_boolean.living_room_cover_override
      last_auto_action_helper: input_number.living_room_cover_last_auto_action
      auto_closed_helper: input_boolean.living_room_cover_auto_closed
```

- `azimuth`: compass degrees (0–359) the window faces. This is the whole
  mechanism — every automation in this repo discovers *only* covers that
  have this attribute, dynamically, at runtime. No cover list is ever
  hardcoded in the automation logic itself (the one unavoidable exception
  is explained in step 5).
- `friendly_direction`: purely cosmetic, used in notification text.
- The three `*_helper` fields point at the input helpers from step 2.

## 2. Helpers

One `input_boolean` override flag, one `input_boolean` auto-closed flag,
and one `input_number` timestamp, per cover — see
[`examples/helpers.yaml`](../examples/helpers.yaml). Stick to a consistent
naming convention (`<cover>_override`, `<cover>_auto_closed`,
`<cover>_last_auto_action`) — nothing enforces this mechanically, but it
keeps `customize.yaml` and `helpers.yaml` easy to keep in sync by eye.

## 3. Sun-based auto-close

[`examples/automations/sun-based-auto-close.yaml`](../examples/automations/sun-based-auto-close.yaml)
runs every 10 minutes. When it's hot outside, it computes — for every cover
with an `azimuth` attribute — whether the sun is currently hitting that
facade, by comparing `sun.sun`'s current azimuth against the cover's own
azimuth (wrapped to handle the 0°/360° compass boundary) and checking the
sun is above the horizon. If so, and the cover hasn't been manually
overridden today, it closes the cover to a per-cover target position (a
`target_positions` dict in the automation's `variables:` — most covers
default to fully closed, but you can list specific covers with a partial
percentage, e.g. a room where you still want some light for a screen).
It also reopens covers it previously auto-closed, once they're no longer
sun-exposed — except any cover listed in `never_reopen` (useful for a
bedroom you never want auto-reopened, for sleep-quality reasons; it'll
still get manually reopened whenever you want).

## 4. Away-mode variant (optional)

[`examples/automations/away-mode-full-close.yaml`](../examples/automations/away-mode-full-close.yaml)
ships disabled (`enabled: false`). It's a more aggressive variant: instead
of per-cover target positions, it fully closes every eligible cover
whenever nobody is home (checked via `zone.home`'s occupancy, not any named
person) and it's hot — since nobody's around to care about partial
daylight. Enable it if you want that behavior; it still respects each
cover's override flag.

## 5. Manual-override detection

[`examples/automations/manual-override-detect.yaml`](../examples/automations/manual-override-detect.yaml)
is the load-bearing piece — read [`docs/architecture.md`](architecture.md)
for the full reasoning. In short: it compares a cover's position-changed
timestamp against that cover's own `last_auto_action_helper` (written by
steps 3/4 whenever they move a cover on purpose). If the gap is bigger than
a short debounce window — or there's no record of an automated action on
that cover *today* — it treats the change as manual and sets the cover's
override flag.

One real Home Assistant limitation to know about: triggers can't be
templated, so this automation's `entity_id` trigger list has to be a
literal list of your covers — unlike every other piece of dynamic-discovery
logic in this repo, this one list needs manual upkeep when you add or
remove a cover.

## 6. Nightly override reset

[`examples/automations/override-nightly-reset.yaml`](../examples/automations/override-nightly-reset.yaml)
runs at midnight and turns every override flag back off — discovered
dynamically the same way as step 3, so this file never needs editing when
you add/remove a cover.

## 7. Heat-warning notification

[`examples/automations/heat-warning-notification.yaml`](../examples/automations/heat-warning-notification.yaml)
reuses the same azimuth-diff calculation from step 3, but only sends a
notification naming which covers are currently sun-exposed — no automatic
action. Useful on its own (without adopting the full auto-close behavior),
and as a sanity check that your `azimuth` values are actually correct while
you're setting this up.

## Adapting to your own home

- Figure out each window's azimuth with a compass app (most phones have
  one built in) standing at the window facing outward, or from your home's
  site plan/floor plan if it shows compass orientation.
- Add/remove a cover by adding/removing its `customize.yaml` block and
  matching helpers — every automation except step 5's trigger list picks
  it up automatically.
- Tune `sun_facing_window_degrees` (default 90°) if your windows are very
  recessed/shaded by overhangs and get direct sun over a narrower angle
  range in practice.

## Apply without a restart

1. **Developer Tools → YAML → Check Configuration** after any edit.
2. Reload the individual domains that changed — no full restart needed for
   any of these:
   - **Developer Tools → YAML → Input Booleans** (or the `input_boolean.reload` service)
   - **Developer Tools → YAML → Input Numbers** (or the `input_number.reload` service)
   - **Developer Tools → YAML → Automations** (or the `automation.reload` service)

   (Double-check these exact reload service/domain names against the Home
   Assistant version you're running — this hasn't been verified against a
   live instance as part of writing this guide.)

## Troubleshooting

- **A cover never seems to auto-close or reopen:** check it actually has an
  `azimuth` attribute set in `customize.yaml` — missing it means every
  automation here silently ignores that cover. That's the intended way to
  exclude a cover, but it's an easy thing to forget you did.
- **A cover keeps "fighting" manual adjustments, or won't reopen after you
  manually close/reopen it:** the debounce window in
  `manual-override-detect.yaml` (`debounce_seconds`, default 120) may be
  too short for how slowly your covers move — widen it if the automation
  seems to be treating its own action's tail end as a manual override, or
  too long if it's missing genuine quick manual adjustments right after an
  automated move.

  To tell which direction you're dealing with, check your Home Assistant
  history for the cover entity and its `last_auto_action_helper`
  (`input_number`) around the time of the problem:
  - If a manual adjustment happened *shortly after* an automated move and
    the override flag never turned on, the gap was inside the debounce
    window and got misread as the automation's own tail end — **lower**
    `debounce_seconds` toward (but a bit above) your cover's actual
    open/close travel time.
  - If the override flag turns on right after the automation itself moves
    the cover (with no human involved), the debounce window is shorter
    than your cover needs — **raise** it.

  As a starting point: many modern motorized roller shutters (e.g. Shelly-
  based relays) complete a full open/close traversal in well under 30
  seconds, in which case the 120s default is far more generous than
  needed and mainly serves to swallow real quick manual corrections. A
  debounce window of roughly your cover's travel time plus a few seconds
  of margin is usually enough.
