#!/usr/bin/env python3
"""Post pmpp results as a PR comment (safe, no job failure).

This script is executed within the workflow and uses the runtime
`GITHUB_TOKEN` to post a comment when findings are present. It is
intentionally minimal and uses only the standard library.
"""
import os
import json
import sys
import urllib.request


def main():
    event_path = os.environ.get('GITHUB_EVENT_PATH')
    if not event_path:
        print('GITHUB_EVENT_PATH not set; skipping')
        return 0

    try:
        with open(event_path, 'r', encoding='utf-8') as f:
            ev = json.load(f)
    except Exception as e:
        print('Failed to read event payload:', e)
        return 1

    pr = ev.get('number') or (ev.get('pull_request') or {}).get('number')
    if not pr:
        print('No pull request number found in event payload; skipping comment')
        return 0

    try:
        data = json.load(open('pmpp-results.json', 'r', encoding='utf-8'))
    except Exception as e:
        print('Failed to read pmpp-results.json:', e)
        return 1

    count = len(data.get('findings', []))
    if count == 0:
        print('pmpp found no issues')
        return 0

    short = json.dumps({'findings': data.get('findings')[:10], 'count': count}, indent=2)
    owner_repo = os.environ.get('GITHUB_REPOSITORY', '')
    if '/' in owner_repo:
        owner, repo = owner_repo.split('/', 1)
    else:
        print('GITHUB_REPOSITORY missing or malformed; skipping')
        return 1

    run_url = os.environ.get('GITHUB_SERVER_URL', 'https://github.com')
    run_id = os.environ.get('GITHUB_RUN_ID', '')
    if run_id:
        run_url = f"{run_url}/{owner}/{repo}/actions/runs/{run_id}"

    body = (
        f"pmpp found {count} potential issue(s) in this PR.\n\n"
        f"Summary:\n\n```json\n{short}\n```\n\n"
        f"Full results and artifacts: {run_url}"
    )

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr}/comments"
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print('GITHUB_TOKEN not available; cannot post comment')
        return 1

    req = urllib.request.Request(
        url,
        data=json.dumps({'body': body}).encode('utf-8'),
        headers={
            'Authorization': f'bearer {token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            print('Comment posted, status', resp.status)
    except Exception as e:
        print('Failed to post comment:', e)
        return 1

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
