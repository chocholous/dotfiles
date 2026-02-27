# Issue Reporting Guide

When a serious problem occurs that the user cannot resolve, offer to create a GitHub issue on the skill's marketplace repository.

## Repository

`chocholous/skill-checker`

## When to report

Only report **structural problems** — things that indicate the skill, mcpc, or the platform behave differently than documented:

- mcpc tool returns an error that contradicts the SKILL.md documentation
- An Actor listed in a use-case file no longer exists, is deprecated, or has a renamed/changed identifier
- `fetch-actor-details` output fields or `call-actor` response structure changed (schema drift between mcpc and platform)
- mcpc CLI syntax changed (arguments, flags, session commands)
- Authentication flow broken in a way not covered by error handling section

## When NOT to report

- Actor run returns zero results (likely wrong input — retry with different values)
- Actor run fails with timeout or memory errors (user's plan limits or Actor-specific issue)
- User's Apify token expired or plan limit exceeded
- Network errors or transient failures
- Actor returns unexpected data format (that's the Actor author's problem, not the skill's)

## Issue template

```bash
gh issue create --repo chocholous/skill-checker \
  --title "<concise problem summary>" \
  --label "skill-bug" \
  --body "$(cat <<'EOF'
## Problem

<1-2 sentences: what happened vs what was expected>

## Reproduction

- **mcpc version**: <output of `mcpc --version`>
- **Skill section**: <which part of SKILL.md or use-case file is affected>
- **mcpc command**: `<the exact command that was run>`
- **Expected behavior**: <what SKILL.md says should happen>
- **Actual behavior**: <what actually happened>

## Error output

```
<relevant error message or unexpected response, truncated to essentials>
```

## Context

- Actor: `<actor fullName if applicable>`
- Session: `<@apify or @apify-docs>`
- Timestamp: <ISO timestamp>
EOF
)"
```

## Workflow

1. Summarize the problem to the user in plain language
2. Explain this looks like a skill/platform issue, not a user error
3. Ask: "Do you want me to create an issue on the skill repository so this can be fixed?"
4. Only proceed with `gh issue create` if the user confirms
5. Show the user the created issue URL
