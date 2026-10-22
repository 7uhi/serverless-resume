Place your exported resume PDF here as `Resume.pdf` (capital R).

To update the site, replace that file, commit, and push to `main`.
The website preview, PDF download, and text view all use this same document.
GitHub installs the PDF text extraction tool automatically; no compiler is needed.

The input path is configured by `pdf` in `../site.json`. The published download
always uses `/resume.pdf`, regardless of the input filename.
