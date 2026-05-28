# Fix Diagram Layout Topology for Figures 1 and 3

## Goal

Fix severe layout defects in Figure 1 (UML class diagram) and Figure 3 (level-0 DFD) so the diagrams are suitable for a rigorous academic report.

## Requirements

* Do not add or remove business elements or change system logic.
* Ensure text inside every node/rectangle stays within its border by enlarging nodes or wrapping text.
* Rebuild relative node placement for Figure 1 and Figure 3.
* Use clear orthogonal routing for lines.
* Avoid line crossings and line/text/frame collisions as far as possible.
* Use added spacing/layout channels where necessary to keep exported PNGs clean.
* Regenerate affected PNGs and both Word outputs.
* Validate Word output remains offline-openable and embeds 8 images.

## Acceptance Criteria

* [x] Figure 1 has no text overflowing class boxes and no obvious line/label overlap.
* [x] Figure 1 relationships are routed in separated channels with minimal/no crossings.
* [x] Figure 3 has no text overflowing process/data-store/entity boxes.
* [x] Figure 3 data flows are routed in clear orthogonal lanes with no obvious line crossings.
* [x] Both `.docx` outputs remain valid zip/OpenXML and parse with `python-docx`.
* [x] Changes are committed and pushed.

## Technical Notes

* Relevant file: `SoftwareEngineering/generate_dorm_repair_report.py`.
* Relevant outputs:
  * `SoftwareEngineering/generated/images/01_uml_class_diagram.png`
  * `SoftwareEngineering/generated/images/03_level0_dfd.png`
  * `SoftwareEngineering/generated/dorm_repair_report_compatible.docx`
* Figure 1 was expanded to `2300x1550`.
* Figure 3 was expanded to `2600x1750`.
* Figure 3 uses layered orthogonal lanes to separate business flows, data-store flows, and reporting flows.
