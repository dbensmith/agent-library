---
name: organize-tax-docs-canada
description: Organize, categorize, and rename Canadian tax documents into a conservative, accountant-friendly taxonomy. Use when the user wants to rename or organize Canadian tax PDFs, images, spreadsheets, or receipts for tax preparation.
---

# Skill: Canadian Tax Document Organizer

## Goal

Rename and sort Canadian tax documents into a consistent format that is easy for an accountant to review.

This skill is optimized for an agent. The agent must:

1. Extract visible facts from documents.
2. Use authoritative Canadian references where available.
3. Prefer conservative classification over guessed tax treatment.
4. Preserve all files even when classification is uncertain.

## Core Rule

**Extract when explicit. Reference when available. Review when uncertain. Never invent metadata.**

If a field cannot be determined from:

- the document text,
- the document structure,
- a highly reliable original filename, or
- an approved reference source,

use a safe fallback value instead of guessing.

## Approved Reference Sources

Use these sources before making normalization or classification decisions.

### Primary tax references

- CRA tax slips overview:
  `https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/what-slips-you-should-have-received.html`
- CRA forms listed by number:
  `https://www.canada.ca/en/revenue-agency/services/forms-publications/forms.html`
- CRA Auto-fill My Return for professional tax preparers:
  `https://www.canada.ca/en/revenue-agency/services/e-services/about-auto-fill-return.html`

### Primary institution references

- CDIC list of member institutions and trade names:
  `https://www.cdic.ca/depositors/list-of-members/`

### Secondary context references

- Finance Canada / Payments Canada membership context:
  `https://www.canada.ca/en/department-finance/programs/consultations/2022/expanding-membership-eligibility-payments-canada/expanding-membership-eligibility-payments-canada.html`

### Source usage policy

- Prefer CRA for slip names, form numbers, and tax-document naming.
- Prefer CDIC for Canadian bank and deposit-institution normalization.
- Use issuer websites only to confirm branding when the issuer is already strongly indicated.
- Use secondary or non-official sources only as supplemental context, never as sole authority for tax classification.

## Filename Format

Rename all files to this format:

**`YYYY - Person - Bucket - Document Type - Issuer - Context (Tags).ext`**

Use spaced hyphens exactly as shown for readability.

If `Context` is empty, omit the entire ` - Context` segment.

## Person Naming Policy

This rule is black and white. The agent must not make a discretionary judgment about confusion risk.

### Default rule

Use the following values:

- `Taxpayer`
- `Spouse`
- `Child - FirstName`
- `Joint`
- `Review Person`

### Full-name rule

Use full person names instead of role labels whenever **any** of the following is true:

1. The input set contains more than one child.
2. The input set contains multiple people with the same first name.
3. The user explicitly provides full names for household members.
4. The input set includes dependants, parents, or relatives beyond the core taxpayer/spouse pair.
5. The same role could refer to more than one real person across files.
6. The user requests full-name filenames.

When the full-name rule is triggered, apply it consistently to the entire batch.

### Allowed values under full-name mode

- `FirstName LastName`
- `FirstName LastName & FirstName LastName`
- `Child - FirstName LastName`
- `Review Person`

### Person assignment rules

- Use `Joint` or both full names only if shared ownership or both people are explicit in the document.
- Do not infer joint ownership from household context alone.
- If ownership is unclear, use `Review Person`.
- Do not shorten a full name to a first name once full-name mode is active for the batch.

## Field Definitions

### 1) `YYYY`

The tax year the document applies to.

Use:

- The slip year shown on the form, if explicit.
- The receipt or statement year, if explicit and clearly tax-relevant.
- `Unknown Year` if no single year can be determined safely.

### 2) `Bucket`

A broad workflow category.

Allowed values:

- `01 Admin`
- `02 Income`
- `03 Investments`
- `04 Deductions`
- `05 Family`
- `06 Events`
- `99 Review`

### 3) `Document Type`

Use the exact CRA or issuer form number when available.

Examples:

- T4
- T4A
- T5
- T3
- T5008
- T2202
- T4RSP
- T4RIF
- 1042-S
- RRSP Receipt
- Donation Receipt
- Medical Receipt
- Childcare Receipt
- Notice of Assessment
- Trading Summary
- Carrying Charges Summary

If unclear, use `Unknown Document`.

### 4) `Issuer`

The organization that issued the file.

Examples:

- CRA
- RBC
- TD
- BMO
- Wealthsimple
- Questrade
- Canada Life
- University of Alberta

Rules:

- Use the issuer name shown on the document when explicit.
- Use a standard acronym only when unambiguous and commonly recognized.
- Prefer official institution naming over user nicknames.
- If unclear, use `Unknown Issuer`.

### 5) `Context`

Optional. Include only when it adds objective clarity.

Allowed examples:

- Jan-Feb 2026
- Mar-Dec 2025
- Non-Registered
- RRSP
- TFSA
- Rental Property
- 123 Pacific View, Victoria
- 789 Prairie Lane, Calgary
- Business Name

Rules:

- Only use context that is explicit in the document or highly reliable from the original filename.
- Do not invent nicknames or descriptive labels.
- Omit context if it does not add verified clarity.

### 6) `(Tags)`

Optional metadata in parentheses.

Allowed tags:

- `(Combined)`
- `(USD)`
- `(EUR)`
- `(GBP)`
- `(Amended)`
- `(Summary)`

Rules:

- Add a currency tag only when the document is clearly denominated in that non-CAD currency.
- Add `(Combined)` only when one file contains multiple same-category items.
- Add `(Summary)` for rollups, spreadsheets, or manually prepared totals.
- Omit tags if none apply.

## Source Priority Rules

### CRA first

Use CRA references to:

- identify tax slip names,
- confirm form numbers,
- distinguish official tax document labels,
- normalize naming for returns, slips, and notices.

### CDIC first

Use CDIC references to:

- normalize Canadian bank and deposit-taking institution names,
- map trade names to member institutions,
- verify whether a retail banking brand is an alias of an official institution.

### Finance Canada / Payments context only

Use Finance Canada or Payments Canada materials only for:

- institution-type context,
- payments ecosystem background,
- supplemental issuer context.

Do not use them as the primary source for filename issuer branding.

## Bucket Mapping Rules

Use these mappings only when the document clearly matches.

### `01 Admin`

Administrative and setup documents.

Examples:

- Notice of Assessment
- Reassessment
- CRA letters
- Authorization forms
- ID provided for onboarding
- Void cheque
- Direct deposit form

### `02 Income`

Income slips and direct income records.

Examples:

- T4
- T4A
- T4E
- T4RSP
- T4RIF
- T5013
- T2125 support
- T776 support
- Payslips when supplied to support reported income

### `03 Investments`

Investment, trading, foreign income, and taxable asset reporting.

Examples:

- T3
- T5
- T5008
- 1042-S
- annual trading summaries,
- taxable account carrying charges,
- crypto gain/loss summaries,
- foreign asset support,
- T1135 support files or workpapers

### `04 Deductions`

Deductions and credit-type documents primarily tied to tax reduction.

Examples:

- RRSP receipts
- Medical receipts
- Donation receipts
- Professional dues
- Moving expenses
- Employment expense support
- Childcare receipts when treated as deductible support
- Accountant fee receipts if clearly deductible
- Carrying charges summaries if clearly linked to taxable investments

### `05 Family`

Family, education, and dependant-related records.

Examples:

- T2202
- Childcare receipts
- Tuition support
- Dependant medical summaries
- disability-related support
- adoption-related tax support
- child benefit support supplied for context

### `06 Events`

Special one-time or infrequent tax events.

Examples:

- Principal residence sale support
- Separation or divorce documents
- Death or estate documents
- Immigration or emigration tax support
- One-time settlement documents
- Property disposition packages

### `99 Review`

Use when classification is uncertain or the document spans multiple categories.

Examples:

- Mixed annual banking packages
- Unclear screenshots
- Poor OCR scans
- Multi-topic PDFs
- Statements with possible tax relevance that cannot be safely determined

## Decision Boundaries

### Safe to extract

These are usually safe when explicitly visible:

- year,
- form number,
- issuer,
- currency,
- child name,
- RRSP contribution period,
- property address,
- account registration type

### Use caution

These require stronger evidence:

- joint ownership,
- bucket selection for mixed files,
- whether a fee is deductible,
- whether a document is only reference material,
- whether a document supports T1135 reporting

### Never infer from weak signals

Do not assume:

- a document is joint just because spouses usually share it,
- a document belongs to one person because their name appears only in the original filename,
- a registered account fee is deductible,
- a statement is tax-irrelevant because it looks routine,
- a nickname should appear in the filename unless the user explicitly asked for nickname preservation

## Extraction Priority

Determine fields in this order:

1. File extension
2. Document year
3. Form number or document type
4. Issuer
5. Person
6. Bucket
7. Context
8. Tags

If earlier fields are uncertain, do not compensate by becoming more aggressive later.

## Formatting Rules

- Preserve the original file extension.
- Use title case for plain-English document labels.
- Preserve official form numbers in uppercase exactly as shown.
- Replace unsupported or noisy characters with spaces or hyphens.
- Normalize repeated whitespace.
- Do not use emojis.
- Do not use slashes in filenames.
- Omit empty segments rather than leaving dangling separators.
- Keep filenames concise.

## Fallback Rules

When a field cannot be determined:

- Year -> `Unknown Year`
- Person -> `Review Person`
- Bucket -> `99 Review`
- Document Type and Issuer -> Use the provided original filename if both are unknown.

Example fallback:

**`Unknown Year - Review Person - 99 Review - [Original Filename].pdf`**

## Special Rules

### RRSP Receipts

If the contribution period is explicit:

- use context `Jan-Feb YYYY` or `Mar-Dec YYYY`

Examples:

- `2025 - Taxpayer - 04 Deductions - RRSP Receipt - Coast Capital Savings - Jan-Feb 2026.pdf`
- `2025 - Spouse - 04 Deductions - RRSP Receipt - Desjardins - Mar-Dec 2025.pdf`

### Combined Receipts

If a single file contains many receipts of one type:

- use a summary-style document type if appropriate,
- add `(Combined)` when clearly true

Example:

- `2025 - Joint - 04 Deductions - Medical Receipt - Various (Combined).pdf`

### Spreadsheets and CSV files

If the file is a user-prepared rollup:

- use `Summary` or `Calculations` in the document type,
- keep issuer as `User Prepared` unless another issuer is clearly primary

Example:

- `2025 - Joint - 04 Deductions - Medical Summary - User Prepared (Summary).xlsx`

### Multi-person documents

If both spouses are explicitly named and the document is shared:

- use `Joint`, or both full names if full-name mode is active

If both spouses are mentioned but ownership is not clear:

- use `Review Person`

## Output Behavior

For each file:

1. Assign the most specific safe filename possible.
2. Use approved references before normalizing ambiguous form names or issuer names.
3. Avoid guessed metadata.
4. Prefer `99 Review` over a wrong bucket.
5. Preserve all files, even if partially classified.
6. Keep near-duplicate files separate unless the user explicitly requests merging.
7. Apply either role-label mode or full-name mode consistently across the batch according to the Person Naming Policy.

## Examples

### Role-label mode

- `2025 - Taxpayer - 02 Income - T4 - Shopify.pdf`
- `2025 - Spouse - 03 Investments - T5 - Assiniboine Credit Union.pdf`
- `2025 - Joint - 04 Deductions - Donation Receipt - Red Cross Canada.pdf`
- `2025 - Child - Baby Doe - 05 Family - T2202 - Dalhousie University.pdf`

### Full-name mode

- `2025 - John Doe - 02 Income - T4 - Shopify.pdf`
- `2025 - Jane Doe - 03 Investments - T5 - Assiniboine Credit Union.pdf`
- `2025 - John Doe & Jane Doe - 04 Deductions - Donation Receipt - Red Cross Canada.pdf`
- `2025 - Child - Baby Doe - 05 Family - T2202 - Dalhousie University.pdf`

### Fallback

- `Unknown Year - Review Person - 99 Review - [Original Filename].pdf`
