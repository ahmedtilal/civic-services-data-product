# Issue tracker: GitHub Issues

Issues for this repo live in GitHub Issues for `ahmedtilal/civic-services-data-product`. Use the `gh` CLI.

## Conventions

- One milestone per part of the series: `part-01-design-and-requirements` through `part-08-review`, named like the branches in [the roadmap](../roadmap.md).
- Each task is one issue in the milestone of the part it belongs to. Label it `part-NN` as well.
- The issue body says what the part should contain and ends with a "Done when" checklist.
- Issues are public. Do not put credentials, real project identifiers, or source row data in them.
- Local scratch notes may live in `.scratch/`, which is gitignored. They are not the tracker.

## When a skill says "publish to the issue tracker"

Create a GitHub issue with `gh issue create --title ... --body ... --milestone <part> --label <part-NN>`.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number>`. The user will normally pass the issue number directly.

## Wayfinding operations

Used by `/wayfinder`.

- **Map**: a tracking issue labelled `map` whose body holds the Notes / Decisions-so-far / Fog.
- **Child ticket**: an issue that links to the map, with the question in the body. A `type:` label records the ticket type (`research`/`prototype`/`grilling`/`task`).
- **Blocking**: a `Blocked by: #N, #N` line near the top of the body. A ticket is unblocked when every listed issue is closed.
- **Frontier**: list open issues in the milestone with `gh issue list --milestone <part> --state open`; take the lowest-numbered unblocked, unassigned one.
- **Claim**: assign it to yourself (`gh issue edit <n> --add-assignee @me`) before any work.
- **Resolve**: comment the answer under an `## Answer` heading, close the issue, then append a context pointer (gist + link) to the map's Decisions-so-far.
