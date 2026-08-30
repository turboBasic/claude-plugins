#!/usr/bin/env python3
# Applies one GitHub repository baseline, idempotently. Every call goes through `gh api`, so
# authentication, hosts, retries and pagination stay gh's problem and this file imports nothing
# outside the standard library. See docs/decisions/0002-*.md in the marketplace repository.
import argparse
import json
import subprocess
import sys

# Not read off any repository, and the key a ruleset is matched on: the rulesets that exist across an
# account are named whatever each was named, so this is the baseline's own ruling.
RULESET_NAME = "protect-default-branch"

# Every value here is the baseline's ruling, not a reading of anyone's tree — including the ones an
# owner might have gone the other way on, `has_projects` above all. A baseline exists to stop the
# negotiation, so only the per-repository facts get flags: description, homepage, topics, checks.
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
    # taken over the fields this command sets. Rules arrive in GitHub's own order, hence the sort.
    return {
        "enforcement": ruleset.get("enforcement"),
        "conditions": ruleset.get("conditions"),
        "bypass_actors": ruleset.get("bypass_actors") or [],
        "rules": sorted(ruleset["rules"], key=lambda r: r["type"]),
    }


def diff(current, desired):
    out = {}
    for key, want in desired.items():
        have = current.get(key)
        # An unset description or homepage arrives as "" from the API and None from the baseline.
        if have in (None, "") and want in (None, ""):
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
    visibility = "public" if public else "private"
    if DRY:
        print(f"  create: absent -> {owner}/{name} ({visibility})")
        return
    me = gh("user")["login"]
    path = "user/repos" if owner == me else f"orgs/{owner}/repos"
    body = {"name": name, "private": not public}
    if description:
        body["description"] = description
    gh(path, "POST", body)
    print(f"created {owner}/{name} ({visibility})")


def actions(slug, repo, public, unborn, args):
    # One entry per endpoint that differs: what it reads now, and the request that closes the gap.
    # Each concern is declared once, so the report and the writes cannot disagree on what is pending.
    # `unborn` is a suppressed --create: nothing exists to query, so every state is the fresh one.
    out = []

    settings = desired_settings(args.description, args.homepage)
    security = security_settings(public)
    scanning = repo.get("security_and_analysis") or {}
    # GitHub reports five keys here and this sets two, so a whole-field compare always differs.
    # Send the field only when one of the two it sets is not already enabled.
    if security and not all(
        scanning.get(k, {}).get("status") == "enabled" for k in security
    ):
        settings["security_and_analysis"] = security
    changes = diff(repo, settings)
    if changes:
        out.append((changes, ("PATCH", f"repos/{slug}", settings)))

    if args.topic:
        topics_now = sorted(repo.get("topics") or [])
        topics_want = sorted(set(args.topic))
        if topics_now != topics_want:
            out.append(
                (
                    {"topics": (topics_now, topics_want)},
                    ("PUT", f"repos/{slug}/topics", {"names": topics_want}),
                )
            )

    alerts = f"repos/{slug}/vulnerability-alerts"
    if unborn or gh(alerts, allow_fail=True) is None:
        out.append(({"vulnerability_alerts": (False, True)}, ("PUT", alerts, None)))
    fixes = f"repos/{slug}/automated-security-fixes"
    if unborn or not (gh(fixes, allow_fail=True) or {}).get("enabled"):
        out.append(({"automated_security_fixes": (False, True)}, ("PUT", fixes, None)))

    # Rulesets are a paid feature on a private repository under a personal account, where the list
    # 403s rather than coming back empty — and private is what --create makes by default.
    listed = [] if unborn else gh(f"repos/{slug}/rulesets", allow_fail=True)
    if listed is None:
        print(
            "  note: rulesets unavailable here — the default branch will stay unprotected"
        )
        return out
    want = desired_ruleset(args.status_check)
    existing = next((r for r in listed if r.get("name") == RULESET_NAME), None)
    if existing is None:
        out.append(
            (
                {"ruleset": ("absent", RULESET_NAME)},
                ("POST", f"repos/{slug}/rulesets", want),
            )
        )
    else:
        path = f"repos/{slug}/rulesets/{existing['id']}"
        if ruleset_shape(gh(path)) != ruleset_shape(want):
            out.append(({"ruleset": ("stale", RULESET_NAME)}, ("PUT", path, want)))
    return out


def apply(args):
    owner, name = resolve(args.target)
    slug = f"{owner}/{name}"
    print(slug)
    repo = gh(f"repos/{slug}", allow_fail=True)
    fresh = repo is None
    if fresh:
        if not args.create:
            sys.exit(f"{slug} does not exist. Pass --create to create it.")
        create(owner, name, args.public, args.description)
        # Under --dry-run the POST was suppressed, so there is nothing to GET back: the baseline is
        # reported against an empty repository at the visibility --create would have given it.
        repo = {} if DRY else gh(f"repos/{slug}")
    public = args.public if fresh else repo.get("visibility") == "public"
    if not fresh and args.public and not public:
        print(
            "  note: --public does not flip an existing private repository; left as it was"
        )
    if not public:
        print(
            "  note: secret scanning skipped — the API rejects it on a private repo without GHAS"
        )

    pending = actions(slug, repo, public, fresh and DRY, args)
    for pairs, _ in pending:
        report(pairs)
    if not pending:
        print("  nothing to change")
        return
    if DRY:
        print("  dry run: nothing was written")
        return
    for _, (method, path, body) in pending:
        gh(path, method, body)
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
