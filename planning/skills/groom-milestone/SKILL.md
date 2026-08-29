---
name: groom-milestone
description: Execute a backlog reading as product owner - move, split, cut, resize and renumber issues, leaving a record of what moved. Use when asked to reshape a milestone, its scope or its issues.
---

# Groom a milestone

**Acting as product owner.** It owns a milestone's composition and an issue's scope, and it never touches
the source tree: a milestone is reshaped by changing issues, never the code they describe.

**This skill executes a reading; it does not produce one.** `review-backlog` owns the reading's shape;
invoke it where one is not in hand, and execute the owner's ruling rather than re-deriving it.

## Executing

1. **Land the content, not a description of it.** A draft file, a measured number, a schema: paste it
   into the thread. A scratch file is lost by the next session.
2. **A cut issue closes with where its parts went**, each named, written before the issue closes.
3. **A body rewritten says what is true now.** `write-issue` holds the shape of both an issue body and an
   epic's.
4. **Relationships move through the API, never through a body.** Changing an issue's milestone does not
   move its parent link, and a prose `Blocked by:` line left behind is the copy that rots.
5. **Report what the board now costs**: which milestone holds what, and the longest remaining dependency
   chain.

## GitHub mechanics

**Both relationship APIs take the numeric issue id, not the issue number** — `gh api
repos/:owner/:repo/issues/<n> -q .id`. Passing the number silently attaches the wrong issue.

| Change | Call |
| --- | --- |
| Move an issue | `gh issue edit <n> --milestone '<title>'` |
| Retitle a milestone | `gh api -X PATCH repos/:owner/:repo/milestones/<m> -f title='<title>'` |
| Read children | `gh api repos/:owner/:repo/issues/<n>/sub_issues` |
| Attach a child | `gh api -X POST repos/:owner/:repo/issues/<n>/sub_issues -F sub_issue_id=<id>` |
| Detach a child | `gh api -X DELETE repos/:owner/:repo/issues/<n>/sub_issue -F sub_issue_id=<id>` |
| Read blockers | `gh api repos/:owner/:repo/issues/<n>/dependencies/{blocked_by,blocking}` |
| Add a blocker | `gh api -X POST repos/:owner/:repo/issues/<n>/dependencies/blocked_by -F issue_id=<id>` |
| Drop a blocker | `gh api -X DELETE repos/:owner/:repo/issues/<n>/dependencies/blocked_by/<id>` |

Read a raw body with `gh issue view <n> --json body -q .body`; write one from a file with `gh issue edit
<n> --body-file <path>`, so no rewrite is smuggled through a shell quote.

## What earns a comment

**A comment narrating backlog mechanics is noise, and future agents read it as context.**

- **Delete:** milestone moves, "the link was dead", "renamed to", any before-and-after account of how an
  issue changed. `git log` and the body's current state own that.
- **Keep:** a scope cut, a measured figure, a dependency order, a draft artefact, a ruling and what lost
  to it, an answer to a scope proposal above it — unanswered, the proposal reads as still open.
- **Trim rather than delete** where a real kernel sits wrapped in that narration.

## Executing a renumber

- **Retitle milestones from the highest number downwards**, so no two collide on a title.
- **An epic follows its theme, not its number.** A milestone whose content is unchanged keeps its epic
  and takes a title edit.
- **Closed issues stay where they are.** They ship in that release whichever milestone labels them. Say
  so in the epic body rather than leaving the mismatch unexplained.
- **Re-parent sub-issues explicitly.** An issue holds one parent, so the attach is refused unless the old
  link goes first — either detach then attach, or pass `-F replace_parent=true` on the attach.
- **Sweep for pointers to anything deleted** — a comment that was only that link goes too.
- **Repoint the dependency graph out of a closed issue** before finishing. An issue closed as superseded
  never closes as done, so a dependency on it blocks its successors for good.
