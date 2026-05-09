# 20 — Plan Revision

When the user provides reviewer feedback (textual letter, list of comments, or a Markdown file with the review), generate the project file.

## 1. Acquire Reviewer Identity

Ask the user unless already supplied:

> What should I call this reviewer? I will use a slug for filenames and suggested commit messages, for example `peer-1`, `editor`, or `reviewer-a`.

## 2. Parse Feedback Into Discrete Points

Split the reviewer's letter into atomic points. One point equals one actionable observation, even if the reviewer wraps several together. Each point should map to:

- an article section, such as *Introduction* or *Methodology — Sample*;
- a priority level (`high`, `medium`, `low`);
- a verbatim quote of the reviewer's words.

Number points progressively. If one reviewer sentence covers multiple sections, split it into multiple points.

## 3. Generate `revisions/<reviewer-slug>/revision-plan-vN.md`

Use `templates/revision-plan.md` and substitute:

- `{{REVIEWER}}` — full name or slug;
- `{{VERSION}}` — article version, such as `9`;
- `{{ARTICLE_PATH}}` — relative path;
- `{{EDITORIAL_LIMIT}}`, `{{LIMIT_UNIT}}` — from `.env`;
- `{{INITIAL_COUNT}}` — output of `scripts/char_count.py --limit-from-env`;
- `{{ARTICLE_LANG}}` — from setup;
- `{{NORMS_PATH}}` — from `.env`.

Then for each point, write a section under `## Point-by-Point Revision` with all subfields populated **except** `Decision`, which stays `To decide`, and the actual proposal text, which is filled later in `30-iterate-points.md`.

Populate the checklist at the bottom:

```text
| # | Point | Section | Status in v<N> | Priority | Decision |
```

## 4. Confirm In Chat

The skill writes the project file to disk. **The user controls git**; no auto-commit. If asked, the suggested commit message is:

```text
revision(<slug>): start — N points planned
```

Then in chat:

```text
Revision plan created: <path>

N points planned:
1. <title> — <section> (priority <high|medium|low>)
2. ...

Start from point 1? (yes / choose point N / postpone)
```

Wait for the user.
