from copy import deepcopy

from libreevolve.problems.benchmarks.alphaevolve_citation_use_inventory_boundary import (
    ALPHAEVOLVE_CITATION_USE_INVENTORY_BOUNDARY_SCHEMA,
    alphaevolve_citation_use_inventory_boundary_record,
    render_alphaevolve_citation_use_inventory_boundary_summary,
    validate_alphaevolve_citation_use_inventory_boundary,
)


def test_citation_use_inventory_resolves_retained_tex_and_bibliography():
    boundary = alphaevolve_citation_use_inventory_boundary_record()

    validation = validate_alphaevolve_citation_use_inventory_boundary(boundary)

    assert validation.ok is True
    assert boundary["schema"] == ALPHAEVOLVE_CITATION_USE_INVENTORY_BOUNDARY_SCHEMA
    assert boundary["source_artifact"]["identity_ok"] is True
    assert boundary["citation_linkage_inventory_ready"] is True
    assert boundary["semantic_claim_mapping_ready"] is False
    assert boundary["alphaevolve_parity_claim_ready"] is False
    assert validation.citation_occurrence_count == 195
    assert validation.citation_key_link_count == 240
    assert validation.unique_cited_key_count == 120
    assert validation.unresolved_citation_key_count == 0
    assert validation.semantic_gap_count == 195
    assert boundary["todo_owned_semantic_gap_count"] == 195
    assert boundary["citation_command_counts"] == {
        "authoryearcite": 1,
        "authoryearcitet": 1,
        "cite": 49,
        "citep": 134,
        "citet": 10,
    }
    assert boundary["citation_source_file_counts"] == {
        "appendix.tex": 81,
        "discussion.tex": 2,
        "introduction.tex": 16,
        "main.tex": 1,
        "methods.tex": 4,
        "related_work.tex": 54,
        "results.tex": 37,
    }
    assert boundary["bibliography_sources"] == {
        "bibtex_member": "literature.bib",
        "bibtex_entry_count": 172,
        "compiled_bibliography_member": "main.bbl",
        "compiled_bibliography_entry_count": 120,
        "pdf_reference_manifest": "papers/references.json",
        "pdf_reference_manifest_entry_count": 120,
    }
    assert boundary["unused_bibtex_entry_count"] == 52
    assert boundary["unresolved_citation_keys"] == []
    assert boundary["uncited_compiled_bibliography_keys"] == []
    assert boundary["missing_compiled_bibtex_keys"] == []
    assert all(
        record["all_keys_resolved"]
        for record in boundary["citation_use_records"]
    )


def test_citation_use_inventory_preserves_source_and_optional_note_anchors():
    boundary = alphaevolve_citation_use_inventory_boundary_record()

    first = boundary["citation_use_records"][0]
    noted = next(
        record
        for record in boundary["citation_use_records"]
        if record["optional_arguments"] == ["page 75"]
    )

    assert first["citation_use_id"] == "tex_citation_0001"
    assert first["source_file"] == "main.tex"
    assert first["source_line"] == 33
    assert first["section_path"] == ["Abstract"]
    assert first["command"] == "authoryearcite"
    assert first["citation_keys"] == ["paredes2023mathematical"]
    assert first["reference_links"][0]["reference_id"] is not None
    assert noted["source_file"] == "appendix.tex"
    assert noted["command"] == "cite"
    assert noted["citation_keys"] == ["vinuesa2010generalized"]
    assert noted["command_text"] == "\\cite[page 75]{vinuesa2010generalized}"
    assert all(
        record["semantic_classification_status"] == "unclassified"
        and record["implementation_relevance_status"] == "not_assessed"
        for record in boundary["citation_use_records"]
    )


def test_citation_use_inventory_rejects_record_and_overclaim_drift():
    boundary = deepcopy(alphaevolve_citation_use_inventory_boundary_record())
    boundary["citation_occurrence_count"] = 194
    boundary["citation_use_records"][0]["citation_keys"] = ["changed"]
    boundary["semantic_claim_mapping_ready"] = True
    boundary["alphaevolve_parity_claim_ready"] = True

    validation = validate_alphaevolve_citation_use_inventory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_citation_occurrence_count" in codes
    assert "invalid_citation_use_records" in codes
    assert "semantic_mapping_overclaim" in codes
    assert "parity_overclaim" in codes


def test_citation_use_inventory_rejects_missing_source_archive(tmp_path):
    boundary = alphaevolve_citation_use_inventory_boundary_record(tmp_path)

    validation = validate_alphaevolve_citation_use_inventory_boundary(
        boundary,
        root=tmp_path,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert boundary["citation_linkage_inventory_ready"] is False
    assert "source_archive_identity_mismatch" in codes
    assert "source_inventory_incomplete" in codes
    assert "unowned_semantic_gap" not in codes


def test_render_citation_use_inventory_summary_reports_shape():
    summary = render_alphaevolve_citation_use_inventory_boundary_summary(
        alphaevolve_citation_use_inventory_boundary_record()
    )

    assert "AlphaEvolve citation-use inventory boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| citation_occurrence_count | 195 |" in summary
    assert "| citation_key_link_count | 240 |" in summary
    assert "| unique_cited_key_count | 120 |" in summary
    assert "| unresolved_citation_key_count | 0 |" in summary
    assert "| semantic_gap_count | 195 |" in summary
