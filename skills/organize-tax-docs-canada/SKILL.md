# Skill: Canadian Tax Document Organizer

## Description

An AI agent skill designed to organize, categorize, and rename Canadian tax documents (PDFs, spreadsheets, and images) into a strict, accountant-friendly taxonomy. This framework is optimized for professional Canadian tax software (like CANTAX, Profile, or Taxprep) to ensure maximum efficiency, minimize accountant queries, and cleanly handle complex family tax scenarios.

## Taxonomy Framework

The agent must rename all files to strictly adhere to the following grammatical structure:

**`YYYY - [Name] - [Bucket] - [Document Type] - [Context] - [Issuer] ([Tags]).[ext]`**

### Fields

- **`YYYY`**: The 4-digit tax year the document applies to.
- **`Name`**: First name of the taxpayer. Use `Name 1 & Name 2` for joint documents (e.g., `John & Jane`).
- **`Bucket`**: A numbered category (`01` through `06`) mapping to the tax preparation workflow (see below).
- **`Document Type`**: The exact CRA form number (e.g., `T4`, `T5008`, `1042-S`) or a standardized description (e.g., `RRSP Receipt`, `Medical Summary`, `Trading Summary`).
- **`Context`**: The specific account type, asset, business name, or custom user nickname (e.g., `Margin Long`, `Joint Save (Pet Fund)`).
- **`Issuer`**: The institution, employer, or entity that generated the document (e.g., `Wealthsimple`, `CRA`, `Canada Life`).
- **`[Tags]`**: _Optional._ Vital metadata wrapped in parentheses at the end of the filename:
  - **RRSP Dates:** `(Mar-Dec)` or `(Jan-Feb)`.
  - **Foreign Assets:** `(Foreign)` or `(USD)`.
  - **Dollar Amounts:** `($XXX.XX)` for loose receipts (e.g., donations, medical).
  - **Combined files:** `(Combined)`.

---

## Workflow Buckets

The agent must sort every document into one of these six fundamental, timeless categories:

### `01 Admin`

_Anything required to set up the file or answer "Who are you and what is your history?"_

- **Covers:** Notices of Assessment (NOA), CRA letters, IDs, void cheques, T1013/AuthRep forms.

### `02 Income`

_All money coming in, regardless of the source._

- **Covers:** Standard employment (T4), EI (T4E), pensions (T4A), self-employment/side-hustles (T2125 summaries), rental property income (T776), and payslips.

### `03 Assets`

_Anything you own that generates passive income, capital gains, or triggers reporting requirements._

- **Covers:** T3s, T5s, T5008s, US Stock plans (1042-S), crypto summaries, carrying charges (deductible margin fees), and foreign property tracking (T1135 triggers).

### `04 Deductions`

_Anything that lowers your taxable income or provides a credit._

- **Covers:** RRSP receipts, Medical expenses, Childcare, Donations, Professional Dues, Tuition, moving expenses, utility bill calculations (for home office).

### `05 Events`

_One-off or infrequent life changes that require special tax disclosures._

- **Covers:** Sale of a principal residence, separation agreements (spousal support), birth/adoption records, or estate documents.

### `06 Reference`

_The "Info Only" drawer. Documents that provide context but aren't actively entered into the tax software._

- **Covers:** TFSA summaries, RESP statements, non-deductible fee reports for registered accounts, general banking statements.

---

## Agent Logic & Processing Rules

The agent must apply the following logic rules when parsing and renaming files:

1.  **The "Name" Routing Rule:** Assign the first name of the individual. If the document covers a joint account or joint asset (e.g., a Joint Chequing T5), the `[Name]` field MUST be `[Name 1] & [Name 2]`.
2.  **The "Asset vs. Reference" Fee Rule:**
    - If an investment fee statement is for a registered account (`TFSA`, `RRSP`, `RESP`, `LIRA`), route it to `06 Reference` (not tax-deductible).
    - If a fee statement is for a taxable account (`Margin`, `Cash`, `Non-Registered`), route it to `03 Assets` (deductible carrying charges).
3.  **The RRSP Date Rule:** If the document is an RRSP receipt, determine the date range. Append `(Mar-Dec)` or `(Jan-Feb)` to the tags based on the contribution period.
4.  **The Foreign Property Rule (T1135):** If the document originates outside Canada (e.g., USD, 1042-S, W-8BEN, or mentions foreign tax paid), append `(Foreign)` or `(USD)` in the tags.
5.  **The Clean Formatting Rule:** Strip all emojis and non-standard characters (e.g., `☔️`, `•`, `|`). Replace them with standard hyphens `-` or wrap the context in parentheses.
6.  **The Context/Nickname Preservation Rule:** If a user has named an account (e.g., "Peanut Fund"), the agent MUST preserve that nickname in the `[Context]` field, formatted as `Account Type (Nickname)` (e.g., `Joint Save (Peanut Fund)`).
7.  **The Aggregation Rule:** If a file contains multiple receipts of the same category (e.g., a single PDF with 15 charity receipts), add `(Combined)` to the tags. If it is an Excel/CSV file calculating totals, use the word `Summary` or `Calculations` in the Document Type.
8.  **The Abbreviation Rule:** Automatically abbreviate major Canadian institutions to their common acronyms to keep filenames concise (e.g., `Royal Bank of Canada` ➔ `RBC`, `Toronto Dominion` ➔ `TD`, `Bank of Montreal` ➔ `BMO`).
