# Review and Improve SoftwareEngineering Diagrams

## Goal

Review every diagram generated for the Software Engineering homework report against the expected notation for its diagram type, then regenerate any diagram that does not meet the assignment's drawing standards or the dorm repair management system design.

## What I Already Know

* Existing report generation script: `SoftwareEngineering/generate_dorm_repair_report.py`.
* Existing diagram PNGs are under `SoftwareEngineering/generated/images/`.
* The assignment requires diagrams to be规范、标注清晰、逻辑严谨 and consistent with the selected `宿舍报修管理系统`.
* The report currently contains:
  * UML 类图
  * 顶层 DFD
  * 0 层 DFD
  * 报修工单 UML 状态图
  * 系统结构图
  * 报修申请受理模块程序流程图
  * 派工处理模块 N-S 图
  * UML 用例图

## Requirements

* Review all 8 diagrams against the conventions of their diagram type.
* Replace non-standard or weak diagrams directly in the generation script.
* Keep diagrams consistent with the report's selected system, modules, data stores, actors, PDL pseudocode, and tests.
* Preserve the original-template report structure and Word/WPS-compatible `.docx` output.
* Regenerate both the Chinese filename `.docx` and ASCII compatibility copy.

## Acceptance Criteria

* [x] UML class diagram uses class compartments, class attributes/methods, relationships, labels, and multiplicity consistently.
* [x] DFD diagrams use standard DFD notation: external entities, processes, data flows, and data stores; no flowchart symbols are mixed into DFDs.
* [x] State diagram uses UML start/final nodes, rounded states, and event/condition transition labels.
* [x] System structure chart is a clear hierarchical module decomposition derived from the 0-level DFD.
* [x] Detailed-design flowchart uses standard flowchart symbols: start/end, input/output, process, decision, loop, and clear arrow direction.
* [x] N-S chart uses structured blocks without arbitrary arrows and clearly represents sequence, loop, and branch.
* [x] Use case diagram uses system boundary, actors, use cases, associations, include/extend labels, and consistent actors.
* [x] Regenerated Word files remain valid zip/OpenXML and contain 8 embedded images.

## Out of Scope

* Changing the selected system.
* Rewriting the report content beyond captions/diagram generation if not needed.
* Filling personal cover fields.

## Technical Notes

* Diagrams are generated programmatically with Pillow in `SoftwareEngineering/generate_dorm_repair_report.py`.
* Review notes are recorded in `SoftwareEngineering/generated/diagram_review.md`.
* Validation after regeneration: both `.docx` outputs are valid zip/OpenXML packages and parse with `python-docx`; each contains 115 paragraphs, 3 tables, 8 inline images, and 8 embedded media files.
