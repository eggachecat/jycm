#!/usr/bin/env python3
"""Install the bundled Agent Skill for Codex, Claude, or project agents."""

import argparse
import shutil
from datetime import datetime
from pathlib import Path


SKILL_NAME = "jycm-business-diff"


def target_path(client, project=None):
    if project:
        root = Path(project).expanduser().resolve()
        folder = ".claude/skills" if client == "claude" else ".agents/skills"
        return root / folder / SKILL_NAME
    home = Path.home()
    folder = ".claude/skills" if client == "claude" else ".codex/skills"
    return home / folder / SKILL_NAME


def install(args):
    source = Path(__file__).resolve().parents[1]
    target = target_path(args.client, args.project)
    if target.exists():
        if not args.force:
            raise SystemExit("Target already exists: {} (use --force to back it up)".format(target))
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = target.with_name("{}.backup-{}".format(SKILL_NAME, stamp))
        shutil.move(str(target), str(backup))
        print("Backed up existing skill to {}".format(backup))
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(str(source), str(target), ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print("Installed {} to {}".format(SKILL_NAME, target))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client", choices=("codex", "claude", "agents"), required=True)
    parser.add_argument("--project", help="install at project scope instead of user scope")
    parser.add_argument("--force", action="store_true", help="back up and replace an existing install")
    args = parser.parse_args()
    if args.client == "agents" and not args.project:
        parser.error("--client agents requires --project")
    return install(args)


if __name__ == "__main__":
    raise SystemExit(main())
