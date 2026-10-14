# Computer-use diagnosis and verification

Date: 2026-10-13, America/Los_Angeles.

Earlier calls returned `trusted Node process exited unexpectedly; kernel reset`.
On this investigation, a minimal Node REPL call succeeded, then importing `@oai/sky`
succeeded, then `sky.list_windows()` returned native windows. Bringing Battle.net
forward and refreshing `get_window_state` produced a clear screenshot.
Native window enumeration, activation and screenshot capture are verified. Clicking,
typing and WoW in-game inspection have not been tested; no game was launched.

The first capture before bringing the target forward showed the foreground chat
window; a capture immediately after activation contained redraw artifacts. A refreshed
capture was clear. Observe a stable target window before using screenshot coordinates.

## Startup evidence

`C:/Users/user/.codex/.sandbox/setup_error.json` reported:

```text
code: helper_unknown_error
message: setup refresh had errors
```

The sandbox log for 2026-10-13 at 15:45:50 and 15:45:53 recorded failed runtime
read/execute validation on the bundled `cua_node` runtime's `node_repl.exe`:

```text
open ACL target for root-only update:
The process cannot access the file because it is being used by another process.
(os error 32)
```

This establishes a file-sharing/locking failure during sandbox setup and is consistent
with the earlier startup error. It does not identify the locking process or establish
why the lock cleared. The supplied computer-use plugin changed from version
26.1002.52244 to 26.1007.21434 between attempts; causation is not established.
No sandbox configuration, permissions, plugin installation, or security settings were
changed during this investigation.

## Recovery sequence if it recurs

Use the current installed computer-use skill's initialization and recovery instructions.
Check a minimal Node call, package import, window enumeration, then stable target capture
separately so the failure stage is explicit. If startup repeatedly fails, inspect the
current sandbox log for a matching timestamp. Restarting the desktop app may release a
stale runtime lock, but has not been established as the fix for this incident.
Do not manually spawn computer-use helpers, bypass permission checks, or change ACLs
to work around it.

## Forever build observation

The verified Battle.net screenshot showed **WoW: Forever – Beta**, installed launcher
version **1.60.1.70338**, matching our pinned Forever UI mirror's version.
The game itself was not running in the enumerated windows. We still need in-game
`GetBuildInfo()` and API/scenario verification before claiming live-client compatibility.
