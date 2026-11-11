# Fictional walkthrough

This example uses Avery Rowan, Cedar & Finch Labs, and a Junior Evidence Analyst vacancy. All candidate, employer, job, and application details are invented.

## 1. Define the search

The example candidate is looking for early-career evidence and data roles. In real use, role, location, language, work-mode, and exclusion criteria come from the private configuration.

The search finds a lead and verifies the primary detail page. The invented result is stored in `examples/fictional-demo/job-lead.json`; its `example.com` URL prevents confusion with a live vacancy.

## 2. Review the vacancy

Before any document is written, the user checks the role, requisition, location, responsibilities, deadline, and open status. A lead that lacks a working primary page remains unverified.

## 3. Research how to apply

`document-input.json` records two current public guidance sources and the points used from them:

- [Bundesagentur für Arbeit cover-letter guidance](https://www.arbeitsagentur.de/bildung/bewerbung/anschreiben)
- [Europass CV guidance](https://europass.europa.eu/en/create-europass-cv)

The vacancy's own instructions would take priority if they differed from general advice.

## 4. Match the candidate to the role

The `matches` array connects each important requirement to a fact from the fictional candidate profile. Unsupported requirements are omitted from the documents or returned as questions; they are never turned into candidate claims.

## 5. Generate and review the documents

Run from the repository root:

```bash
python3 scripts/generate_fictional_documents.py \
  --input examples/fictional-demo/document-input.json \
  --output-dir examples/fictional-demo/generated
```

The generated CV contains experience, project, education, skills, and languages, reordered and described for the target role. The cover letter is written from the evidence map rather than copied from a baseline. `fictional-change-review.md` shows each proposed change, its rationale, evidence IDs, and decision.

The user compares the drafts with the candidate profile and source notes before treating them as ready. The application record then links the reviewed CV and letter by their exact version IDs.

## 6. Track the decision

`application-record.json` records the role as planned. Generating files does not prove upload or submission. If the user later supplies a confirmation, the tracker can update the event date and enabled adapters after review.

Run all repository checks with:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
bash scripts/run_checks.sh
```
