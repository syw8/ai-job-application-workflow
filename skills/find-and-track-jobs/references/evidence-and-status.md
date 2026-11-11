# Evidence, identity, dates, and status

## Evidence order

Use the strongest available evidence for each fact:

1. Explicit user confirmation for the user's actions or decisions.
2. Direct application confirmation, interview communication, or decision communication supplied by the user.
3. Existing reviewed private record.
4. Current primary employer page for vacancy content and observed availability.
5. Trustworthy archived or secondary source, clearly labeled.
6. Search snippet or inferred metadata, used only as a lead.

Keep the evidence date and source. New evidence may supersede a stale value without erasing explanatory history.

## Deduplication

Compare requisition ID, canonical official URL, organization, title, location, and observation dates. Equivalent official URLs with the same requisition are strong duplicate evidence. Matching titles with different requisitions may be distinct. Use `possible_duplicate` when uncertain.

## Separate states

Application status: `needs_review`, `planned`, `submitted`, `interviewing`, `offer`, `rejected`, `withdrawn`, `declined`.

Vacancy status: `unknown`, `observed_open`, `observed_closed`, `expired`, `removed`.

Never convert one dimension into the other.

## Date precision

Store the normalized value and precision: day (`2030-04-12`), month (`2030-04`), year (`2030`), a stated range, or unknown. Preserve original wording when normalization loses ambiguity. The date on which the user confirms an event is not automatically the event date.

## Materials

Track each local document with a stable version ID, type, review state, creation date, and target requisition. Track user-confirmed uploads and submitted versions separately by those IDs. Never link another role's document merely because its filename is similar.
