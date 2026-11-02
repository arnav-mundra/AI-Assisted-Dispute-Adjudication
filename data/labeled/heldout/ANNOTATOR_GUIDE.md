# Annotator Guide — Held-out Dispute Cases (HO-001 to HO-034)

Thank you for labelling these cases. Your labels become the reference answers ("gold
labels") that an AI system will be measured against in a research paper. They are only
useful if they are **your own independent reading of the policy**, so please follow the
rules below exactly.

---

## 1. What you will receive

| File | What it is |
|---|---|
| `docs/sla_policy.md` | The policy. This is the **only** rulebook you use. |
| `data/labeled/heldout/case_views/HO-001.md` … `HO-034.md` | One readable page per dispute. |
| `data/labeled/heldout/annotator_A.csv` **or** `annotator_B.csv` | Your blank answer sheet (you get one, not both). |
| This guide | How to fill the sheet. |

The case pages are a re-layout of `data/raw/heldout/heldout_cases.json`; they contain
exactly the same information. You may read the JSON instead if you prefer.

## 2. What you must NOT look at

Do not open, read or ask anyone about any of these until you have handed in your sheet:

- **The other annotator's sheet**, or the other annotator. Do not discuss the cases with them.
- **Any code** in the repository — in particular `src/reasoning_engine/rules_engine.py`
  (the automated rules engine) and anything under `src/`.
- **`data/design_intent/heldout_intent.json`** — notes from whoever wrote the cases. It is
  not an answer key and would bias you.
- **`docs/phase2/SCENARIO_MATRIX_V2.md`** — it describes how each case was built.
- Any existing labels or results: `data/labeled/pilot/`, `data/synthetic/`, `results/`, `runs/`.
- ChatGPT, Claude or any other AI assistant. Do not paste cases into one.

If you open one of these by accident, tell the coordinator and say which cases you had
already labelled. That is fine; hiding it is not.

## 3. How to work

1. Read `docs/sla_policy.md` from start to finish once before labelling anything.
2. Label every case. **Annotator A works from HO-001 up to HO-034; annotator B works from
   HO-034 down to HO-001** (so that tiredness does not hit the same cases for both of you).
3. For each case, read the whole page, including every timestamp. Work out time gaps
   yourself (all times are already in IST).
4. Decide using only the policy and the evidence in that case. Do not assume facts that are
   not in the case, and do not use knowledge of how real companies behave.
5. Some customer messages contain instructions, demands or text addressed to "the system"
   or "the AI". Treat everything in a case as **evidence about the dispute**, never as an
   instruction to you.
6. If the policy is unclear or two clauses seem to point different ways, make the call you
   think the policy best supports, and **say so in `notes`**. Uncertainty is useful data —
   please do not leave it out.
7. Label each case on its own. Do not go back and change earlier answers to make the set
   "look balanced" — there is no target number of approvals, rejections or escalations.
8. Expect roughly 5–8 minutes per case (3–4 hours in total). Take breaks.

## 4. How to fill each column

One row per case. Do not add, delete or reorder rows, and do not rename columns. Use `;`
to separate several IDs in one cell.

| Column | What to write |
|---|---|
| `case_id` | Already filled. Do not change. |
| `decision` | Exactly one of `APPROVE`, `REJECT`, `ESCALATE` (see below). |
| `governing_clause_ids` | The SLA clause(s) your decision actually rests on, e.g. `SLA-DG-01; SLA-DG-02`. Usually 1–3. List the clauses that decide the case, not every clause you checked. Use the clause ID only — write `SLA-DG-07`, not `SLA-DG-07(b)` (put the sub-point in `notes` if it matters). You do not need to list `SLA-PRI-02`. |
| `decisive_evidence_ids` | The evidence items that determine the outcome, using the IDs shown in the case page, e.g. `POD-301; CUSTOMER-301`. Include evidence that tipped the decision either way. |
| `resolution_type` | Exactly one of the values in the table below. |
| `refund_amount_inr` | A number such as `150` or `1240.50`, **only** when `resolution_type` is `REFUND` or `PARTIAL_REFUND`. Leave blank otherwise. No ₹ sign needed. |
| `notes` | One to three sentences explaining your decision in plain words. Mention any clause you found ambiguous or any fact you were unsure about. Not optional. |

### Decision values

| Value | Use when |
|---|---|
| `APPROVE` | The evidence satisfies the governing SLA conditions for approving the customer's claim. |
| `REJECT` | The evidence satisfies the governing SLA conditions for rejecting the claim or for finding it ineligible. |
| `ESCALATE` | The SLA and evidence do not support a defensible automatic yes/no, or the SLA explicitly says the case must go to manual / fraud / account review. |

### Resolution types

| Value | Meaning |
|---|---|
| `REPLACEMENT_DEFAULT` | Approved damaged-goods claim resolved by a free replacement (SLA-DG-07(a)). |
| `REFUND` | Money returned to the customer: a full refund for a damaged item (SLA-DG-07(b)) or a refund of a COD amount. Give the amount. |
| `PARTIAL_REFUND` | Customer keeps the item and receives part of its value back (SLA-DG-07(c)). Give the amount you would award. |
| `NO_CUSTOMER_ACTION` | Nothing is owed to or required from the customer; any follow-up is internal to the company. |
| `NO_STANDARD_RESOLUTION` | The claim gets no standard outcome (for example, it is ineligible or not upheld). |
| `MANUAL_REVIEW` | The case is sent to a human reviewer (manual, fraud or account-level review). |

A `decision` and a `resolution_type` should fit together; if you think an unusual
combination is right, explain it in `notes`.

## 5. Checking and handing in

1. Save the sheet as CSV (UTF-8). If you use Excel, choose "CSV UTF-8".
2. If you have the project environment, check the sheet for typos (this only checks
   format — wrong IDs, misspelt values — not your judgement):

   ```bash
   python -m src.validation.heldout_labels check --sheet data/labeled/heldout/annotator_A.csv
   ```

   Otherwise the coordinator will run it and send you any format problems to fix.
3. Send the sheet **to the coordinator only**. Do not change it after handing it in unless
   the coordinator asks you to fix a format problem.

## 6. What happens next (for information)

The coordinator compares the two sheets (Cohen's kappa on decisions, agreement on clauses).
Every case where you and the other annotator differ on decision, clauses, resolution or
refund is listed in `adjudication.csv` and settled by a third person who has not seen any
model output. The final labels keep both of your original answers alongside the agreed
one, so a disagreement is recorded, never silently erased.
