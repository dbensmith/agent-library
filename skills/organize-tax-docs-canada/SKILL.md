---
name: organize-tax-docs-canada
description: Organize, categorize, and rename Canadian tax documents into an accountant-friendly taxonomy. Use when the user wants to rename or organize tax PDFs, spreadsheets, or receipts for Canadian tax preparation.
---

# Skill: Canadian Tax Document Organizer

## Taxonomy Framework

Rename all files to strictly adhere to the following grammatical structure:

**`YYYY - [Name] - [Bucket] - [Document Type] - [Context] - [Issuer] ([Tags]).[ext]`**

### Fields

- **`YYYY`**: The 4-digit tax year the document applies to.
- **`Name`**: First name of the taxpayer. Use `Name 1 & Name 2` for joint documents (e.g., `John & Jane`).
- **`Bucket`**: A numbered category (`01` through `06`) mapping to the tax preparation workflow (see below).
- **`Document Type`**: The exact CRA form number (e.g., `T4`, `T5008`, `1042-S`) or a standardized description (e.g., `RRSP Receipt`, `Medical Summary`, `Trading Summary`).
- **`Context`**: The specific account type, asset, business name, or custom user nickname (e.g., `Margin Long`, `Joint Save (Pet Fund)`).
- **`Issuer`**: The institution, employer, or entity that generated the document (e.g., `Wealthsimple`, `CRA`, `Canada Life`).
- **`[Tags]`**: Optional metadata wrapped in parentheses at the end of the filename:
  - **RRSP Dates:** `(Mar-Dec YYYY)` or `(Jan-Feb YYYY)`.
  - **Foreign Currency:** 3-letter ISO currency code (e.g., `(USD)`, `(EUR)`, `(GBP)`, `(PHP)`).
  - **Dollar Amounts:** `($XXX.XX)` for loose receipts (e.g., donations, medical).
  - **Combined files:** `(Combined)`.

## Workflow Buckets

Sort every document into one of these six categories:

- **`01 Admin`**: Documents required to set up the file (e.g., Notices of Assessment, CRA letters, IDs, void cheques, T1013/AuthRep forms).
- **`02 Income`**: All money coming in (e.g., T4, T4E, T4A, T2125 summaries, T776, payslips).
- **`03 Assets`**: Assets generating passive income, capital gains, or triggering reporting requirements (e.g., T3, T5, T5008, 1042-S, crypto summaries, carrying charges, T1135 triggers).
- **`04 Deductions`**: Items lowering taxable income or providing credits (e.g., RRSP receipts, Medical expenses, Childcare, Donations, Professional Dues, Tuition, moving expenses, utility bill calculations).
- **`05 Events`**: Infrequent life changes requiring special disclosures (e.g., Sale of a principal residence, separation agreements, birth/adoption records, estate documents).
- **`06 Reference`**: Contextual documents not actively entered into tax software (e.g., TFSA summaries, RESP statements, non-deductible fee reports, general banking statements).

## Processing Rules

Apply these logic rules when parsing and renaming files:

1. **Route Names:** Assign the first name of the individual. If the document covers a joint account or joint asset, set the `[Name]` field to `[Name 1] & [Name 2]`.
2. **Route Fees:**
   - Route investment fee statements for registered accounts (`TFSA`, `RRSP`, `RESP`, `LIRA`) to `06 Reference`.
   - Route fee statements for taxable accounts (`Margin`, `Cash`, `Non-Registered`) to `03 Assets`.
3. **Format RRSP Dates:** Determine the date range for RRSP receipts. Append `(Mar-Dec YYYY)` or `(Jan-Feb YYYY)` to the tags based on the contribution period.
4. **Flag Foreign Currency:** If a document reports values in a foreign, non-CAD currency (e.g., a US stock plan or a USD brokerage account), append the 3-letter ISO currency code in the tags (e.g., `(USD)`, `(EUR)`, `(GBP)`, `(PHP)`). Do not tag CAD documents.
5. **Clean Formatting:** Strip emojis and non-standard characters (e.g., `☔️`, `•`, `|`). Replace them with standard hyphens `-` or wrap the context in parentheses.
6. **Preserve Nicknames:** Preserve custom account names (e.g., "Pet Fund") in the `[Context]` field, formatted as `Account Type (Nickname)` (e.g., `Joint Save (Pet Fund)`).
7. **Aggregate Files:** Add `(Combined)` to the tags if a file contains multiple receipts of the same category. Use `Summary` or `Calculations` in the Document Type for Excel/CSV files calculating totals.
8. **Abbreviate Institutions:** Abbreviate major Canadian institutions to their common acronyms (e.g., `Royal Bank of Canada` -> `RBC`, `Toronto Dominion` -> `TD`, `Bank of Montreal` -> `BMO`).
