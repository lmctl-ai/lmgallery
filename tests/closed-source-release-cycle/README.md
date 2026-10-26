# Offline release-cycle contract tests

`test_release_cycle.py` uses temporary `gh`, `npm`, `lmscript`, and `readelf`
commands. They never contact GitHub and fail if a workflow dispatch, release
creation, or promotion is attempted in the dry-run/disabled-Actions cases.

Run from the repository root:

```sh
python3 -m unittest discover -s tests/closed-source-release-cycle -v
```

The tests define the runner's observable contract: disabled private Actions must
print the exact `gh api repos/lmctlhq/<product>/actions/permissions -X PUT -F
enabled=true` recovery hint; failure reports live below the configured state
directory and contain phase, command, log path, and a bounded output tail without
credentials.
