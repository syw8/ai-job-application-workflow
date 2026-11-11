# Privacy policy and local-data model

## Scope

This repository is a local, skills-only workflow package. It does not include a hosted service, analytics, an MCP server, or a data collection backend. The repository maintainers do not receive candidate data through the code in this project.

## Data the workflow may process locally

When a user invokes the skills, the user's chosen agent environment may process candidate profiles, CVs, cover letters, job descriptions, application records, local file paths, and review decisions. These are sensitive employment-related materials and should remain in user-controlled private storage.

## Data minimization

- Provide only the source document and target information needed for the current task.
- Keep candidate profiles and local configuration outside version control.
- Do not place real application material in this repository, examples, tests, issues, pull requests, or CI artifacts.
- Do not add credentials, government identifiers, payment data, health data, or unrelated personal records.

## Storage and recipients

This project itself stores no submitted user data. Storage, retention, model processing, and recipients depend on the user's selected agent product, connected tools, local filesystem, and organizational policies. Users must review those terms separately.

## External scheduled discovery

Scheduled job discovery is configured outside this repository. Its searches, results, retention, and notifications are governed by the scheduling product and any connected services. GitHub does not execute the documented discovery workflow.

## User controls

Users choose which files and folders the agent may access, which adapters are enabled, and whether generated changes are accepted. Human review is required before using a tailored document or recording a consequential application event.

## Public examples

All repository examples are fictional. Similarity to a real person, institution, employer, or job is unintended.

## Reporting a privacy issue

Do not open a public issue containing personal data. Report the problem through a private security channel configured by the repository owner, and remove exposed data from the working tree and Git history before publication.
