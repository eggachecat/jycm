#!/usr/bin/env python3
"""Validate JYCM policies and produce explanations plus RFC 6902 patches."""

import argparse
import json
import sys
from pathlib import Path


def load_local_jycm():
    """Prefer the surrounding checkout, then fall back to an installed package."""
    for parent in Path(__file__).resolve().parents:
        if (parent / "jycm" / "__init__.py").is_file():
            sys.path.insert(0, str(parent))
            break
    try:
        from jycm import BusinessDiffPolicy
    except (ImportError, AttributeError):
        raise SystemExit(
            "JYCM with BusinessDiffPolicy is required. Run this script from a "
            "current JYCM checkout or install a release that provides the API."
        )
    return BusinessDiffPolicy


def read_json(path):
    with Path(path).open("r", encoding="utf-8") as stream:
        return json.load(stream)


def write_json(path, value):
    rendered = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    if path:
        Path(path).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)


def validate(args):
    policy = load_local_jycm()(read_json(args.policy))
    policy.compile()
    write_json(args.output, policy.to_dict())
    return 0


def compare(args):
    policy = load_local_jycm()(read_json(args.policy))
    before = read_json(args.before)
    after = read_json(args.after)
    differ = policy.build(before, after)
    explanation = differ.explain()
    patch = differ.to_json_patch(include_tests=args.include_tests)
    patched = differ.apply_patch(patch=patch)
    patch_is_semantically_valid = policy.build(patched, after).diff()
    explanation["summary"]["patch_operation_count"] = len(patch)
    explanation["summary"]["patch_semantically_valid"] = patch_is_semantically_valid

    if args.explain_out:
        write_json(args.explain_out, explanation)
    else:
        write_json(None, explanation)
    if args.patch_out:
        write_json(args.patch_out, patch)

    if not patch_is_semantically_valid:
        sys.stderr.write("Generated patch is not semantically equivalent to target.\n")
        return 2
    if args.fail_on_difference and not explanation["equal"]:
        return 1
    return 0


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command")

    validate_parser = commands.add_parser("validate", help="validate and normalize a policy")
    validate_parser.add_argument("policy")
    validate_parser.add_argument("--output")
    validate_parser.set_defaults(handler=validate)

    compare_parser = commands.add_parser("compare", help="compare JSON documents")
    compare_parser.add_argument("before")
    compare_parser.add_argument("after")
    compare_parser.add_argument("policy")
    compare_parser.add_argument("--explain-out")
    compare_parser.add_argument("--patch-out")
    compare_parser.add_argument("--include-tests", action="store_true")
    compare_parser.add_argument("--fail-on-difference", action="store_true")
    compare_parser.set_defaults(handler=compare)
    return root


def main(argv=None):
    arguments = parser().parse_args(argv)
    if not hasattr(arguments, "handler"):
        parser().print_help()
        return 2
    return arguments.handler(arguments)


if __name__ == "__main__":
    sys.exit(main())
