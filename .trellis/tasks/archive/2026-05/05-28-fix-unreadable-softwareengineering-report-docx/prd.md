# Fix Unreadable SoftwareEngineering Report Docx

## Goal

Fix the generated SoftwareEngineering `.docx` so it opens reliably in Word/WPS, while preserving the original-template cover structure and completed report content.

## What I Already Know

* The user reported that the generated file cannot be opened.
* `python-docx` could parse the file, but Word/WPS may reject stricter OpenXML issues.
* The likely risk is the custom footer page field inserted directly into paragraph XML; if malformed, Word/WPS can treat the document as corrupt.
* The Chinese filename may also be inconvenient in some file-transfer/opening paths, so an ASCII filename copy should be provided.

## Requirements

* Regenerate a Word/WPS-compatible `.docx`.
* Preserve the original template cover text and section structure already added.
* Preserve all report content, tables, and 8 embedded diagrams.
* Replace risky custom footer XML with plain compatible footer text.
* Save both the Chinese final filename and an ASCII filename copy under `SoftwareEngineering/generated/`.

## Acceptance Criteria

* [x] The generated `.docx` is a valid zip package and all XML files parse.
* [x] No footer field XML is inserted directly into invalid locations.
* [x] The `.docx` can be parsed by `python-docx`.
* [x] The report contains the original-template cover markers and 8 embedded images.
* [x] An ASCII filename copy exists for easier opening/downloading.

## Technical Notes

* Replaced the custom page-number field XML with plain footer text `- PAGE -`.
* Generated `SoftwareEngineering/generated/dorm_repair_report_compatible.docx` as an ASCII filename copy of the final report.
* Validation passed for both `.docx` files: `zipfile.is_zipfile`, `ZipFile.testzip`, parsing every `.xml` member with `ElementTree`, and reopening with `python-docx`.

## Out of Scope

* Installing system LibreOffice without sudo password.
* Filling personal cover fields.
