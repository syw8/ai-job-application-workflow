---
name: find-and-track-jobs
description: Search for current jobs matching private user criteria, verify primary vacancy pages, deduplicate leads, and maintain evidence-backed application records across optional JSON, Markdown, Excel, and DOCX adapters. Use for job discovery and tracking; do not submit applications or infer candidate actions.
---

# Find and Track Jobs

Find relevant live vacancies, let the user choose, and keep the resulting records consistent.

## Before searching

Read the private search criteria and enabled tracker adapters. Confirm material ambiguities in desired roles, locations, work modes, languages, eligibility, seniority, and exclusions. Do not infer sensitive preferences from candidate documents.

Read [references/search-policy.md](references/search-policy.md) for discovery and [references/evidence-and-status.md](references/evidence-and-status.md) for records. Read [references/adapters.md](references/adapters.md) only for enabled adapters.

## Search workflow

1. Search current official employer, university, institute, public-sector, and recognized job-service pages that fit the user's criteria.
2. Use aggregators and search snippets only to discover leads. Open the primary vacancy detail page before treating a role as verified.
3. Capture organization, exact title, requisition ID, location, work mode, deadline and precision, eligibility, required language, source URL, observation date, and observed vacancy status.
4. Compare each lead with existing records by requisition ID, canonical URL, organization, title, and location.
5. Present a concise shortlist with evidence, fit questions, exclusions, and possible duplicates. Do not claim that a candidate is qualified when evidence is incomplete.
6. Create or update private records only for leads the user wants tracked, unless the user explicitly requested a broader lead inbox.

## Tracking workflow

1. Treat each supported fact independently and keep its evidence date and source.
2. Preserve uncertainty and conflicts. Never merge distinct requisitions solely because titles match.
3. Keep vacancy status separate from application status.
4. Require direct evidence and human review for submitted, interviewing, offer, rejected, withdrawn, and declined states.
5. Record each local CV or letter by a stable version ID, document type, review state, creation date, and target requisition. Record uploaded or submitted versions only from direct evidence.
6. Prepare the smallest consistent update across enabled adapters.
7. Validate JSON against `schemas/application-record.schema.json` when available, write each adapter, then compare key fields across adapters.
8. Report partial writes, conflicts, and records needing review.

## Safety boundaries

- A local CV or letter is not proof of upload or submission.
- A closed vacancy is not a rejection or withdrawal.
- Failure to find a confirmation is not proof that no application occurred.
- Never infer exact dates from ambiguous text.
- Do not submit applications, contact employers, or run unattended two-way synchronization.

Scheduled searching may be configured in an external scheduler. The Skill itself also supports an on-demand search; the repository does not claim that GitHub runs personal job searches.
