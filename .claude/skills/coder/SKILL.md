---
name: coder
description: Manage Coder workspaces and templates using the official `coder` CLI. Use when the user wants to list, create, start, stop, restart, delete, ssh into, or update workspaces; push or list templates; manage tokens; forward ports. Env vars required: CODER_URL and CODER_SESSION_TOKEN (NOT CODER_TOKEN — that's only for workspace agents).
---

# Coder CLI Skill

Binary: `/usr/local/bin/coder`
Auth: `CODER_URL` + `CODER_SESSION_TOKEN`

## Setup

```bash
export CODER_URL=https://46-225-180-131.nip.io
export CODER_SESSION_TOKEN=e1d8ceca0b-XsSN6OaB0tvdRK4xsoIeUQ
```

Or interactively: `coder login <url>`

## Workspaces

```bash
coder list                                      # list all workspaces
coder create <name>                             # create (prompts template + params)
coder start <workspace>                         # start stopped workspace
coder stop <workspace>                          # stop workspace
coder restart <workspace>                       # restart (keeps current template version)
coder update <workspace> --always-prompt=false  # update to latest template version
coder delete <workspace>                        # permanently delete
coder show <workspace>                          # show resources and agents
coder rename <workspace> <new-name>
coder ssh <workspace>                           # open shell
coder ssh <workspace> -- <cmd>                  # run command
coder port-forward <workspace> --tcp 8080:8080
coder schedule <workspace> start "Mon-Fri 09:00"
```

**`restart` vs `update`**: `restart` keeps old template version; `update` applies new one.

## Templates

```bash
coder templates list
coder templates push <name> -d <dir> --yes      # publish new version
coder templates versions list <name>
```

## Tokens

```bash
coder tokens list
coder tokens create --name <name>
coder tokens remove <token-id>
```

## Notes

- Full CLI reference: `references/cli-reference.md`
- Template dir (local): `/tmp/coder-template/`
- Template dir (server): `/opt/coder-templates/dev-workspace/`
