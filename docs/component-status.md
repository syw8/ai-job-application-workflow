# Implementation map

This page maps the repository's main capabilities to their technical implementation and verification path.

| Capability | Implementation | Verification |
| --- | --- | --- |
| Job discovery and tracking | `find-and-track-jobs` Skill with source verification, deduplication, evidence, and status rules | Skill validation, workflow tests, record business-rule tests |
| Cover-letter workflow | `write-cover-letter` Skill with official-guidance research, evidence mapping, versioning, and change decisions | Skill validation and fictional end-to-end generation |
| CV workflow | `tailor-cv` Skill with full-document tailoring, protected candidate facts, and reviewable proposals | Skill validation and fictional CV generation |
| Application records | JSON Schema plus Python rules for dates, evidence, duplicates, exact document versions, statuses, and adapter agreement | Schema and unit tests |
| Privacy validation | Redacting Python scanner with configurable private denylist | Positive and negative privacy tests |
| Fictional demonstration | Deterministic CV, cover-letter, and change-review generator with checked-in fixtures | Regeneration comparison tests |
| Continuous integration | GitHub Actions workflow running privacy, project, and unit checks | Required workflow executed on pushes and pull requests |
| Local data adapters | Skill contracts for JSON, Markdown, Excel, and DOCX records | Schema, state-consistency, and adapter-contract tests |

## Integration model

The Skills use the tools available in the host agent environment. Web-enabled agents support current vacancy and guidance research. Compatible document and spreadsheet tools support Excel and DOCX reconciliation while preserving the user's private files and established formats.

Optional scheduled discovery runs in a scheduling product and passes source-linked leads into the same `find-and-track-jobs` workflow. GitHub Actions is reserved for repository validation.
