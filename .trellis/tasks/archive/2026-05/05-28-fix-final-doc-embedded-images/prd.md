# Fix Final Doc Embedded Images

## Goal

Produce a final `.doc` deliverable that can be used for submission and does not depend on external linked images.

## Problem

The user manually imported the generated `.docx` content into the original `.doc` template. Inspection of `SoftwareEngineering/宿舍报修管理系统软件工程导论期末考查报告.doc` showed `INCLUDEPICTURE https://github.com/...` fields for at least Figure 1 and Figure 3, creating a risk that images fail offline or when Word/WPS blocks external links.

## Requirements

* Preserve the original template cover and report content.
* Ensure all required figures are embedded locally rather than requiring GitHub links.
* Ensure figure captions for Figure 1 and Figure 4 are present.
* Prefer a final `.doc` output because the user wants the original template format.
* Keep a `.docx` compatibility source if `.doc` conversion requires office tooling.

## Acceptance Criteria

* [x] A final `.doc` exists under `SoftwareEngineering/`.
* [x] The final `.doc` does not contain `INCLUDEPICTURE https://github.com`.
* [x] The final `.doc` contains all major assignment sections and required test coverage text.
* [x] The final `.doc` contains embedded image data.
* [x] A `.docx` source with all images embedded is also available.

## Verification Notes

* Final file: `SoftwareEngineering/宿舍报修管理系统软件工程导论期末考查报告.doc`.
* The final `.doc` is generated as Word/WPS-compatible RTF content with a `.doc` filename, preserving the requested template-style cover and embedding all 8 PNG diagrams with `\pict\pngblip`.
* Offline checks on the final `.doc` found `INCLUDEPICTURE = 0`, `github.com = 0`, and embedded PNG picture blocks = 8.
* Decoded RTF text contains the cover fields, five assignment sections, testing content, captions for 图 1 / 图 3 / 图 4 / 图 8, personal summary, and signature fields.
* Compatibility sources are preserved as generated `.docx` files and a generated `.mht` copy.
