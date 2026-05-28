# Diagram Review

Reviewed against the Software Engineering assignment requirements and the current `宿舍报修管理系统` design.

## Results

| Diagram | Review Result | Fix Applied |
|---|---|---|
| UML 类图 | Acceptable after cleanup | Kept class compartments and added clearer association names/multiplicity labels. |
| 顶层 DFD | Acceptable | Already used external entities, a single process, and data flows. |
| 0 层 DFD | Needed notation fix | Replaced database cylinder symbols with DFD-style double-line data stores; kept source/sink, process, data flow, and data store notation separate. |
| UML 状态图 | Needed logic fix | Corrected cancellation transition to originate from `待提交`; kept start/final nodes and event labels. |
| 系统结构图 | Needed layout fix | Rebuilt as a tree-style hierarchical module chart derived from P1-P5 in the 0-level DFD. |
| 程序流程图 | Needed notation fix | Replaced generic rectangles with standard input/output parallelograms, process rectangles, decisions, terminators, and directed flow arrows. |
| N-S 图 | Needed notation fix | Rebuilt as a pure structured N-S chart with sequence, loop, and IF/THEN/ELSE blocks; removed flowchart diamonds/arrows. |
| UML 用例图 | Needed relationship fix | Replaced plain dashed lines with dashed arrows for `<<include>>` and `<<extend>>`, preserving actors and system boundary. |

## Consistency Checks

* Diagrams use the same actors as the report: 学生、管理员、维修员、后勤部门.
* DFD process names align with the structure chart modules: 报修申请、工单审核、派工处理、维修反馈、统计查询.
* Detailed-design diagrams align with the selected modules: 报修申请受理模块 and 派工处理模块.
* The PDL and test cases still target 报修申请受理模块.
* Regenerated Word outputs contain 8 embedded images and remain valid OpenXML packages.

## Final Polish

* 图 1：relationship lines were rerouted as cleaner orthogonal/short line segments; labels and multiplicities were moved away from class-box borders and text compartments.
* 图 3：long diagonal DFD flows were rerouted as orthogonal paths; labels were manually placed away from process/data-store frames and arrowheads.
