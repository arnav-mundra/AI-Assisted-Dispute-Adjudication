# Runs that lost a case to an API error

Kept unedited for reference; `list_runs` does not read this folder. Failed cases score as wrong,
so these accuracy figures should not be cited. Re-run the configuration instead.

- `20261102-211021_counterfactual_llm_gpt-oss-20b_cot`: CF-104 failed with Groq error 400
  `json_validate_failed`.
- `20261105-011346_counterfactual_llm_gpt-oss-20b_cot`: CF-112 failed with Groq error 400
  `json_validate_failed`, after earlier rate-limit retries used up the shared retry count.
- `20261114-225846_heldout_llm_gpt-oss-20b_cot`: HO-025 failed with Groq error 400 `json_validate_failed`
  (three rejections); HO-032, HO-033 and HO-034 hit the 200K tokens-per-day limit. gpt-oss-20b needs
  slightly more than one day's budget for the 34 held-out cases.
- `20261117-141636_heldout_llm_qwen3.8-27b_zero_shot`: HO-005, HO-008, HO-009 and HO-010 failed with a transient
  `Connection error.`; the other 30 cases are reused by `--resume-from`.
