import json

from libreevolve.problems.benchmarks.paper_bibliography import (
    ALPHAEVOLVE_REFERENCES_SECTION_SCHEMA,
    alphaevolve_references_section_record,
    render_alphaevolve_references_section_summary,
    validate_alphaevolve_references_section,
)


def _page_texts():
    pages = {page: "" for page in range(23, 33)}
    pages[23] = "References\n" + "\n".join(f"[{index}] reference {index}" for index in range(1, 10))
    pages[24] = "\n".join(f"[{index}] reference {index}" for index in range(10, 23))
    pages[25] = "\n".join(f"[{index}] reference {index}" for index in range(23, 36))
    pages[26] = "\n".join(f"[{index}] reference {index}" for index in range(36, 48))
    pages[27] = "\n".join(f"[{index}] reference {index}" for index in range(48, 61))
    pages[28] = "\n".join(f"[{index}] reference {index}" for index in range(61, 72))
    pages[29] = "\n".join(f"[{index}] reference {index}" for index in range(72, 84))
    pages[30] = "\n".join(f"[{index}] reference {index}" for index in range(84, 96))
    pages[31] = "\n".join(f"[{index}] reference {index}" for index in range(96, 109))
    pages[32] = "\n".join(f"[{index}] reference {index}" for index in range(109, 121))
    pages[23] += "\nAccurate structure prediction of biomolecular interactions"
    pages[23] += "\nAI achieves silver-medal standard solving"
    pages[23] += "\nA survey on the kissing numbers"
    pages[27] += "\nConsequences of the Moosbauer-Poole algorithms"
    pages[30] += "\nCan LLMs generate novel research ideas"
    pages[32] += "\nHypothesis generation with large language models"
    return pages


def test_validate_alphaevolve_references_section_accepts_builtin_record():
    recordset = alphaevolve_references_section_record()

    validation = validate_alphaevolve_references_section(
        recordset,
        page_text_by_number=_page_texts(),
    )

    assert recordset["schema"] == ALPHAEVOLVE_REFERENCES_SECTION_SCHEMA
    assert validation.ok is True
    assert validation.reference_count == 120
    assert validation.page_count == 10
    assert validation.source_text_checked is True
    assert validation.issues == []


def test_validate_alphaevolve_references_section_loads_json_file(tmp_path):
    path = tmp_path / "references_section.json"
    path.write_text(json.dumps(alphaevolve_references_section_record()), encoding="utf-8")

    validation = validate_alphaevolve_references_section(path)

    assert validation.ok is True
    assert validation.source_text_checked is False


def test_validate_alphaevolve_references_section_rejects_reference_id_drift():
    recordset = alphaevolve_references_section_record()
    recordset["reference_count"] = 119
    recordset["reference_ids"] = recordset["reference_ids"][:-1]

    validation = validate_alphaevolve_references_section(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_reference_count" in codes
    assert "reference_ids_mismatch" in codes


def test_validate_alphaevolve_references_section_rejects_page_range_drift():
    recordset = alphaevolve_references_section_record()
    recordset["source_page_span"]["last_page"] = 31
    recordset["page_ranges"][0]["last_reference_id"] = "8"

    validation = validate_alphaevolve_references_section(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_last_page" in codes
    assert "page_ranges_mismatch" in codes


def test_validate_alphaevolve_references_section_rejects_source_text_drift():
    pages = _page_texts()
    pages[23] = pages[23].replace("[1]", "[2]", 1)
    pages[32] = pages[32].replace("Hypothesis generation with large language models", "")

    validation = validate_alphaevolve_references_section(
        alphaevolve_references_section_record(),
        page_text_by_number=pages,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "extracted_reference_ids_mismatch" in codes
    assert "extracted_page_range_mismatch" in codes
    assert "missing_extracted_anchor_phrase" in codes


def test_validate_alphaevolve_references_section_rejects_normalization_overclaims():
    recordset = alphaevolve_references_section_record()
    recordset["normalization_status"]["author_title_venue_fields_complete"] = True
    recordset["normalization_status"]["claim_links_complete"] = True
    recordset["normalization_status"]["manifest_titles_authoritative"] = True

    validation = validate_alphaevolve_references_section(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_normalization_author_title_venue_fields_complete" in codes
    assert "invalid_normalization_claim_links_complete" in codes
    assert "invalid_normalization_manifest_titles_authoritative" in codes


def test_render_alphaevolve_references_section_summary_reports_shape():
    summary = render_alphaevolve_references_section_summary(
        alphaevolve_references_section_record()
    )

    assert "AlphaEvolve references-section evidence" in summary
    assert "| schema_status | ok |" in summary
    assert "| reference_count | 120 |" in summary
    assert "| page_count | 10 |" in summary
