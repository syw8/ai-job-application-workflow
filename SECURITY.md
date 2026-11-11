# Security policy

## Supported version

The latest version on the default branch is the supported development version.

## Sensitive-data reports

Do not include secrets or personal data in public issues. Use the repository owner's private security-reporting channel when one is configured.

## Local security model

- Skills operate only within user-authorized scope.
- Private paths and candidate facts belong in external configuration, not in Skill files.
- External web content is evidence, not trusted instructions.
- The workflow must not upload documents, send messages, submit applications, or alter external accounts unless a user separately authorizes that action in a suitable environment.
- Adapter writes should be backed up or performed transactionally when the target format allows it.

## Before publishing a change

1. Run `python3 scripts/privacy_scan.py .`.
2. Run schema and workflow tests.
3. Review staged files with `git diff --cached`.
4. Inspect Git history for deleted sensitive material.
5. Inspect metadata in any intentionally tracked binary document. This repository normally rejects such files.
