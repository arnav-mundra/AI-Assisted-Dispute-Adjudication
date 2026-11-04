# Runs that lost a case to an API error

Kept unedited for reference; `list_runs` does not read this folder. Failed cases score as wrong,
so these accuracy figures should not be cited. Re-run the configuration instead.

- `20261102-211021_counterfactual_llm_gpt-oss-20b_cot`: CF-104 failed with Groq error 400
  `json_validate_failed`.
- `20261105-011346_counterfactual_llm_gpt-oss-20b_cot`: CF-112 failed with Groq error 400
  `json_validate_failed`, after earlier rate-limit retries used up the shared retry count.
