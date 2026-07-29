# ha-sun-blind-automation

[![Validate](https://github.com/ftrauernicht/ha-sun-blind-automation/actions/workflows/validate.yml/badge.svg)](https://github.com/ftrauernicht/ha-sun-blind-automation/actions/workflows/validate.yml)
[![Link Check](https://github.com/ftrauernicht/ha-sun-blind-automation/actions/workflows/link-check.yml/badge.svg)](https://github.com/ftrauernicht/ha-sun-blind-automation/actions/workflows/link-check.yml)
[![License: MIT](https://img.shields.io/github/license/ftrauernicht/ha-sun-blind-automation)](LICENSE)

A sun-aware, self-correcting Home Assistant blind/cover automation system:
it closes covers when the sun is actually hitting that facade and it's hot,
reliably tells its own moves apart from a real manual adjustment (despite
cover integrations not giving you a reliable way to do that directly), and
resets itself every night — all without ever hardcoding a list of your
covers in the automation logic.

## How it works, at a glance

Every cover you want managed gets a small metadata block via Home
Assistant's `customize:` — its compass azimuth, plus three linked helper
entities:

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

Every automation in this repo discovers covers dynamically by filtering
`states.cover` for entities carrying an `azimuth` attribute — never a
hardcoded entity list. Add a cover by adding its metadata; leave one out to
exclude it entirely. (There's one honest exception, explained in the setup
guide: Home Assistant triggers can't be templated, so the manual-override
detector's trigger needs a literal entity list.)

```
              customize: azimuth + 3 helper entities per cover
                                     |
                                     v
                          dynamic cover discovery
             (states.cover | selectattr('azimuth', 'defined'))
                                     |
       +---------------+--------------+------------+---------------+
       |               |              |            |               |
+------------+  +------------+  +----------+  +---------+  +--------------+
| sun-based  |  | away-mode  |  | manual-  |  | nightly |  | heat-warning |
| auto-close |  |  variant   |  | override |  |  reset  |  | notification |
|            |  | (optional) |  |  detect  |  |         |  |              |
+------------+  +------------+  +----------+  +---------+  +--------------+

        manual-override detect compares the event timestamp against
        the cover's last_auto_action_helper (not the event context)
```

The trickiest part of the whole system is telling the automation's own
cover moves apart from a real manual adjustment — the cover integration's
event context isn't reliable enough for this, because the "final position
reached" event arrives asynchronously from whatever triggered the move.
This repo solves it with a timestamp comparison instead of a context check.
See [`docs/architecture.md`](docs/architecture.md) for the full reasoning.

## Setup

See [`docs/home-assistant-setup.md`](docs/home-assistant-setup.md) for the
full, step-by-step guide (metadata → helpers → each automation, in the
order you'd add them), plus adapting-to-your-own-home notes and
troubleshooting.

The complete example YAML lives under [`examples/`](examples/).

## Related

See also the `sun-exposed-windows-notification` pattern in
[ha-automation-cookbook](https://github.com/ftrauernicht/ha-automation-cookbook)
for a standalone version of the notification half of this system, without
the full blind-control automation.

## Contributing

All changes land via Pull Request — direct pushes to `main` are blocked,
for everyone including the maintainer. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE).

---

Part of the `ha-*` Home Assistant toolkit — see also
[ha-dashboard-recipes](https://github.com/ftrauernicht/ha-dashboard-recipes)
and [ha-zone-time-stats](https://github.com/ftrauernicht/ha-zone-time-stats).
