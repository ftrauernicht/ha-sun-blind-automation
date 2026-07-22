#!/usr/bin/env python3
"""Validate every YAML file under examples/.

Two checks, both intentionally shallow (see the caveat below):

1. The file must be loadable YAML. Plain `yaml.safe_load` chokes on
   Home Assistant's custom tags (`!secret`, `!include`, `!include_dir_list`,
   `!include_dir_named`, `!input`), so this registers permissive
   passthrough constructors for them on a SafeLoader subclass first.
2. Every string value that contains a Jinja `{{` is compiled (not
   rendered) via a vanilla jinja2.Environment().parse() to catch gross
   template syntax errors.

Caveat: this does NOT catch undefined-variable or missing-Home-Assistant-
filter errors (e.g. a typo'd `state_attr` call) — that would require
running inside a real Home Assistant instance, which is disproportionate
for a docs/examples repo. Treat a clean run here as "parses", not as
"guaranteed to work on your instance".
"""
import sys
from pathlib import Path

import jinja2
import yaml

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = ROOT / "examples"

HA_TAGS = ["!secret", "!include", "!include_dir_list", "!include_dir_named", "!include_dir_merge_named", "!input"]


class PermissiveLoader(yaml.SafeLoader):
    pass


def _passthrough_constructor(loader, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)


for tag in HA_TAGS:
    PermissiveLoader.add_constructor(tag, _passthrough_constructor)


def iter_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from iter_strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from iter_strings(v)


def check_jinja_syntax(value, jinja_env, errors, file_path):
    for s in iter_strings(value):
        if "{{" in s or "{%" in s:
            try:
                jinja_env.parse(s)
            except jinja2.TemplateSyntaxError as exc:
                errors.append(f"{file_path}: Jinja syntax error: {exc}")


def main():
    yaml_files = sorted(EXAMPLES_DIR.rglob("*.yaml")) + sorted(EXAMPLES_DIR.rglob("*.yml"))
    if not yaml_files:
        print("No YAML files found under examples/", file=sys.stderr)
        sys.exit(1)

    jinja_env = jinja2.Environment()
    errors = []

    for path in yaml_files:
        text = path.read_text(encoding="utf-8")
        try:
            data = yaml.load(text, Loader=PermissiveLoader)
        except yaml.YAMLError as exc:
            errors.append(f"{path.relative_to(ROOT)}: YAML parse error: {exc}")
            continue
        check_jinja_syntax(data, jinja_env, errors, path.relative_to(ROOT))

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        sys.exit(1)

    print(f"OK: {len(yaml_files)} files validated")


if __name__ == "__main__":
    main()
