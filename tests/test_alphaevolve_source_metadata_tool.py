import json

from libreevolve.tools.alphaevolve_source_metadata import (
    build_alphaevolve_source_metadata_report,
    main,
)


def test_alphaevolve_source_metadata_report_extracts_retained_artifacts():
    report = build_alphaevolve_source_metadata_report(".")

    assert report["ok"] is True
    assert report["artifact_count"] == 5
    assert report["script_artifact"]["path"] == "libreevolve/tools/alphaevolve_source_metadata.py"
    assert (
        report["artifacts"]["arxiv_abstract_html"]["sha256"]
        == "ab39ec118afe0874f34179b5a06c42a57799b1103f027942a1ecd54dc3d95471"
    )
    assert report["artifacts"]["cached_pdf_first_page"]["markers"]["has_arxiv_header"] is True
    assert report["artifacts"]["datacite_full_response"]["creator_count"] == 18
    assert report["artifacts"]["tex_archive"]["member_count"] == 58


def test_alphaevolve_source_metadata_cli_outputs_json(capsys):
    exit_code = main(["--root", "."])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["schema"] == "libreevolve.alphaevolve_source_metadata_extraction.v1"
    assert payload["ok"] is True
