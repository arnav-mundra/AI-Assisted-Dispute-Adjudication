# IEEE PIC 2026 camera-ready (Paper 325)

Scripts that build the camera-ready version of "AI-Assisted Dispute Adjudication for D2C Delivery
Operations: An SLA-Grounded LLM Pipeline" from the saved runs in `results/runs/`.

| File | What it does |
|---|---|
| `build_camera_ready.py` | Edits a copy of the submitted Word file. Every number in the paper is computed from the saved runs, and the build runs the test suite to get the test count. It fails if a stated finding no longer holds. |
| `fig1_pipeline.py` | Draws Fig. 1 (`fig1_pipeline.png`), the pipeline at one IEEE column width. |
| `to_pdf.ps1` | Converts the Word file to PDF with Microsoft Word. |
| `make_response_letter.py` | Turns `response_to_reviewers.md` into the response-letter Word file. |
| `response_to_reviewers.md` | Reviewer comments and the change made for each. |

The paper files themselves (the submitted Word file, the camera-ready Word and PDF files, the letter and the
CMT ZIP) and `author_emails.txt` stay in a local `PIC 2026 camera-ready` folder next to the repository, outside
git. To rebuild, run these from the repository root:

    venv/Scripts/python paper/pic2026/build_camera_ready.py
    powershell -File paper/pic2026/to_pdf.ps1
