# Optional adapter contracts

All paths come from private configuration. Read current values before writing and preserve unrelated user changes.

## JSON

Use stable IDs, validate the record schema, preserve compatible extension fields, and write atomically when possible.

## Markdown

Preserve source links, evidence dates, unresolved questions, update history, and valid internal links. Do not require application-specific syntax unless configured.

## Excel

Locate fields by headers and records by stable ID. Preserve tables, filters, validation, formatting, formulas, date types, hyperlinks, and frozen panes. Recalculate and inspect changed ranges when supported.

## DOCX timeline

Back up to the configured private location. Update only the matching role and confirmed event, preserve the existing style and order, then render all pages and inspect page breaks and clipping.

## Verification

Compare identity, vacancy status, application status, event date, document version IDs, material state, and next action across enabled adapters. A partial batch is not fully synchronized.
