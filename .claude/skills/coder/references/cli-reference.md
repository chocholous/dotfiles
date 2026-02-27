# Coder CLI Reference

Source: https://coder.com/docs/reference/cli

## Global Flags

| Flag | Env var | Description |
|------|---------|-------------|
| `--url` | `CODER_URL` | Deployment URL |
| `--token` | `CODER_SESSION_TOKEN` | Auth token |
| `--verbose` | | Verbose output |
| `--no-version-warning` | | Suppress version mismatch warnings |

## coder list

```
coder list [flags]
  -c, --column strings   Columns to display (default: workspace,template,status,last_built,current_version,outdated,starts_at,stops_after)
  -o, --output string    Output format: table|json (default "table")
  --all                  Show workspaces from all users (admins only)
  --search string        Filter by name/owner/status
```

## coder create

```
coder create [flags] [workspace name]
  --template string         Template name
  --start-at string         Autostart schedule
  --stop-after duration     Autostop after
  --parameter strings       Template parameters as key=value
  --rich-parameter-file     YAML file with parameter values
  --copy-parameters-from    Workspace to copy params from
```

## coder start / stop / restart

```
coder start <workspace>
coder stop <workspace>
coder restart <workspace>
  --reason string   Reason for the action (optional)
```

## coder update

```
coder update <workspace> [flags]
  --always-prompt=false   Don't prompt for immutable params
  --parameter strings     Override parameters
```

## coder delete

```
coder delete <workspace> [flags]
  --yes   Skip confirmation
```

## coder show

```
coder show <workspace>
  -o, --output string   table|json
```

## coder ssh

```
coder ssh <workspace> [command] [flags]
  -A                      Forward SSH agent
  --forward-gpg           Forward GPG agent
  --identity-agent string Agent socket path
  --log-dir string        Log directory
  --no-wait               Connect without waiting for startup
  --remote-forward string Remote port forward
  --stdio                 Use stdio (for proxying)
  --wait                  Wait for startup (default)
```

## coder port-forward

```
coder port-forward <workspace> [flags]
  --tcp strings    TCP ports: local:remote or port
  --udp strings    UDP ports
  --unix strings   Unix sockets

# Examples:
coder port-forward myworkspace --tcp 8080        # forward 8080
coder port-forward myworkspace --tcp 5432:5432   # postgres
coder port-forward myworkspace --tcp 8080,9090   # multiple
```

## coder rename

```
coder rename <workspace> <new name> [flags]
  --yes   Skip confirmation
```

## coder schedule

```
coder schedule show <workspace>
coder schedule start <workspace> <schedule>    # e.g. "Mon-Fri 09:00"
coder schedule stop <workspace> <duration>    # e.g. 8h
coder schedule override-stop <workspace> <duration>
```

## coder templates

```
coder templates list [flags]
  -c, --column strings   Columns to display
  -o, --output string    table|json

coder templates push [template] [flags]
  -d, --directory string   Template directory (default: current dir)
  --yes                    Skip confirmation
  --name string            Version name
  --message string         Version message
  --provisioner-tag strings  Provisioner tags
  --activate               Activate after push (default true)
  --var strings            Terraform variables as key=value
  --var-file string        Terraform .tfvars file
  -y, --yes                Skip prompts

coder templates versions list <template> [flags]
  -o, --output string   table|json

coder templates versions activate <template> <version>
```

## coder tokens

```
coder tokens list [flags]
  -c, --column strings
  -o, --output string   table|json
  --all                 Include expired tokens

coder tokens create [flags]
  --name string       Token name
  --lifetime duration Token lifetime (default: 30d, max: 1y)
                      Use large value for automation: 8760h = 1 year

coder tokens remove <token-id>
```

## coder login

```
coder login <url> [flags]
  --first-user-email string
  --first-user-password string
  --first-user-username string
  --use-token-as-session   Use provided token directly (skip new session creation)
```

## coder external-auth

```
coder external-auth list
coder external-auth access-token <provider>   # Get token for GitHub etc.
```

## coder publickey

```
coder publickey   # Output public key for Git operations in workspaces
```
