# SoftwareEngineering Homework

## Goal

Complete the Software Engineering final assessment report under `SoftwareEngineering/`, following the provided assignment requirements and report template as closely as the local environment allows.

## What I Already Know

* The assignment file is `SoftwareEngineering/软件工程导论期末大作业试题.docx`.
* The report template file is `SoftwareEngineering/《软件工程导论》期末考查报告模板.doc`.
* The selected system is `宿舍报修管理系统`.
* The user confirmed that a new `.docx` final report is acceptable.
* The selectable systems are limited to:
  * 图书借阅系统
  * 学生教务管理系统
  * 超市订单管理系统
  * 宿舍报修管理系统
* Custom simple systems are explicitly prohibited.
* The report must include requirements analysis, overall design, detailed design, coding/pseudocode, software testing, and a UML use case diagram.
* All diagrams and written sections must stay consistent with each other.

## Assumptions

* The final deliverable can be a `.docx` report if direct editing of the legacy `.doc` template is not practical in this environment.
* The user will provide personal information required by the cover page, such as name, student ID, class, and instructor, because those must be accurate.
* The user will review the final report before submission and confirm it matches course expectations.

## Requirements

* Use `宿舍报修管理系统` as the selected small/medium transaction management information system.
* Generate a new `.docx` report under `SoftwareEngineering/`.
* Leave accurate personal cover-page metadata as placeholders if the user has not provided it.
* Explain the selected lifecycle model and why it fits the system.
* Describe at least three core functions.
* Provide either an E-R diagram or UML class diagram with at least three entities/classes and clear relationships.
* Provide layered DFD diagrams: top-level DFD and level-0 DFD.
* Provide a UML state diagram for one core business entity.
* Convert the level-0 DFD into a hierarchical system structure chart.
* Choose two modules containing branch and loop logic, then describe them with two different detailed-design diagrams selected from program flowchart, N-S chart, and PAD chart.
* Write PDL pseudocode or runnable code for one module from the detailed-design section.
* Design white-box and black-box test cases for one function containing nested branches and loops.
* Cover white-box standards: statement coverage, decision-condition coverage, condition combination coverage, and independent path coverage.
* Cover black-box standards: equivalence partitioning and boundary value analysis, including normal and robust boundary tests.
* Provide a complete UML use case diagram with system boundary, actors, core use cases, and include/extend relationships.

## Acceptance Criteria

* [x] Report content covers every scoring item from the assignment.
* [x] Chosen system is one of the four allowed systems.
* [x] Diagrams and prose use consistent actors, modules, data stores, entities, and functions.
* [x] Code or pseudocode matches the selected detailed-design module.
* [x] Test cases match the selected code or pseudocode.
* [x] Final deliverable is saved under `SoftwareEngineering/`.
* [x] Any personal cover-page fields that require user input are clearly identified.

## Definition of Done

* Draft report generated.
* Diagram source files generated or embedded where practical.
* Final files are easy for the user to open and review.
* Any parts that require the user personally to fill in are explicitly listed.

## Out of Scope

* Falsifying personal identity, class, or submission metadata.
* Logging into course systems or submitting the assignment on behalf of the user.
* Guaranteeing the teacher's final score.

## Technical Notes

* `.docx` assignment text was extracted from `word/document.xml`.
* The local environment currently has Python only for document processing; `pandoc`, `libreoffice`, `antiword`, and `catdoc` were not found.
* The `.doc` template is a legacy binary Word document, so exact template modification may require Word/WPS/LibreOffice if no local converter is available.
* `python-docx` and `Pillow` were installed into `/tmp/finalexams-pydeps` and used only for generation; the final `.docx` is self-contained and can be opened offline.
* Generated final report: `SoftwareEngineering/generated/宿舍报修管理系统软件工程导论期末考查报告.docx`.
* Validation: the generated `.docx` re-opened successfully with `python-docx`, contains 96 paragraphs, 3 tables, 8 inline images, and 8 embedded `word/media/*.png` files.
* Git commit step could not be performed because `/home/tthm/workspace/FinalExams` is not a Git repository.
