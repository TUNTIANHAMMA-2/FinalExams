# Apply Original Report Template Formatting

## Goal

Regenerate the Software Engineering homework report so the final `.docx` uses the original report template's cover page and formatting as closely as possible.

## What I Already Know

* Existing generated report: `SoftwareEngineering/generated/宿舍报修管理系统软件工程导论期末考查报告.docx`.
* Original template: `SoftwareEngineering/《软件工程导论》期末考查报告模板.doc`.
* The template is legacy binary Word `.doc`, not directly editable with `python-docx`.
* Local direct-conversion tools were not initially installed.
* The template text extracted with `strings` shows cover/layout clues including `Sichuan Top Vocational College of Information Technology`, blank underline fields, year/date placeholders, DFD/UML/PAD headings, and WPS metadata.
* OLE parsing of the `.doc` WordDocument stream recovered the original template text more completely, including `期 末 考 查 报 告`, `系别：信息工程学院`, `专业：软件技术`, `年级：2024级`, `指导教师：项叙淋`, `项目名称`, `项目目的`, `项目内容及要求`, `个人总结`, `学生签名`, and `指导教师签字（签章）`.
* System-level LibreOffice installation was blocked because `sudo apt-get` requires a password in this environment.

## Requirements

* Convert or otherwise reuse the original `.doc` template so the final deliverable reflects the original cover and formatting.
* Preserve the report content already generated for the dorm repair management system.
* Keep the final output offline-openable, with diagrams embedded in the Word file.
* Save a regenerated final `.docx` under `SoftwareEngineering/generated/`.
* Keep a reproducible generation path in `SoftwareEngineering/generate_dorm_repair_report.py`.

## Acceptance Criteria

* [x] A converted `.docx` version of the original template exists, or a clear fallback template replica is generated if conversion is impossible.
* [x] The final report starts from the original cover/template rather than the previous generic cover.
* [x] The final report can be opened and parsed as `.docx`.
* [x] The final report contains the existing complete report content and all 8 embedded diagrams.
* [x] The user is told which personal fields still require manual filling.

## Out of Scope

* Filling in personal identity fields without user-provided data.
* Submitting the assignment to a course platform.

## Technical Notes

* Best path would be to install LibreOffice Writer and use headless conversion from `.doc` to `.docx`, then append/merge generated content with `python-docx`.
* Actual path used: recovered template text from the OLE WordDocument stream and replicated the original cover/section structure in `python-docx`.
* Validation: regenerated `.docx` parses successfully and contains 115 paragraphs, 3 tables, 8 inline images, 8 embedded media files, original template cover text, template project sections, signature area, and footer page-number field.
