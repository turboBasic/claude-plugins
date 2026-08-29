#!/usr/bin/env python3
# Applies one GitHub repository baseline, idempotently. Every call goes through `gh api`, so
# authentication, hosts, retries and pagination stay gh's problem and this file imports nothing
# outside the standard library. See docs/decisions/0002-*.md in the marketplace repository.
import argparse
import json
import subprocess
import sys

RULESET_NAME = "protect-default-branch"

# Not read off any repository: the three rulesets that exist across the account are named three
# different things, so the name is this command's own ruling and the key it matches on.
BASELINE = {
    "has_issues": True,
    "has_wiki": False,
    "has_projects": True,
    "has_discussions": False,
    "allow_squash_merge": True,
    "allow_rebase_merge": True,
    "allow_merge_commit": False,
    "allow_auto_merge": False,
    "allow_update_branch": False,
    "delete_branch_on_merge": True,
    "squash_merge_commit_title": "COMMIT_OR_PR_TITLE",
    "squash_merge_commit_message": "COMMIT_MESSAGES",
    "web_commit_signoff_required": False,
}

DRY = False


def gh(path, method="GET", body=None, allow_fail=False):
    # A dry run must reach no write, and this is the only place a request is issued.
    if DRY and method != "GET":
        return {}
    cmd = ["gh", "api", "--method", method, path]
    if body is not None:
        cmd += ["--input", "-"]
    run = subprocess.run(
        cmd,
        input=json.dumps(body) if body is not None else None,
        capture_output=True,
        text=True,
        check=False,
    )
    if run.returncode:
        if allow_fail:
            return None
        sys.exit(f"gh api {method} {path} failed:\n{run.stderr.strip()}")
    return json.loads(run.stdout) if run.stdout.strip() else {}


def desired_settings(description=None, homepage=None):
    out = dict(BASELINE)
    if description is not None:
        out["description"] = description
    if homepage is not None:
        out["homepage"] = homepage
    return out


def security_settings(public):
    # The API rejects secret scanning on a private repository without GHAS, which would fail the
    # whole run on its last call. Public repositories get it for free.
    if not public:
        return None
    return {
        "secret_scanning": {"status": "enabled"},
        "secret_scanning_push_protection": {"status": "enabled"},
    }


def desired_ruleset(status_checks=()):
    rules = [
        {"type": "deletion"},
        {"type": "non_fast_forward"},
        {"type": "required_linear_history"},
    ]
    if status_checks:
        rules.append(
            {
                "type": "required_status_checks",
                "parameters": {
                    "strict_required_status_checks_policy": False,
                    "do_not_enforce_on_create": False,
                    "required_status_checks": [{"context": c} for c in status_checks],
                },
            }
        )
    return {
        "name": RULESET_NAME,
        "target": "branch",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        # RepositoryRole 5 is the repository admin. Without the bypass, required linear history
        # locks the sole owner out of the force-push that produces it.
        "bypass_actors": [
            {"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always"}
        ],
        "rules": rules,
    }


def ruleset_shape(ruleset):
    # GitHub returns ids, timestamps and links that no desired state can match, so equality is
    # taken over the fields this command actually sets.
    return {
        "enforcement": ruleset.get("enforcement"),
        "conditions": ruleset.get("conditions"),
        "bypass_actors": [
            {k: a.get(k) for k in ("actor_id", "actor_type", "bypass_mode")}
            for a in ruleset.get("bypass_actors") or []
        ],
        "rules": sorted(
            (
                {"type": r["type"], "parameters": r.get("parameters")}
                for r in ruleset["rules"]
            ),
            key=lambda r: r["type"],
        ),
    }


def blank(value):
    return value in (None, "")


def diff(current, desired):
    out = {}
    for key, want in desired.items():
        have = current.get(key)
        if blank(have) and blank(want):
            continue
        if have != want:
            out[key] = (have, want)
    return out


def report(pairs):
    for key, (have, want) in sorted(pairs.items()):
        print(f"  {key}: {json.dumps(have)} -> {json.dumps(want)}")


def resolve(target):
    if "/" in target:
        owner, name = target.split("/", 1)
        return owner, name
    return gh("user")["login"], target


def create(owner, name, public, description):
    me = gh("user")["login"]
    path = "user/repos" if owner == me else f"orgs/{owner}/repos"
    body = {"name": name, "private": not public}
    if description:
        body["description"] = description
    gh(path, "POST", body)
    print(f"created {owner}/{name} ({'public' if public else 'private'})")


def apply(args):
    owner, name = resolve(args.target)
    slug = f"{owner}/{name}"
    repo = gh(f"repos/{slug}", allow_fail=True)
    if repo is None:
        if not args.create:
            sys.exit(f"{slug} does not exist. Pass --create to create it.")
        create(owner, name, args.public, args.description)
        repo = gh(f"repos/{slug}")
    public = repo.get("visibility") == "public"

    settings = desired_settings(args.description, args.homepage)
    security = security_settings(public)
    if security:
        settings["security_and_analysis"] = security
    current = dict(repo)
    if security:
        current["security_and_analysis"] = {
            k: {
                "status": (repo.get("security_and_analysis") or {})
                .get(k, {})
                .get("status")
            }
            for k in security
        }
    changes = diff(current, settings)

    topic_change = None
    if args.topic:
        have = sorted(repo.get("topics") or [])
        want = sorted(set(args.topic))
        if have != want:
            topic_change = (have, want)

    alerts = gh(f"repos/{slug}/vulnerability-alerts", allow_fail=True) is not None
    fixes = bool(
        (gh(f"repos/{slug}/automated-security-fixes", allow_fail=True) or {}).get(
            "enabled"
        )
    )

    want_ruleset = desired_ruleset(args.status_check)
    existing = next(
        (r for r in gh(f"repos/{slug}/rulesets") if r.get("name") == RULESET_NAME), None
    )
    ruleset_state = "absent"
    if existing:
        full = gh(f"repos/{slug}/rulesets/{existing['id']}")
        ruleset_state = (
            "current" if ruleset_shape(full) == ruleset_shape(want_ruleset) else "stale"
        )

    print(slug)
    report(changes)
    if topic_change:
        report({"topics": topic_change})
    if not alerts:
        report({"vulnerability_alerts": (False, True)})
    if not fixes:
        report({"automated_security_fixes": (False, True)})
    if ruleset_state != "current":
        report({"ruleset": (ruleset_state, RULESET_NAME)})
    pending = (
        bool(changes or topic_change)
        or not alerts
        or not fixes
        or ruleset_state != "current"
    )
    if not pending:
        print("  nothing to change")
        return
    if DRY:
        print("  dry run: nothing was written")
        return

    if changes:
        gh(f"repos/{slug}", "PATCH", settings)
    if topic_change:
        gh(f"repos/{slug}/topics", "PUT", {"names": topic_change[1]})
    if not alerts:
        gh(f"repos/{slug}/vulnerability-alerts", "PUT")
    if not fixes:
        gh(f"repos/{slug}/automated-security-fixes", "PUT")
    if ruleset_state == "absent":
        gh(f"repos/{slug}/rulesets", "POST", want_ruleset)
    elif ruleset_state == "stale":
        gh(f"repos/{slug}/rulesets/{existing['id']}", "PUT", want_ruleset)
    print("  applied")


def self_check():
    base = desired_settings()
    assert base["allow_merge_commit"] is False
    assert base["allow_squash_merge"] is True and base["allow_rebase_merge"] is True
    assert base["has_wiki"] is False and base["has_discussions"] is False
    # Merge commits are off, so their message template is never sent.
    assert "merge_commit_title" not in base and "merge_commit_message" not in base
    assert "description" not in base and "homepage" not in base
    assert desired_settings(description="x")["description"] == "x"

    assert security_settings(public=False) is None
    assert security_settings(public=True)["secret_scanning"]["status"] == "enabled"

    solo = desired_ruleset()
    assert [r["type"] for r in solo["rules"]] == [
        "deletion",
        "non_fast_forward",
        "required_linear_history",
    ]
    assert solo["conditions"]["ref_name"]["include"] == ["~DEFAULT_BRANCH"]
    assert solo["bypass_actors"][0]["actor_id"] == 5
    checked = desired_ruleset(["CI"])
    assert len(checked["rules"]) == 4
    assert checked["rules"][3]["parameters"]["required_status_checks"] == [
        {"context": "CI"}
    ]

    # An unset homepage arrives as "" from the API and None from the baseline: not a change.
    assert diff({"homepage": ""}, {"homepage": None}) == {}
    assert diff({"has_wiki": True}, {"has_wiki": False}) == {"has_wiki": (True, False)}
    # Rule order and the ids GitHub adds must not read as drift.
    live = dict(desired_ruleset(), id=1, node_id="x")
    live["rules"] = list(reversed(live["rules"]))
    assert ruleset_shape(live) == ruleset_shape(desired_ruleset())
    assert ruleset_shape(desired_ruleset(["CI"])) != ruleset_shape(desired_ruleset())

    assert resolve("owner/name") == ("owner", "name")
    print("self-check passed")


def main():
    parser = argparse.ArgumentParser(
        description="Apply the GitHub repository baseline."
    )
    parser.add_argument("target", nargs="?", help="<name> or <owner>/<name>")
    parser.add_argument(
        "--create", action="store_true", help="create it if it does not exist"
    )
    parser.add_argument(
        "--public", action="store_true", help="create it public; default private"
    )
    parser.add_argument("--description")
    parser.add_argument("--homepage")
    parser.add_argument(
        "--topic", action="append", default=[], help="repeatable; replaces the set"
    )
    parser.add_argument(
        "--status-check", action="append", default=[], help="repeatable check name"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="report the diff, write nothing"
    )
    parser.add_argument(
        "--self-check", action="store_true", help="assert over the pure builders"
    )
    args = parser.parse_args()

    if args.self_check:
        self_check()
        return
    if not args.target:
        parser.error("target is required")
    global DRY
    DRY = args.dry_run
    apply(args)


if __name__ == "__main__":
    main()
