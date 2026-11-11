# Fictional demo

The files in this folder contain only invented candidate, employer, vacancy, and application data.

- `candidate-profile.example.yaml` shows the shape of a private factual profile.
- `job-lead.json` represents a verified search lead.
- `document-input.json` combines the reviewed vacancy, public guidance notes, requirement-to-evidence map, document version, and change decisions.
- `generated/` contains the resulting CV, cover letter, and change-review record.
- `application-record.json` links the reviewed document versions to a planned application without claiming submission.
- `review-checkpoint.md` lists the decisions a person should make before using the documents or changing the record.

Generate the documents from the repository root:

```bash
python3 scripts/generate_fictional_documents.py \
  --input examples/fictional-demo/document-input.json \
  --output-dir examples/fictional-demo/generated
```
