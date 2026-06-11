from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_FOLLOW_ON_MATH_SOURCE_SCHEMA = "libreevolve.alphaevolve_follow_on_math_source.v1"
ALPHAEVOLVE_FOLLOW_ON_SOURCE_MANIFEST_SCHEMA = (
    "libreevolve.alphaevolve_follow_on_source_manifest.v1"
)
ALPHAEVOLVE_FOLLOW_ON_REPOSITORY_RIGHTS_SCHEMA = (
    "libreevolve.alphaevolve_follow_on_repository_rights.v1"
)
ALPHAEVOLVE_FOLLOW_ON_REPOSITORY_RIGHTS_MANIFEST_SCHEMA = (
    "libreevolve.alphaevolve_follow_on_repository_rights_manifest.v1"
)
ALPHAEVOLVE_FOLLOW_ON_RUNTIME_ABSENCE_SCHEMA = (
    "libreevolve.alphaevolve_follow_on_runtime_absence.v1"
)
ALPHAEVOLVE_FOLLOW_ON_RUNTIME_ABSENCE_MANIFEST_SCHEMA = (
    "libreevolve.alphaevolve_follow_on_runtime_absence_manifest.v1"
)
ALPHAEVOLVE_FOLLOW_ON_TAO_BLOG_SCHEMA = (
    "libreevolve.alphaevolve_follow_on_tao_blog.v1"
)
ALPHAEVOLVE_FOLLOW_ON_TAO_BLOG_MANIFEST_SCHEMA = (
    "libreevolve.alphaevolve_follow_on_tao_blog_manifest.v1"
)
EXPECTED_FOLLOW_ON_SOURCE_MANIFEST_FILE = "papers/follow_on_sources.json"
EXPECTED_FOLLOW_ON_REPOSITORY_RIGHTS_MANIFEST_FILE = (
    "papers/follow_on_repository_rights.json"
)
EXPECTED_FOLLOW_ON_RUNTIME_ABSENCE_MANIFEST_FILE = (
    "papers/follow_on_runtime_absence.json"
)
EXPECTED_FOLLOW_ON_PROBLEM_COVERAGE_SCHEMA = (
    "libreevolve.alphaevolve_follow_on_problem_coverage.v1"
)
EXPECTED_FOLLOW_ON_TAO_BLOG_MANIFEST_FILE = "papers/follow_on_tao_blog.json"
EXPECTED_ORIGINAL_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_FOLLOW_ON_ARXIV_ID = "2511.02864"
EXPECTED_FOLLOW_ON_VERSION = 3
EXPECTED_FOLLOW_ON_VERSIONED_ID = "2511.02864v3"
EXPECTED_FOLLOW_ON_TITLE = "Mathematical exploration and discovery at scale"
EXPECTED_FOLLOW_ON_REVISION_DATE = "2025-12-22"
EXPECTED_FOLLOW_ON_CATEGORY = "cs.NE"
EXPECTED_FOLLOW_ON_AUTHORS = (
    "Bogdan Georgiev",
    "Javier Gomez-Serrano",
    "Terence Tao",
    "Adam Zsolt Wagner",
)
EXPECTED_REPOSITORY_NAME = "google-deepmind/alphaevolve_repository_of_problems"
EXPECTED_REPOSITORY_URL = f"https://github.com/{EXPECTED_REPOSITORY_NAME}"
EXPECTED_REPOSITORY_COMMIT = "".join(
    ["bfd2", "24d0", "e776", "3f89", "eb4a", "8efe", "93ac", "1260", "91f8", "5ed9"]
)
EXPECTED_README_SHA256 = "".join(
    [
        "cecf",
        "8d52",
        "3151",
        "ca5e",
        "174f",
        "306f",
        "a52e",
        "f804",
        "1350",
        "e3ac",
        "6128",
        "6cbb",
        "744a",
        "312a",
        "029a",
        "1543",
    ]
)
EXPECTED_README_BYTES = 4425
EXPECTED_DECLARED_PROBLEM_COUNT = 67
EXPECTED_ARTIFACT_KINDS = (
    "problem_pages",
    "colab_notebooks_many_not_all",
    "prompts",
    "verification_code",
    "initial_programs",
    "final_evolved_programs",
    "visualization_or_analysis_where_appropriate",
)
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_COMMIT_RE = re.compile(r"[0-9a-f]{40}")
EXPECTED_FOLLOW_ON_REPOSITORY_RIGHTS_SURFACES = {
    "README.md",
    "ROADMAP.md",
    "papers/README.md",
    "docs/todo/code.md",
    "docs/todo/papers.md",
    "docs/todo/readme.md",
    "docs/todo/roadmap.md",
}
EXPECTED_FOLLOW_ON_REPOSITORY_LICENSE_MAPPING = {
    "notebook_code": "Apache-2.0",
    "verification_code": "Apache-2.0",
    "analysis_code": "Apache-2.0",
    "initial_programs": "Apache-2.0",
    "final_evolved_programs": "Apache-2.0",
    "visualization_code": "Apache-2.0",
    "problem_pages": "CC-BY-4.0",
    "problem_statements": "CC-BY-4.0",
    "notebook_prompt_text": "CC-BY-4.0",
    "status_artifacts": "CC-BY-4.0",
    "result_distribution_artifacts": "CC-BY-4.0",
}
EXPECTED_FOLLOW_ON_RUNTIME_SURFACES = {
    "README.md",
    "ROADMAP.md",
    "papers/README.md",
    "docs/todo/code.md",
    "docs/todo/papers.md",
    "docs/todo/readme.md",
    "docs/todo/roadmap.md",
}
EXPECTED_FOLLOW_ON_NOTEBOOK_ARTIFACT_KINDS = (
    "prompt",
    "verification_code",
    "initial_program",
    "final_evolved_programs",
    "visualization_or_analysis_where_appropriate",
)
EXPECTED_FOLLOW_ON_NOTEBOOKS = (
    ("experiments/autocorrelation_problems/autocorrelation_problems.ipynb", 740589, "617eeebbc391d535b82139f0a63f677074e16dca"),
    ("experiments/classical_inequalities/classical_inequalities.ipynb", 32330, "07709bb38cde8ef2b4f1ef7d5a5452db2d372848"),
    ("experiments/difference_bases/difference_bases.ipynb", 68217, "0cdb812ada3b6053f749e05301a743fd191e8700"),
    ("experiments/edges_vs_triangles/edges_vs_triangles.ipynb", 92456, "e83e4a01c31ee122137c6826bcd1e6272f2fc1e2"),
    ("experiments/equidistant_points_in_convex_polygons/Equidistant_points_in_convex_polygons.ipynb", 3183232, "160c7e47e7d8827310877092b9f0835194922573"),
    ("experiments/erdos_szekeres_happy_ending_problem/happy_ending_problem.ipynb", 16831, "7ecb9ca73d4deecb94bf6c26a2be70f1a5d5f05e"),
    ("experiments/finite_field_kakeya_problem/finite_field_kakeya.ipynb", 176127, "ad7d55fc67eb191cbac38dea078787549cd85cc6"),
    ("experiments/finite_field_nikodym_problem/finite_field_nikodym.ipynb", 97138, "228345fbbe29d6f9913239d4fd44ad53287cf759"),
    ("experiments/finite_field_sum_product_problem/finite_field_sum_product.ipynb", 30069, "5d1c3f1609bf3a8a470ccb9845ef1117fddc1fba"),
    ("experiments/flat_polynomials/flat_polynomials.ipynb", 72500, "b3276c9d212402e7e1e48faf72e33868ee1881c0"),
    ("experiments/imo_2025_p6/imo_2025_p6.ipynb", 20175, "b39631272746893fe395eecbd02e4d47cd605927"),
    ("experiments/kakeya_needle_2d/kakeya_needle_2d.ipynb", 72281, "1f01477b857ea9a5a07d30f4ee49db3e135f64e7"),
    ("experiments/kakeya_needle_3d/kakeya_needle_3d.ipynb", 237723, "0a7a1667536ec779d72989de0c3622e0d23506a0"),
    ("experiments/kissing_cylinders/kissing_cylinders.ipynb", 94134, "14d14daf90e511f3c988989b21354fbf6e201fd7"),
    ("experiments/no_5_on_a_sphere/no_5_on_a_sphere.ipynb", 103026, "0e8b3b4da863c316ab7207d78e2c04f551baa185"),
    ("experiments/ovals_problem/ovals_problem.ipynb", 19563, "b47cfee8cddc895ff1d8b2edf3bccf1aae31f3d7"),
    ("experiments/packing_circles_max_sum_of_radii/packing_circle_max_sum_of_radii.ipynb", 77546, "0f4de7b576720a3116c0aa8a3d6e9b5c12a6a92e"),
    ("experiments/packing_unit_cubes/packing_unit_cubes.ipynb", 124215, "c147faa3323f47a64f1c2127ea35c1eadac590d1"),
    ("experiments/prime_number_theorem/prime_number_theorem.ipynb", 13841, "284319bcf534c5152b433a03f56126e955497ebc"),
    ("experiments/ring_loading_problem/ring_loading_problem.ipynb", 44196, "ea5abec2001c7002b2edcd59a27e04079293b5fb"),
    ("experiments/sphere_packing_uncertainty_principles/sphere_packing_uncertainty_principles.ipynb", 104990, "38badb91897a6fb822d4203458f277fe783885d0"),
    ("experiments/spherical_t_designs/spherical_t_designs.ipynb", 242167, "1134a81661580506e2599335ba051efbdb99e068"),
    ("experiments/subsets_of_the_grid_with_no_isosceles_triangles/no_isosceles_triangles.ipynb", 38367, "c0d665a986ece2f7efd220f2f179ebf2935149e5"),
    ("experiments/sums_differences_problems/sums_differences_problems.ipynb", 643544, "4f763db6d59b224e5ba9ebbab0e4e54683f74ea3"),
    ("experiments/tammes_problem/tammes_problem.ipynb", 117565, "360abdd1b160a180288cd2da07dd8f0f8b227d62"),
    ("experiments/the_2d_moving_sofa/the_2d_moving_sofa.ipynb", 18029403, "1125bb223c471d94d5ee32cc463a785b8f6a01be"),
    ("experiments/the_3d_moving_sofa/the_3d_moving_sofa.ipynb", 309704, "fff09e075abf6e4391248dd80dc1cb0b616b4926"),
    ("experiments/thomson_problem/thomson_problem.ipynb", 86472, "95871bcbb7f5fdf43749d3d17cf61d37fc476081"),
)
EXPECTED_FOLLOW_ON_NOTEBOOK_SHA256S = {
    "experiments/autocorrelation_problems/autocorrelation_problems.ipynb": "996e7e9dd20991fe06319d2c91e8af3501b48b14c2dd10e5ce3a95343ee071ba",
    "experiments/classical_inequalities/classical_inequalities.ipynb": "b51091f45790eb89b72cd05c344febe7d7571f2370a7a90e1d77294c5eefc03d",
    "experiments/difference_bases/difference_bases.ipynb": "e5bd224563055caf53c0fef9b9c67620c7124a14aa77094cce456d9927b65489",
    "experiments/edges_vs_triangles/edges_vs_triangles.ipynb": "f4db3301d6fa8a59b833127230dd3afce8392ae1240e0806b6213c90a693706c",
    "experiments/equidistant_points_in_convex_polygons/Equidistant_points_in_convex_polygons.ipynb": "aec48a4334aaa1a5ceb342677e5ee34a5a4f0fc08da4b58a38f44f3eb7ef9188",
    "experiments/erdos_szekeres_happy_ending_problem/happy_ending_problem.ipynb": "e54087cec155baa2446cc66a05a6b0f593c76e186acad408f3ff2f9d32304fb0",
    "experiments/finite_field_kakeya_problem/finite_field_kakeya.ipynb": "bc445b9a522ee1b0ea78e66536c90ca7e3b67071e07065b0d878e313852ce65b",
    "experiments/finite_field_nikodym_problem/finite_field_nikodym.ipynb": "cd9be3d00417ed9f9aeb88e19d481bef692a1f72050157dd54ee22a176d734d8",
    "experiments/finite_field_sum_product_problem/finite_field_sum_product.ipynb": "feeb2e1b6d77e3146863ab5cfc8b2588cc7575fb92745c4ce72747575043adaf",
    "experiments/flat_polynomials/flat_polynomials.ipynb": "c6cb19c14077ccf20dbf2422a6d8bb5cb2f6c44fbc670569770a550e1234e6ef",
    "experiments/imo_2025_p6/imo_2025_p6.ipynb": "14944077e2f9d66f2f96872b72d7bd53cb1a1af5512894e97950516387cb60f6",
    "experiments/kakeya_needle_2d/kakeya_needle_2d.ipynb": "cee72a338df6f26a46813962b113daaf1c1d6a4210ac2af39e3becb758ca3810",
    "experiments/kakeya_needle_3d/kakeya_needle_3d.ipynb": "2a503d78432fb1d7c218e9c53538e2e260e137fabf4dcc54eb6d1a51fa1c3652",
    "experiments/kissing_cylinders/kissing_cylinders.ipynb": "d36aa867912149024c0da16eea5b2d3f73af805d2049d86892c92b26b17cd51a",
    "experiments/no_5_on_a_sphere/no_5_on_a_sphere.ipynb": "0af65a39d7b5d5d55ba078d19b6dae4b410c66c3395101234a09f0223e5af075",
    "experiments/ovals_problem/ovals_problem.ipynb": "5745654087376d544b6414ff0777452cb56f3d1f00dcca37decb07a79b1b71df",
    "experiments/packing_circles_max_sum_of_radii/packing_circle_max_sum_of_radii.ipynb": "e7a304378a5ca80c74f94f5060a9f5db953767af850834513fd797e3306a935e",
    "experiments/packing_unit_cubes/packing_unit_cubes.ipynb": "a260a6a7a75da3d1bf3242483beb2fce902b995fc5c34ca87e9573af5c7c2326",
    "experiments/prime_number_theorem/prime_number_theorem.ipynb": "a66dd0674ace2a3e0771779b92292ce577f21bdb5af0b310b6456b322e59fbba",
    "experiments/ring_loading_problem/ring_loading_problem.ipynb": "360ec04a8fa80654d54f4a32c9c31377ae2b78505444aa454161590dad2f7003",
    "experiments/sphere_packing_uncertainty_principles/sphere_packing_uncertainty_principles.ipynb": "5ce6c2d79fbaa9babd235cf69fbbc14247091baec041551ed3d79645088b179e",
    "experiments/spherical_t_designs/spherical_t_designs.ipynb": "6d117c8044884bb87a461292dc1aafd2056f15a622103665e2e2135cb4b86b27",
    "experiments/subsets_of_the_grid_with_no_isosceles_triangles/no_isosceles_triangles.ipynb": "653accd24369672f1cc757b203dae311f1489895a1cb8e6242d3308fe657891d",
    "experiments/sums_differences_problems/sums_differences_problems.ipynb": "8ac90e85303e97dc5d69489a6393692d018f87ee5ac220216313ead97daa1da2",
    "experiments/tammes_problem/tammes_problem.ipynb": "2094a9b8cda3d05353fc76fbdbbe2de84745e2d43f31d63f75edcc727f5df150",
    "experiments/the_2d_moving_sofa/the_2d_moving_sofa.ipynb": "8e418dcaf572c0334a8b21040e22b570a23d2b3f64450f9a8a00a0756c145299",
    "experiments/the_3d_moving_sofa/the_3d_moving_sofa.ipynb": "a5b03434f3848bedcec5d47f87182660830209d811b4d31d3058357d3eabd73e",
    "experiments/thomson_problem/thomson_problem.ipynb": "c0171419f891ce81a9a112ce57ec2c8870724e803487e1600064621b08a49671",
}
EXPECTED_TAO_BLOG_URL = (
    "https://terrytao.wordpress.com/2025/11/05/"
    "mathematical-exploration-and-discovery-at-scale/"
)
EXPECTED_TAO_BLOG_API_URL = (
    "https://public-api.wordpress.com/rest/v1.1/sites/"
    "terrytao.wordpress.com/posts/slug:mathematical-exploration-and-discovery-at-scale"
)
EXPECTED_TAO_BLOG_POST_ID = 15811
EXPECTED_TAO_BLOG_TITLE = "Mathematical exploration and discovery at scale"
EXPECTED_TAO_BLOG_AUTHOR = "Terence Tao"
EXPECTED_TAO_BLOG_POST_DATE = "2025-11-05T22:36:56+00:00"
EXPECTED_TAO_BLOG_MODIFIED_DATE = "2025-11-06T17:14:40+00:00"
EXPECTED_TAO_BLOG_API_BYTES = 34570
EXPECTED_TAO_BLOG_API_SHA256 = "5b351f99976faa5061aaa52732d5d46bc1d09ee5f8ad20d2fac256a5826a3231"
EXPECTED_TAO_BLOG_HTML_BYTES = 378198
EXPECTED_TAO_BLOG_HTML_SHA256 = "929af5092a099abafef443b2d3dd1bf9c5f4a7df038be649dfb7b2174847c4bc"
EXPECTED_TAO_BLOG_CLAIM_CATEGORIES = (
    "commentary",
    "experiment_summary",
    "verifier_design_lesson",
    "negative_result",
    "proof_handoff",
    "future_work",
)
EXPECTED_TAO_BLOG_SURFACES = {
    "README.md",
    "ROADMAP.md",
    "papers/README.md",
    "docs/todo/code.md",
    "docs/todo/papers.md",
    "docs/todo/readme.md",
    "docs/todo/roadmap.md",
}


@dataclass(frozen=True)
class AlphaEvolveFollowOnMathSourceIssue:
    code: str
    message: str
    source_id: str | None = None


@dataclass(frozen=True)
class AlphaEvolveFollowOnMathSourceValidation:
    ok: bool
    source_count: int
    repository_ref_pinned: bool
    local_pdf_cache_available: bool
    issues: list[AlphaEvolveFollowOnMathSourceIssue]


@dataclass(frozen=True)
class AlphaEvolveFollowOnRepositoryRightsValidation:
    ok: bool
    rights_count: int
    citation_required: bool
    artifact_license_mapping_count: int
    issues: list[AlphaEvolveFollowOnMathSourceIssue]


@dataclass(frozen=True)
class AlphaEvolveFollowOnRuntimeAbsenceValidation:
    ok: bool
    runtime_absence_count: int
    notebook_count: int
    alphaevolve_runtime_available: bool
    verifier_code_available: bool
    issues: list[AlphaEvolveFollowOnMathSourceIssue]


@dataclass(frozen=True)
class AlphaEvolveFollowOnTaoBlogValidation:
    ok: bool
    source_count: int
    claim_category_count: int
    linked_repository_pinned: bool
    commentary_secondary: bool
    issues: list[AlphaEvolveFollowOnMathSourceIssue]


def alphaevolve_follow_on_math_source_record() -> dict[str, Any]:
    readme_raw_url = (
        "https://raw.githubusercontent.com/google-deepmind/"
        f"alphaevolve_repository_of_problems/{EXPECTED_REPOSITORY_COMMIT}/README.md"
    )
    return {
        "schema": ALPHAEVOLVE_FOLLOW_ON_MATH_SOURCE_SCHEMA,
        "source_family": "alphaevolve_follow_on_mathematics",
        "original_source_paper_id": EXPECTED_ORIGINAL_SOURCE_PAPER_ID,
        "scope_boundary": {
            "original_alphaevolve_spec_source": EXPECTED_ORIGINAL_SOURCE_PAPER_ID,
            "follow_on_evidence_source": EXPECTED_FOLLOW_ON_ARXIV_ID,
            "separates_original_spec_from_later_math_evidence": True,
            "not_original_alphaevolve_runtime_spec": True,
            "not_full_problem_inventory": True,
        },
        "paper": {
            "arxiv_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
            "version": EXPECTED_FOLLOW_ON_VERSION,
            "versioned_id": EXPECTED_FOLLOW_ON_VERSIONED_ID,
            "category": EXPECTED_FOLLOW_ON_CATEGORY,
            "latest_revision_date": EXPECTED_FOLLOW_ON_REVISION_DATE,
            "title": EXPECTED_FOLLOW_ON_TITLE,
            "authors": list(EXPECTED_FOLLOW_ON_AUTHORS),
            "abs_url": f"https://arxiv.org/abs/{EXPECTED_FOLLOW_ON_ARXIV_ID}",
            "versioned_abs_url": f"https://arxiv.org/abs/{EXPECTED_FOLLOW_ON_VERSIONED_ID}",
            "floating_pdf_url": f"https://arxiv.org/pdf/{EXPECTED_FOLLOW_ON_ARXIV_ID}.pdf",
            "versioned_pdf_url": f"https://arxiv.org/pdf/{EXPECTED_FOLLOW_ON_VERSIONED_ID}",
            "local_cache": {
                "available": False,
                "manifest_row_present": False,
                "file": None,
                "sha256": None,
                "bytes": None,
            },
        },
        "repository": {
            "name": EXPECTED_REPOSITORY_NAME,
            "url": EXPECTED_REPOSITORY_URL,
            "git_url": f"{EXPECTED_REPOSITORY_URL}.git",
            "default_branch": "main",
            "commit": EXPECTED_REPOSITORY_COMMIT,
            "snapshot_date": "2026-06-08",
            "live_update_policy": "live_repository_snapshot_required",
            "readme_url": f"{EXPECTED_REPOSITORY_URL}/blob/main/README.md",
            "readme_raw_url": readme_raw_url,
            "readme_sha256": EXPECTED_README_SHA256,
            "readme_bytes": EXPECTED_README_BYTES,
        },
        "repository_claims": {
            "declared_problem_count": EXPECTED_DECLARED_PROBLEM_COUNT,
            "problem_pages_declared_complete": True,
            "per_problem_inventory_validated": False,
            "numbered_page_inventory_validated": True,
            "notebook_coverage": "many_not_all",
            "runtime_code_available": False,
            "notebook_artifact_kinds": list(EXPECTED_ARTIFACT_KINDS),
            "hosted_problem_page_url_pattern": (
                "https://google-deepmind.github.io/"
                "alphaevolve_repository_of_problems/problems/{n}.html"
            ),
            "status_artifact_inventory_validated": True,
        },
        "problem_coverage_evidence": {
            "schema": EXPECTED_FOLLOW_ON_PROBLEM_COVERAGE_SCHEMA,
            "source_boundary": "alphaevolve_follow_on_problem_coverage",
            "declared_problem_count": EXPECTED_DECLARED_PROBLEM_COUNT,
            "observed_numbered_html_count": 68,
            "extra_numbered_page_ids": [68],
            "numbered_page_inventory_validated": True,
            "page_68_classification_complete": True,
            "resource_link_diagnostics_complete_for_pages_67_68": True,
            "all_page_resource_link_diagnostics_complete": True,
            "source_inventory_rows_emitted": True,
            "source_inventory_row_count": 68,
            "notebook_mapping_complete": True,
            "notebook_absence_reason_inventory_complete": True,
            "per_problem_inventory_validated": False,
            "page_hash_inventory_complete": True,
            "claim_boundary": (
                "The follow-on coverage record reconciles the declared "
                "67-problem count against 68 observed numbered HTML pages, "
                "classifies page 68, records all-page resource-link "
                "diagnostics, pins raw-page hashes, and emits per-page "
                "source rows with status buckets, notebook-link mappings, "
                "absence reasons, and pinned notebook SHA-256 hashes, but "
                "does not claim artifact flags."
            ),
        },
        "source_use": {
            "repository_software_license": "Apache-2.0",
            "repository_materials_license": "CC-BY-4.0",
            "rights_holder": "Google LLC",
            "copyright_year": 2025,
            "citation_required": True,
            "citation_arxiv_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
        },
        "required_follow_on_work": [
            "complete_per_problem_notebook_artifact_flag_inventory",
            "validate_notebook_prompt_verifier_initial_final_artifacts",
            "map_original_appendix_b_claims_to_follow_on_problem_records",
            "attach_rights_attribution_to_generated_artifacts",
        ],
    }


def alphaevolve_follow_on_repository_rights_record() -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_FOLLOW_ON_REPOSITORY_RIGHTS_SCHEMA,
        "source_family": "alphaevolve_follow_on_problem_repository_rights",
        "source_paper_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
        "source_manifest": EXPECTED_FOLLOW_ON_SOURCE_MANIFEST_FILE,
        "repository": {
            "name": EXPECTED_REPOSITORY_NAME,
            "url": EXPECTED_REPOSITORY_URL,
            "commit": EXPECTED_REPOSITORY_COMMIT,
            "snapshot_date": "2026-06-08",
            "readme_raw_url": (
                "https://raw.githubusercontent.com/google-deepmind/"
                f"alphaevolve_repository_of_problems/{EXPECTED_REPOSITORY_COMMIT}/README.md"
            ),
            "license_file": "LICENSE",
            "license_url": f"{EXPECTED_REPOSITORY_URL}/blob/{EXPECTED_REPOSITORY_COMMIT}/LICENSE",
        },
        "citation": {
            "required": True,
            "bibtex_key": "alphaevolve",
            "title": EXPECTED_FOLLOW_ON_TITLE,
            "authors": [
                "Georgiev, Bogdan",
                "Gomez-Serrano, Javier",
                "Tao, Terence",
                "Wagner, Adam Zsolt",
            ],
            "year": 2025,
            "journal": f"arXiv preprint arXiv:{EXPECTED_FOLLOW_ON_ARXIV_ID}",
            "arxiv_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
        },
        "rights": {
            "rights_holder": "Google LLC",
            "copyright_year": 2025,
            "software_license": "Apache-2.0",
            "software_license_url": "https://www.apache.org/licenses/LICENSE-2.0",
            "materials_license": "CC-BY-4.0",
            "materials_license_url": "https://creativecommons.org/licenses/by/4.0/legalcode",
            "artifact_license_mapping": dict(EXPECTED_FOLLOW_ON_REPOSITORY_LICENSE_MAPPING),
        },
        "disclaimers": {
            "as_is": True,
            "official_google_product": False,
            "as_is_source_phrase": 'distributed on an "AS IS" BASIS',
            "non_official_product_source_phrase": "This is not an official Google product.",
        },
        "role_attribution": {
            "contributors": [
                {
                    "name": "Javier Gomez-Serrano",
                    "affiliation": "Brown University",
                    "roles": ["supervision", "problem_selection", "review", "analysis", "commentary"],
                },
                {
                    "name": "Terence Tao",
                    "affiliation": "University of California, Los Angeles",
                    "roles": ["supervision", "problem_selection", "review", "analysis", "commentary"],
                },
            ],
            "source_phrase": (
                "provided supervision, problem selection, review, analysis and commentary"
            ),
        },
        "third_party_origins": [
            {
                "problem_id": 65,
                "origin": "official IMO problems website",
                "url": "https://www.imo-official.org/problems.aspx",
                "source_phrase": "Problem 65 originates from https://www.imo-official.org/problems.aspx",
            }
        ],
        "boundary": {
            "distinct_from_original_alphaevolve_pdf_rights": True,
            "distinct_from_alphaevolve_results_companion_rights": True,
            "distinct_from_libreevolve_mit_license": True,
            "source_rights_holder_required_for_copied_material": True,
            "generated_artifacts_need_source_relationship": True,
            "local_project_endorsement": False,
        },
    }


def alphaevolve_follow_on_repository_rights_manifest_record() -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_FOLLOW_ON_REPOSITORY_RIGHTS_MANIFEST_SCHEMA,
        "repository_rights_count": 1,
        "sources": [
            {
                "manifest_row_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
                "follow_on_source_manifest": EXPECTED_FOLLOW_ON_SOURCE_MANIFEST_FILE,
                "repository_rights_id": "alphaevolve_repository_of_problems_rights",
                "repository_rights_record": alphaevolve_follow_on_repository_rights_record(),
                "claim_artifact_links": {
                    "repository_rights_used_by": sorted(
                        EXPECTED_FOLLOW_ON_REPOSITORY_RIGHTS_SURFACES
                    ),
                    "policy": (
                        "follow_on_problem_repository_rights_must_remain_separate_"
                        "from_original_pdf_companion_repository_and_libreevolve_license"
                    ),
                },
                "reuse_policy": {
                    "copied_repository_material_requires_source_attribution": True,
                    "generated_local_artifacts_require_source_relationship": True,
                    "publication_ready_without_rights_review": False,
                    "scope": (
                        "follow-on problem repository source-use terms, not original "
                        "AlphaEvolve PDF rights or LibreEvolve project licensing"
                    ),
                },
            }
        ],
    }


def alphaevolve_follow_on_runtime_absence_record() -> dict[str, Any]:
    readme_raw_url = (
        "https://raw.githubusercontent.com/google-deepmind/"
        f"alphaevolve_repository_of_problems/{EXPECTED_REPOSITORY_COMMIT}/README.md"
    )
    return {
        "schema": ALPHAEVOLVE_FOLLOW_ON_RUNTIME_ABSENCE_SCHEMA,
        "source_family": "alphaevolve_follow_on_problem_repository_runtime_absence",
        "source_paper_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
        "source_manifest": EXPECTED_FOLLOW_ON_SOURCE_MANIFEST_FILE,
        "repository": {
            "name": EXPECTED_REPOSITORY_NAME,
            "url": EXPECTED_REPOSITORY_URL,
            "commit": EXPECTED_REPOSITORY_COMMIT,
            "snapshot_date": "2026-06-08",
            "readme_raw_url": readme_raw_url,
            "tree_api_url": (
                "https://api.github.com/repos/google-deepmind/"
                "alphaevolve_repository_of_problems/git/trees/"
                f"{EXPECTED_REPOSITORY_COMMIT}?recursive=1"
            ),
        },
        "notebook_inventory": {
            "notebook_count": len(EXPECTED_FOLLOW_ON_NOTEBOOKS),
            "coverage": "many_not_all_problem_notebooks",
            "hash_algorithm": "git_blob_sha1_and_raw_sha256",
            "sha256_inventory_complete": True,
            "problem_id_mapping_complete": True,
            "absence_reason_inventory_complete": True,
            "notebooks": [
                {
                    "path": path,
                    "bytes": byte_count,
                    "git_blob_sha": git_blob_sha,
                    "sha256": EXPECTED_FOLLOW_ON_NOTEBOOK_SHA256S[path],
                    "artifact_kinds": list(EXPECTED_FOLLOW_ON_NOTEBOOK_ARTIFACT_KINDS),
                    "alphaevolve_runtime_available": False,
                }
                for path, byte_count, git_blob_sha in EXPECTED_FOLLOW_ON_NOTEBOOKS
            ],
        },
        "runtime_boundary": {
            "alphaevolve_runtime_available": False,
            "verifier_code_available": True,
            "verifier_is_not_runtime": True,
            "notebook_artifacts_are_experiment_inputs_and_outputs": True,
            "no_installation_required": True,
            "colab_browser_access_only": True,
            "absence_source_phrase": "This repository does *not* contain the code to run AlphaEvolve.",
            "artifact_source_phrase": (
                "Each notebook contains the prompt, verification code, and initial program "
                "used to launch the AlphaEvolve experiments, along with the final evolved "
                "programs and visualization / analysis code where appropriate."
            ),
        },
        "boundary": {
            "not_alphaevolve_runtime_implementation": True,
            "not_replayable_alphaevolve_service": True,
            "not_full_notebook_cell_inventory": True,
            "not_cell_artifact_flag_inventory": True,
            "must_not_describe_notebooks_as_runtime_harnesses": True,
        },
        "remaining_runtime_work": [
            "validate_notebook_cell_artifact_flags",
        ],
    }


def alphaevolve_follow_on_runtime_absence_manifest_record() -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_FOLLOW_ON_RUNTIME_ABSENCE_MANIFEST_SCHEMA,
        "runtime_absence_count": 1,
        "sources": [
            {
                "manifest_row_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
                "follow_on_source_manifest": EXPECTED_FOLLOW_ON_SOURCE_MANIFEST_FILE,
                "runtime_absence_id": "alphaevolve_repository_of_problems_runtime_absence",
                "runtime_absence_record": alphaevolve_follow_on_runtime_absence_record(),
                "claim_artifact_links": {
                    "runtime_absence_used_by": sorted(EXPECTED_FOLLOW_ON_RUNTIME_SURFACES),
                    "policy": (
                        "follow_on_problem_repository_notebooks_must_not_be_treated_"
                        "as_alphaevolve_runtime"
                    ),
                },
                "runtime_claim_policy": {
                    "prompt_verifier_outputs_are_source_artifacts": True,
                    "alphaevolve_runtime_available": False,
                    "publication_ready_runtime_claim": False,
                    "scope": (
                        "follow-on problem repository runtime absence, not full notebook "
                        "inventory"
                    ),
                },
            }
        ],
    }


def alphaevolve_follow_on_tao_blog_record() -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_FOLLOW_ON_TAO_BLOG_SCHEMA,
        "source_family": "alphaevolve_follow_on_tao_blog_commentary",
        "source_paper_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
        "source_manifest": EXPECTED_FOLLOW_ON_SOURCE_MANIFEST_FILE,
        "canonical_url": EXPECTED_TAO_BLOG_URL,
        "api_url": EXPECTED_TAO_BLOG_API_URL,
        "post": {
            "post_id": EXPECTED_TAO_BLOG_POST_ID,
            "title": EXPECTED_TAO_BLOG_TITLE,
            "author": EXPECTED_TAO_BLOG_AUTHOR,
            "post_date": EXPECTED_TAO_BLOG_POST_DATE,
            "modified_date": EXPECTED_TAO_BLOG_MODIFIED_DATE,
            "site_title": "What's new",
        },
        "retrieval": {
            "retrieved_on": "2026-06-09",
            "api_bytes": EXPECTED_TAO_BLOG_API_BYTES,
            "api_sha256": EXPECTED_TAO_BLOG_API_SHA256,
            "html_bytes": EXPECTED_TAO_BLOG_HTML_BYTES,
            "html_sha256": EXPECTED_TAO_BLOG_HTML_SHA256,
            "hash_algorithm": "sha256",
            "api_surface_preferred": True,
            "html_surface_expected_volatile": True,
        },
        "linked_sources": {
            "follow_on_arxiv_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
            "follow_on_arxiv_url": f"https://arxiv.org/abs/{EXPECTED_FOLLOW_ON_ARXIV_ID}",
            "problem_repository_url": EXPECTED_REPOSITORY_URL,
            "problem_repository_commit": EXPECTED_REPOSITORY_COMMIT,
            "alphaevolve_tool_url": (
                "https://deepmind.google/discover/blog/"
                "alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/"
            ),
            "original_whitepaper_url": (
                "https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/"
                "alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/"
                "AlphaEvolve.pdf"
            ),
        },
        "claim_spans": [
            {
                "category": "commentary",
                "source_lines": "20-26",
                "summary": (
                    "Frames the post as Tao's longer-report commentary on AlphaEvolve "
                    "experiments and describes LLM-guided code mutation."
                ),
                "requires_backing_artifact": False,
            },
            {
                "category": "experiment_summary",
                "source_lines": "27-31",
                "summary": (
                    "Summarizes 67 mathematics problems and positive/negative outcomes "
                    "with scale and adaptability observations."
                ),
                "requires_backing_artifact": True,
            },
            {
                "category": "verifier_design_lesson",
                "source_lines": "43-46",
                "summary": (
                    "Describes verifier exploits and the need for exact or interval "
                    "arithmetic with conservative bounds."
                ),
                "requires_backing_artifact": True,
            },
            {
                "category": "negative_result",
                "source_lines": "48-51",
                "summary": (
                    "Describes one-sided open-conjecture limits and the value of "
                    "systematically recording negative search results."
                ),
                "requires_backing_artifact": True,
            },
            {
                "category": "proof_handoff",
                "source_lines": "42, 52-82",
                "summary": (
                    "Separates discovered constructions from later human proof work, "
                    "Deep Think, AlphaProof, or later-paper handoffs."
                ),
                "requires_backing_artifact": True,
            },
            {
                "category": "future_work",
                "source_lines": "50-51, 712-713",
                "summary": (
                    "Presents future-use and variationalization ideas as commentary, "
                    "not implemented LibreEvolve capability."
                ),
                "requires_backing_artifact": True,
            },
        ],
        "claim_boundary": {
            "blog_commentary_secondary": True,
            "blog_only_claims_require_paper_repository_or_proof_artifact": True,
            "not_original_alphaevolve_spec": True,
            "not_runtime_implementation_evidence": True,
            "not_repository_snapshot": True,
            "not_proof_artifact": True,
            "not_independent_verification": True,
        },
        "remaining_work": [
            "map_blog_claims_to_paper_sections",
            "map_blog_claims_to_repository_problem_ids",
            "attach_proof_artifacts_for_handoff_claims",
            "separate_comment_thread_claims_from_post_claims",
        ],
    }


def alphaevolve_follow_on_tao_blog_manifest_record() -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_FOLLOW_ON_TAO_BLOG_MANIFEST_SCHEMA,
        "tao_blog_source_count": 1,
        "sources": [
            {
                "manifest_row_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
                "follow_on_source_manifest": EXPECTED_FOLLOW_ON_SOURCE_MANIFEST_FILE,
                "tao_blog_source_id": "terence_tao_2025_11_05_mathematical_exploration",
                "source_record": alphaevolve_follow_on_tao_blog_record(),
                "claim_artifact_links": {
                    "tao_blog_used_by": sorted(EXPECTED_TAO_BLOG_SURFACES),
                    "policy": (
                        "tao_blog_claims_are_secondary_until_backed_by_"
                        "paper_repository_notebook_verifier_or_proof_artifacts"
                    ),
                },
                "evidence_policy": {
                    "commentary_secondary": True,
                    "publication_ready_without_backing_artifacts": False,
                    "comment_thread_included": False,
                    "scope": (
                        "Terence Tao follow-on blog source metadata and claim "
                        "boundaries, not original AlphaEvolve specification"
                    ),
                },
            }
        ],
    }


def alphaevolve_follow_on_source_manifest_record() -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_FOLLOW_ON_SOURCE_MANIFEST_SCHEMA,
        "follow_on_source_count": 1,
        "sources": [
            {
                "manifest_row_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
                "follow_on_source_id": EXPECTED_FOLLOW_ON_VERSIONED_ID,
                "source_record": alphaevolve_follow_on_math_source_record(),
                "claim_artifact_links": {
                    "follow_on_source_used_by": [
                        "README.md",
                        "ROADMAP.md",
                        "papers/README.md",
                        "docs/todo/code.md",
                        "docs/todo/papers.md",
                        "docs/todo/readme.md",
                        "docs/todo/roadmap.md",
                    ],
                    "policy": (
                        "follow_on_sources_must_not_be_treated_as_original_"
                        "alphaevolve_spec_or_cached_pdf"
                    ),
                },
                "cache_policy": {
                    "paper_cache_manifest_row_required": False,
                    "explicit_no_cache_policy_recorded": True,
                    "repository_snapshot_required": True,
                    "local_cache_status_field": "source_record.paper.local_cache",
                    "scope": (
                        "committed follow-on source provenance, not cached PDF "
                        "or per-problem inventory"
                    ),
                },
                "remaining_work": [
                    "complete_per_problem_notebook_artifact_flag_inventory",
                    "validate_notebook_prompt_verifier_initial_final_artifacts",
                    "map_original_appendix_b_claims_to_follow_on_problem_records",
                    "attach_rights_attribution_to_generated_artifacts",
                ],
            }
        ],
    }


def validate_alphaevolve_follow_on_math_source(
    recordset: object | str | Path | None = None,
) -> AlphaEvolveFollowOnMathSourceValidation:
    data, read_issues = _load_recordset(recordset)
    if read_issues:
        return AlphaEvolveFollowOnMathSourceValidation(False, 0, False, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveFollowOnMathSourceIssue] = []
    if data.get("schema") != ALPHAEVOLVE_FOLLOW_ON_MATH_SOURCE_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported AlphaEvolve follow-on math source schema"))
    if data.get("source_family") != "alphaevolve_follow_on_mathematics":
        issues.append(_issue("invalid_source_family", "source_family must identify follow-on AlphaEvolve mathematics evidence"))
    if data.get("original_source_paper_id") != EXPECTED_ORIGINAL_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_original_source_paper_id", "original_source_paper_id must be 2506.13131"))
    _validate_scope_boundary(data.get("scope_boundary"), issues)
    local_pdf_cache_available = _validate_paper(data.get("paper"), issues)
    repository_ref_pinned = _validate_repository(data.get("repository"), issues)
    _validate_repository_claims(data.get("repository_claims"), issues)
    _validate_problem_coverage_evidence(data.get("problem_coverage_evidence"), issues)
    _validate_source_use(data.get("source_use"), issues)
    _validate_required_follow_on_work(data.get("required_follow_on_work"), issues)
    source_count = sum(
        1
        for key in ("paper", "repository")
        if isinstance(data.get(key), dict)
    )
    return AlphaEvolveFollowOnMathSourceValidation(
        ok=not issues,
        source_count=source_count,
        repository_ref_pinned=repository_ref_pinned,
        local_pdf_cache_available=local_pdf_cache_available,
        issues=issues,
    )


def validate_alphaevolve_follow_on_source_manifest(
    recordset: object | str | Path | None = None,
) -> AlphaEvolveFollowOnMathSourceValidation:
    data, read_issues = _load_manifest_recordset(recordset)
    if read_issues:
        return AlphaEvolveFollowOnMathSourceValidation(False, 0, False, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveFollowOnMathSourceIssue] = []
    if data.get("schema") != ALPHAEVOLVE_FOLLOW_ON_SOURCE_MANIFEST_SCHEMA:
        issues.append(_issue("invalid_manifest_schema", "unsupported AlphaEvolve follow-on source manifest schema"))
    sources = data.get("sources")
    if not isinstance(sources, list):
        issues.append(_issue("invalid_manifest_sources", "follow-on source manifest sources must be a list"))
        sources = []
    source_count = len(sources)
    if data.get("follow_on_source_count") != source_count:
        issues.append(
            _issue(
                "invalid_manifest_follow_on_source_count",
                "follow_on_source_count must equal the number of follow-on source records",
            )
        )
    if source_count != 1:
        issues.append(_issue("invalid_manifest_source_count", "follow-on source manifest must contain the math-scale paper/repository row"))
    repository_ref_pinned = False
    local_pdf_cache_available = False
    for index, source in enumerate(sources):
        source_report = _validate_follow_on_source_manifest_source(source, issues, index)
        repository_ref_pinned = repository_ref_pinned or source_report.repository_ref_pinned
        local_pdf_cache_available = local_pdf_cache_available or source_report.local_pdf_cache_available
    return AlphaEvolveFollowOnMathSourceValidation(
        ok=not issues,
        source_count=source_count,
        repository_ref_pinned=repository_ref_pinned,
        local_pdf_cache_available=local_pdf_cache_available,
        issues=issues,
    )


def validate_alphaevolve_follow_on_repository_rights(
    recordset: object | str | Path | None = None,
) -> AlphaEvolveFollowOnRepositoryRightsValidation:
    data, read_issues = _load_repository_rights_recordset(recordset)
    if read_issues:
        return AlphaEvolveFollowOnRepositoryRightsValidation(False, 0, False, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveFollowOnMathSourceIssue] = []
    if data.get("schema") != ALPHAEVOLVE_FOLLOW_ON_REPOSITORY_RIGHTS_SCHEMA:
        issues.append(_issue("invalid_repository_rights_schema", "unsupported follow-on repository rights schema"))
    if data.get("source_family") != "alphaevolve_follow_on_problem_repository_rights":
        issues.append(_issue("invalid_repository_rights_source_family", "source_family must identify follow-on repository rights"))
    if data.get("source_paper_id") != EXPECTED_FOLLOW_ON_ARXIV_ID:
        issues.append(_issue("invalid_repository_rights_source_paper_id", "source_paper_id must be 2511.02864"))
    if data.get("source_manifest") != EXPECTED_FOLLOW_ON_SOURCE_MANIFEST_FILE:
        issues.append(_issue("invalid_repository_rights_source_manifest", "source_manifest must point to papers/follow_on_sources.json"))
    _validate_repository_rights_repository(data.get("repository"), issues)
    citation_required = _validate_repository_rights_citation(data.get("citation"), issues)
    mapping_count = _validate_repository_rights_rights(data.get("rights"), issues)
    _validate_repository_rights_disclaimers(data.get("disclaimers"), issues)
    _validate_repository_rights_role_attribution(data.get("role_attribution"), issues)
    _validate_repository_rights_third_party_origins(data.get("third_party_origins"), issues)
    _validate_repository_rights_boundary(data.get("boundary"), issues)
    return AlphaEvolveFollowOnRepositoryRightsValidation(
        ok=not issues,
        rights_count=1 if isinstance(data.get("rights"), dict) else 0,
        citation_required=citation_required,
        artifact_license_mapping_count=mapping_count,
        issues=issues,
    )


def validate_alphaevolve_follow_on_repository_rights_manifest(
    recordset: object | str | Path | None = None,
) -> AlphaEvolveFollowOnRepositoryRightsValidation:
    data, read_issues = _load_repository_rights_manifest_recordset(recordset)
    if read_issues:
        return AlphaEvolveFollowOnRepositoryRightsValidation(False, 0, False, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveFollowOnMathSourceIssue] = []
    if data.get("schema") != ALPHAEVOLVE_FOLLOW_ON_REPOSITORY_RIGHTS_MANIFEST_SCHEMA:
        issues.append(_issue("invalid_repository_rights_manifest_schema", "unsupported follow-on repository rights manifest schema"))
    sources = data.get("sources")
    if not isinstance(sources, list):
        issues.append(_issue("invalid_repository_rights_manifest_sources", "repository-rights manifest sources must be a list"))
        sources = []
    rights_count = len(sources)
    if data.get("repository_rights_count") != rights_count:
        issues.append(_issue("invalid_repository_rights_count", "repository_rights_count must equal the number of rights records"))
    if rights_count != 1:
        issues.append(_issue("invalid_repository_rights_source_count", "repository-rights manifest must contain the problem repository row"))
    citation_required = False
    mapping_count = 0
    for index, source in enumerate(sources):
        report = _validate_repository_rights_manifest_source(source, issues, index)
        citation_required = citation_required or report.citation_required
        mapping_count += report.artifact_license_mapping_count
    return AlphaEvolveFollowOnRepositoryRightsValidation(
        ok=not issues,
        rights_count=rights_count,
        citation_required=citation_required,
        artifact_license_mapping_count=mapping_count,
        issues=issues,
    )


def validate_alphaevolve_follow_on_runtime_absence(
    recordset: object | str | Path | None = None,
) -> AlphaEvolveFollowOnRuntimeAbsenceValidation:
    data, read_issues = _load_runtime_absence_recordset(recordset)
    if read_issues:
        return AlphaEvolveFollowOnRuntimeAbsenceValidation(False, 0, 0, False, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveFollowOnMathSourceIssue] = []
    if data.get("schema") != ALPHAEVOLVE_FOLLOW_ON_RUNTIME_ABSENCE_SCHEMA:
        issues.append(_issue("invalid_runtime_absence_schema", "unsupported follow-on runtime-absence schema"))
    if data.get("source_family") != "alphaevolve_follow_on_problem_repository_runtime_absence":
        issues.append(_issue("invalid_runtime_absence_source_family", "source_family must identify follow-on runtime absence"))
    if data.get("source_paper_id") != EXPECTED_FOLLOW_ON_ARXIV_ID:
        issues.append(_issue("invalid_runtime_absence_source_paper_id", "source_paper_id must be 2511.02864"))
    if data.get("source_manifest") != EXPECTED_FOLLOW_ON_SOURCE_MANIFEST_FILE:
        issues.append(_issue("invalid_runtime_absence_source_manifest", "source_manifest must point to papers/follow_on_sources.json"))
    _validate_runtime_absence_repository(data.get("repository"), issues)
    notebook_count = _validate_runtime_absence_notebook_inventory(data.get("notebook_inventory"), issues)
    alphaevolve_runtime_available, verifier_code_available = _validate_runtime_absence_boundary(
        data.get("runtime_boundary"), issues
    )
    _validate_runtime_absence_limits(data.get("boundary"), issues)
    _validate_remaining_runtime_work(data.get("remaining_runtime_work"), issues)
    return AlphaEvolveFollowOnRuntimeAbsenceValidation(
        ok=not issues,
        runtime_absence_count=1 if isinstance(data.get("runtime_boundary"), dict) else 0,
        notebook_count=notebook_count,
        alphaevolve_runtime_available=alphaevolve_runtime_available,
        verifier_code_available=verifier_code_available,
        issues=issues,
    )


def validate_alphaevolve_follow_on_runtime_absence_manifest(
    recordset: object | str | Path | None = None,
) -> AlphaEvolveFollowOnRuntimeAbsenceValidation:
    data, read_issues = _load_runtime_absence_manifest_recordset(recordset)
    if read_issues:
        return AlphaEvolveFollowOnRuntimeAbsenceValidation(False, 0, 0, False, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveFollowOnMathSourceIssue] = []
    if data.get("schema") != ALPHAEVOLVE_FOLLOW_ON_RUNTIME_ABSENCE_MANIFEST_SCHEMA:
        issues.append(_issue("invalid_runtime_absence_manifest_schema", "unsupported follow-on runtime-absence manifest schema"))
    sources = data.get("sources")
    if not isinstance(sources, list):
        issues.append(_issue("invalid_runtime_absence_manifest_sources", "runtime-absence manifest sources must be a list"))
        sources = []
    runtime_absence_count = len(sources)
    if data.get("runtime_absence_count") != runtime_absence_count:
        issues.append(_issue("invalid_runtime_absence_count", "runtime_absence_count must equal the number of runtime-absence records"))
    if runtime_absence_count != 1:
        issues.append(_issue("invalid_runtime_absence_source_count", "runtime-absence manifest must contain the problem repository row"))
    notebook_count = 0
    alphaevolve_runtime_available = False
    verifier_code_available = False
    for index, source in enumerate(sources):
        report = _validate_runtime_absence_manifest_source(source, issues, index)
        notebook_count += report.notebook_count
        alphaevolve_runtime_available = (
            alphaevolve_runtime_available or report.alphaevolve_runtime_available
        )
        verifier_code_available = verifier_code_available or report.verifier_code_available
    return AlphaEvolveFollowOnRuntimeAbsenceValidation(
        ok=not issues,
        runtime_absence_count=runtime_absence_count,
        notebook_count=notebook_count,
        alphaevolve_runtime_available=alphaevolve_runtime_available,
        verifier_code_available=verifier_code_available,
        issues=issues,
    )


def validate_alphaevolve_follow_on_tao_blog(
    recordset: object | str | Path | None = None,
) -> AlphaEvolveFollowOnTaoBlogValidation:
    data, read_issues = _load_tao_blog_recordset(recordset)
    if read_issues:
        return AlphaEvolveFollowOnTaoBlogValidation(False, 0, 0, False, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveFollowOnMathSourceIssue] = []
    if data.get("schema") != ALPHAEVOLVE_FOLLOW_ON_TAO_BLOG_SCHEMA:
        issues.append(_issue("invalid_tao_blog_schema", "unsupported follow-on Tao blog schema"))
    if data.get("source_family") != "alphaevolve_follow_on_tao_blog_commentary":
        issues.append(_issue("invalid_tao_blog_source_family", "source_family must identify Tao follow-on blog commentary"))
    if data.get("source_paper_id") != EXPECTED_FOLLOW_ON_ARXIV_ID:
        issues.append(_issue("invalid_tao_blog_source_paper_id", "source_paper_id must be 2511.02864"))
    if data.get("source_manifest") != EXPECTED_FOLLOW_ON_SOURCE_MANIFEST_FILE:
        issues.append(_issue("invalid_tao_blog_source_manifest", "source_manifest must point to papers/follow_on_sources.json"))
    if data.get("canonical_url") != EXPECTED_TAO_BLOG_URL:
        issues.append(_issue("invalid_tao_blog_canonical_url", "canonical_url must match Tao's blog post URL"))
    if data.get("api_url") != EXPECTED_TAO_BLOG_API_URL:
        issues.append(_issue("invalid_tao_blog_api_url", "api_url must match the pinned WordPress post API URL"))
    _validate_tao_blog_post(data.get("post"), issues)
    _validate_tao_blog_retrieval(data.get("retrieval"), issues)
    linked_repository_pinned = _validate_tao_blog_linked_sources(data.get("linked_sources"), issues)
    claim_category_count = _validate_tao_blog_claim_spans(data.get("claim_spans"), issues)
    commentary_secondary = _validate_tao_blog_claim_boundary(data.get("claim_boundary"), issues)
    _validate_tao_blog_remaining_work(data.get("remaining_work"), issues)
    return AlphaEvolveFollowOnTaoBlogValidation(
        ok=not issues,
        source_count=1,
        claim_category_count=claim_category_count,
        linked_repository_pinned=linked_repository_pinned,
        commentary_secondary=commentary_secondary,
        issues=issues,
    )


def validate_alphaevolve_follow_on_tao_blog_manifest(
    recordset: object | str | Path | None = None,
) -> AlphaEvolveFollowOnTaoBlogValidation:
    data, read_issues = _load_tao_blog_manifest_recordset(recordset)
    if read_issues:
        return AlphaEvolveFollowOnTaoBlogValidation(False, 0, 0, False, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveFollowOnMathSourceIssue] = []
    if data.get("schema") != ALPHAEVOLVE_FOLLOW_ON_TAO_BLOG_MANIFEST_SCHEMA:
        issues.append(_issue("invalid_tao_blog_manifest_schema", "unsupported follow-on Tao blog manifest schema"))
    sources = data.get("sources")
    if not isinstance(sources, list):
        issues.append(_issue("invalid_tao_blog_manifest_sources", "Tao blog manifest sources must be a list"))
        sources = []
    source_count = len(sources)
    if data.get("tao_blog_source_count") != source_count:
        issues.append(_issue("invalid_tao_blog_source_count", "tao_blog_source_count must equal the number of Tao blog source records"))
    if source_count != 1:
        issues.append(_issue("invalid_tao_blog_manifest_source_count", "Tao blog manifest must contain the follow-on blog source row"))
    claim_category_count = 0
    linked_repository_pinned = False
    commentary_secondary = False
    for index, source in enumerate(sources):
        report = _validate_tao_blog_manifest_source(source, issues, index)
        claim_category_count += report.claim_category_count
        linked_repository_pinned = linked_repository_pinned or report.linked_repository_pinned
        commentary_secondary = commentary_secondary or report.commentary_secondary
    return AlphaEvolveFollowOnTaoBlogValidation(
        ok=not issues,
        source_count=source_count,
        claim_category_count=claim_category_count,
        linked_repository_pinned=linked_repository_pinned,
        commentary_secondary=commentary_secondary,
        issues=issues,
    )


def render_alphaevolve_follow_on_math_source_summary(recordset: object | str | Path | None = None) -> str:
    validation = validate_alphaevolve_follow_on_math_source(recordset)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve follow-on math source evidence",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| source_count | {validation.source_count} |",
        f"| arxiv_version | v{EXPECTED_FOLLOW_ON_VERSION} |",
        f"| latest_revision_date | {EXPECTED_FOLLOW_ON_REVISION_DATE} |",
        f"| declared_problem_count | {EXPECTED_DECLARED_PROBLEM_COUNT} |",
        f"| repository_ref_pinned | {validation.repository_ref_pinned} |",
        f"| local_pdf_cache_available | {validation.local_pdf_cache_available} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(
            f"- {issue.code}: {issue.message}"
            + (f" ({issue.source_id})" if issue.source_id else "")
            for issue in validation.issues
        )
    return "\n".join(lines)


def _load_manifest_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveFollowOnMathSourceIssue]]:
    if recordset is None:
        return alphaevolve_follow_on_source_manifest_record(), []
    return _load_recordset(recordset)


def _load_repository_rights_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveFollowOnMathSourceIssue]]:
    if recordset is None:
        return alphaevolve_follow_on_repository_rights_record(), []
    return _load_recordset(recordset)


def _load_repository_rights_manifest_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveFollowOnMathSourceIssue]]:
    if recordset is None:
        return alphaevolve_follow_on_repository_rights_manifest_record(), []
    return _load_recordset(recordset)


def _load_runtime_absence_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveFollowOnMathSourceIssue]]:
    if recordset is None:
        return alphaevolve_follow_on_runtime_absence_record(), []
    return _load_recordset(recordset)


def _load_runtime_absence_manifest_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveFollowOnMathSourceIssue]]:
    if recordset is None:
        return alphaevolve_follow_on_runtime_absence_manifest_record(), []
    return _load_recordset(recordset)


def _load_tao_blog_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveFollowOnMathSourceIssue]]:
    if recordset is None:
        return alphaevolve_follow_on_tao_blog_record(), []
    return _load_recordset(recordset)


def _load_tao_blog_manifest_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveFollowOnMathSourceIssue]]:
    if recordset is None:
        return alphaevolve_follow_on_tao_blog_manifest_record(), []
    return _load_recordset(recordset)


def _load_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveFollowOnMathSourceIssue]]:
    if recordset is None:
        return alphaevolve_follow_on_math_source_record(), []
    if isinstance(recordset, dict):
        return dict(recordset), []
    if isinstance(recordset, (str, Path)):
        path = Path(recordset)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [_issue("read_error", f"failed to read follow-on source record: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"invalid follow-on source JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [_issue("invalid_shape", "follow-on source record must be a JSON object")]


def _validate_scope_boundary(value: object, issues: list[AlphaEvolveFollowOnMathSourceIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_scope_boundary", "scope_boundary must be an object"))
        return
    expected = {
        "original_alphaevolve_spec_source": EXPECTED_ORIGINAL_SOURCE_PAPER_ID,
        "follow_on_evidence_source": EXPECTED_FOLLOW_ON_ARXIV_ID,
        "separates_original_spec_from_later_math_evidence": True,
        "not_original_alphaevolve_runtime_spec": True,
        "not_full_problem_inventory": True,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_scope_boundary_{field}", f"scope_boundary.{field} must preserve the follow-on source boundary"))


def _validate_paper(value: object, issues: list[AlphaEvolveFollowOnMathSourceIssue]) -> bool:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_paper", "paper must be an object", EXPECTED_FOLLOW_ON_ARXIV_ID))
        return False
    expected = {
        "arxiv_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
        "version": EXPECTED_FOLLOW_ON_VERSION,
        "versioned_id": EXPECTED_FOLLOW_ON_VERSIONED_ID,
        "category": EXPECTED_FOLLOW_ON_CATEGORY,
        "latest_revision_date": EXPECTED_FOLLOW_ON_REVISION_DATE,
        "title": EXPECTED_FOLLOW_ON_TITLE,
        "abs_url": f"https://arxiv.org/abs/{EXPECTED_FOLLOW_ON_ARXIV_ID}",
        "versioned_abs_url": f"https://arxiv.org/abs/{EXPECTED_FOLLOW_ON_VERSIONED_ID}",
        "floating_pdf_url": f"https://arxiv.org/pdf/{EXPECTED_FOLLOW_ON_ARXIV_ID}.pdf",
        "versioned_pdf_url": f"https://arxiv.org/pdf/{EXPECTED_FOLLOW_ON_VERSIONED_ID}",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_paper_{field}", f"paper.{field} must match the verified follow-on arXiv source", EXPECTED_FOLLOW_ON_ARXIV_ID))
    if tuple(value.get("authors") or ()) != EXPECTED_FOLLOW_ON_AUTHORS:
        issues.append(_issue("invalid_paper_authors", "paper.authors must match the verified follow-on author list", EXPECTED_FOLLOW_ON_ARXIV_ID))
    return _validate_local_cache(value.get("local_cache"), issues)


def _validate_local_cache(value: object, issues: list[AlphaEvolveFollowOnMathSourceIssue]) -> bool:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_local_cache", "paper.local_cache must be an object", EXPECTED_FOLLOW_ON_ARXIV_ID))
        return False
    available = value.get("available")
    manifest_row_present = value.get("manifest_row_present")
    if available is not False:
        issues.append(_issue("local_pdf_cache_overclaim", "paper.local_cache.available must remain false until a cache row is validated", EXPECTED_FOLLOW_ON_ARXIV_ID))
    if manifest_row_present is not False:
        issues.append(_issue("manifest_row_overclaim", "paper.local_cache.manifest_row_present must remain false until a paper manifest row exists", EXPECTED_FOLLOW_ON_ARXIV_ID))
    for field in ("file", "sha256", "bytes"):
        if value.get(field) is not None:
            issues.append(_issue(f"local_cache_{field}_overclaim", f"paper.local_cache.{field} must be null while the follow-on PDF is not cached", EXPECTED_FOLLOW_ON_ARXIV_ID))
    return available is True


def _validate_repository(value: object, issues: list[AlphaEvolveFollowOnMathSourceIssue]) -> bool:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_repository", "repository must be an object", EXPECTED_REPOSITORY_NAME))
        return False
    expected = {
        "name": EXPECTED_REPOSITORY_NAME,
        "url": EXPECTED_REPOSITORY_URL,
        "git_url": f"{EXPECTED_REPOSITORY_URL}.git",
        "default_branch": "main",
        "snapshot_date": "2026-06-08",
        "live_update_policy": "live_repository_snapshot_required",
        "readme_url": f"{EXPECTED_REPOSITORY_URL}/blob/main/README.md",
        "readme_raw_url": (
            "https://raw.githubusercontent.com/google-deepmind/"
            f"alphaevolve_repository_of_problems/{EXPECTED_REPOSITORY_COMMIT}/README.md"
        ),
        "readme_bytes": EXPECTED_README_BYTES,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_repository_{field}", f"repository.{field} must match the pinned DeepMind problem repository snapshot", EXPECTED_REPOSITORY_NAME))
    commit = value.get("commit")
    if not isinstance(commit, str) or _COMMIT_RE.fullmatch(commit) is None:
        issues.append(_issue("invalid_repository_commit", "repository.commit must be a 40-character commit hash", EXPECTED_REPOSITORY_NAME))
    elif commit != EXPECTED_REPOSITORY_COMMIT:
        issues.append(_issue("repository_commit_drift", "repository.commit must match the verified follow-on source revision", EXPECTED_REPOSITORY_NAME))
    sha256 = value.get("readme_sha256")
    if not isinstance(sha256, str) or _SHA256_RE.fullmatch(sha256) is None:
        issues.append(_issue("invalid_readme_sha256", "repository.readme_sha256 must be a lowercase 64-hex digest", EXPECTED_REPOSITORY_NAME))
    elif sha256 != EXPECTED_README_SHA256:
        issues.append(_issue("readme_sha256_drift", "repository.readme_sha256 must match the pinned README digest", EXPECTED_REPOSITORY_NAME))
    return commit == EXPECTED_REPOSITORY_COMMIT and sha256 == EXPECTED_README_SHA256


def _validate_repository_claims(value: object, issues: list[AlphaEvolveFollowOnMathSourceIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_repository_claims", "repository_claims must be an object", EXPECTED_REPOSITORY_NAME))
        return
    expected = {
        "declared_problem_count": EXPECTED_DECLARED_PROBLEM_COUNT,
        "problem_pages_declared_complete": True,
        "per_problem_inventory_validated": False,
        "numbered_page_inventory_validated": True,
        "notebook_coverage": "many_not_all",
        "runtime_code_available": False,
        "hosted_problem_page_url_pattern": (
            "https://google-deepmind.github.io/"
            "alphaevolve_repository_of_problems/problems/{n}.html"
        ),
        "status_artifact_inventory_validated": True,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            code = f"invalid_repository_claims_{field}"
            if field == "runtime_code_available":
                code = "runtime_code_overclaim"
            elif field == "per_problem_inventory_validated":
                code = f"{field}_overclaim"
            issues.append(_issue(code, f"repository_claims.{field} must match the scoped follow-on source evidence", EXPECTED_REPOSITORY_NAME))
    if tuple(value.get("notebook_artifact_kinds") or ()) != EXPECTED_ARTIFACT_KINDS:
        issues.append(_issue("invalid_notebook_artifact_kinds", "repository_claims.notebook_artifact_kinds must preserve the README artifact kinds", EXPECTED_REPOSITORY_NAME))


def _validate_problem_coverage_evidence(value: object, issues: list[AlphaEvolveFollowOnMathSourceIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_problem_coverage_evidence", "problem_coverage_evidence must be an object", EXPECTED_REPOSITORY_NAME))
        return
    expected = {
        "schema": EXPECTED_FOLLOW_ON_PROBLEM_COVERAGE_SCHEMA,
        "source_boundary": "alphaevolve_follow_on_problem_coverage",
        "declared_problem_count": EXPECTED_DECLARED_PROBLEM_COUNT,
        "observed_numbered_html_count": 68,
        "extra_numbered_page_ids": [68],
        "numbered_page_inventory_validated": True,
        "page_68_classification_complete": True,
        "resource_link_diagnostics_complete_for_pages_67_68": True,
        "all_page_resource_link_diagnostics_complete": True,
        "source_inventory_rows_emitted": True,
        "source_inventory_row_count": 68,
        "notebook_mapping_complete": True,
        "notebook_absence_reason_inventory_complete": True,
        "per_problem_inventory_validated": False,
        "page_hash_inventory_complete": True,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            code = f"invalid_problem_coverage_evidence_{field}"
            if field == "per_problem_inventory_validated":
                code = f"problem_coverage_evidence_{field}_overclaim"
            issues.append(_issue(code, f"problem_coverage_evidence.{field} must link only the validated numbered-page boundary", EXPECTED_REPOSITORY_NAME))
    claim_boundary = value.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "does not claim" not in claim_boundary
        or "artifact flags" not in claim_boundary
    ):
        issues.append(_issue("missing_problem_coverage_claim_boundary", "problem_coverage_evidence must preserve artifact gaps", EXPECTED_REPOSITORY_NAME))


def _validate_source_use(value: object, issues: list[AlphaEvolveFollowOnMathSourceIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_source_use", "source_use must be an object", EXPECTED_REPOSITORY_NAME))
        return
    expected = {
        "repository_software_license": "Apache-2.0",
        "repository_materials_license": "CC-BY-4.0",
        "rights_holder": "Google LLC",
        "copyright_year": 2025,
        "citation_required": True,
        "citation_arxiv_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_source_use_{field}", f"source_use.{field} must match the follow-on repository README source-use boundary", EXPECTED_REPOSITORY_NAME))


def _validate_required_follow_on_work(value: object, issues: list[AlphaEvolveFollowOnMathSourceIssue]) -> None:
    required = {
        "complete_per_problem_notebook_artifact_flag_inventory",
        "validate_notebook_prompt_verifier_initial_final_artifacts",
        "map_original_appendix_b_claims_to_follow_on_problem_records",
        "attach_rights_attribution_to_generated_artifacts",
    }
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(_issue("invalid_required_follow_on_work", "required_follow_on_work must be a list of remaining work ids"))
        return
    missing = sorted(required - set(value))
    for work_id in missing:
        issues.append(_issue("missing_required_follow_on_work", f"required_follow_on_work is missing {work_id}"))


def _validate_follow_on_source_manifest_source(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
    index: int,
) -> AlphaEvolveFollowOnMathSourceValidation:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_manifest_source", f"follow-on source manifest source {index} must be an object"))
        return AlphaEvolveFollowOnMathSourceValidation(False, 0, False, False, [])
    if value.get("manifest_row_id") != EXPECTED_FOLLOW_ON_ARXIV_ID:
        issues.append(_issue("invalid_manifest_source_row_id", "manifest row id must match the follow-on arXiv id"))
    if value.get("follow_on_source_id") != EXPECTED_FOLLOW_ON_VERSIONED_ID:
        issues.append(_issue("invalid_manifest_follow_on_source_id", "follow-on source id must name the verified arXiv version"))
    source_report = validate_alphaevolve_follow_on_math_source(value.get("source_record"))
    issues.extend(source_report.issues)
    _validate_follow_on_claim_artifact_links(value.get("claim_artifact_links"), issues)
    _validate_follow_on_cache_policy(value.get("cache_policy"), issues)
    _validate_follow_on_manifest_remaining_work(value.get("remaining_work"), issues)
    return source_report


def _validate_follow_on_claim_artifact_links(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_claim_artifact_links", "claim_artifact_links must be an object"))
        return
    expected_surfaces = {
        "README.md",
        "ROADMAP.md",
        "papers/README.md",
        "docs/todo/code.md",
        "docs/todo/papers.md",
        "docs/todo/readme.md",
        "docs/todo/roadmap.md",
    }
    surfaces = value.get("follow_on_source_used_by")
    if not isinstance(surfaces, list) or not all(isinstance(item, str) for item in surfaces):
        issues.append(_issue("invalid_claim_artifact_surfaces", "follow_on_source_used_by must list docs, papers, and active TODO surfaces"))
    elif set(surfaces) != expected_surfaces:
        issues.append(_issue("claim_artifact_surface_mismatch", "follow_on_source_used_by must cover docs, papers, and active TODO evidence"))
    if value.get("policy") != (
        "follow_on_sources_must_not_be_treated_as_original_"
        "alphaevolve_spec_or_cached_pdf"
    ):
        issues.append(_issue("invalid_claim_artifact_policy", "claim artifact policy must preserve original-paper and cached-PDF boundaries"))


def _validate_follow_on_cache_policy(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_cache_policy", "cache_policy must be an object"))
        return
    expected = {
        "paper_cache_manifest_row_required": False,
        "explicit_no_cache_policy_recorded": True,
        "repository_snapshot_required": True,
        "local_cache_status_field": "source_record.paper.local_cache",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_cache_policy_{field}", f"cache_policy.{field} must preserve the follow-on source cache boundary"))
    scope = value.get("scope")
    if not isinstance(scope, str) or "not cached PDF" not in scope or "not" not in scope:
        issues.append(_issue("invalid_cache_policy_scope", "cache_policy.scope must distinguish source provenance from cached PDFs and per-problem inventory"))


def _validate_follow_on_manifest_remaining_work(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    expected = {
        "complete_per_problem_notebook_artifact_flag_inventory",
        "validate_notebook_prompt_verifier_initial_final_artifacts",
        "map_original_appendix_b_claims_to_follow_on_problem_records",
        "attach_rights_attribution_to_generated_artifacts",
    }
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(_issue("invalid_manifest_remaining_work", "remaining_work must list unsatisfied follow-on work ids"))
        return
    actual = set(value)
    if actual != expected:
        issues.append(_issue("manifest_remaining_work_mismatch", "remaining_work must preserve only unsatisfied follow-on inventory, mapping, and rights work"))


def _validate_repository_rights_repository(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_repository_rights_repository", "repository must be an object", EXPECTED_REPOSITORY_NAME))
        return
    expected = {
        "name": EXPECTED_REPOSITORY_NAME,
        "url": EXPECTED_REPOSITORY_URL,
        "commit": EXPECTED_REPOSITORY_COMMIT,
        "snapshot_date": "2026-06-08",
        "readme_raw_url": (
            "https://raw.githubusercontent.com/google-deepmind/"
            f"alphaevolve_repository_of_problems/{EXPECTED_REPOSITORY_COMMIT}/README.md"
        ),
        "license_file": "LICENSE",
        "license_url": f"{EXPECTED_REPOSITORY_URL}/blob/{EXPECTED_REPOSITORY_COMMIT}/LICENSE",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_repository_rights_repository_{field}", f"repository.{field} must match the pinned rights source", EXPECTED_REPOSITORY_NAME))
    commit = value.get("commit")
    if not isinstance(commit, str) or _COMMIT_RE.fullmatch(commit) is None:
        issues.append(_issue("invalid_repository_rights_commit", "repository.commit must be a 40-character commit hash", EXPECTED_REPOSITORY_NAME))


def _validate_repository_rights_citation(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> bool:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_repository_rights_citation", "citation must be an object", EXPECTED_FOLLOW_ON_ARXIV_ID))
        return False
    expected = {
        "required": True,
        "bibtex_key": "alphaevolve",
        "title": EXPECTED_FOLLOW_ON_TITLE,
        "authors": [
            "Georgiev, Bogdan",
            "Gomez-Serrano, Javier",
            "Tao, Terence",
            "Wagner, Adam Zsolt",
        ],
        "year": 2025,
        "journal": f"arXiv preprint arXiv:{EXPECTED_FOLLOW_ON_ARXIV_ID}",
        "arxiv_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_repository_rights_citation_{field}", f"citation.{field} must match the README BibTeX", EXPECTED_FOLLOW_ON_ARXIV_ID))
    return value.get("required") is True


def _validate_repository_rights_rights(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_repository_rights_rights", "rights must be an object", EXPECTED_REPOSITORY_NAME))
        return 0
    expected = {
        "rights_holder": "Google LLC",
        "copyright_year": 2025,
        "software_license": "Apache-2.0",
        "software_license_url": "https://www.apache.org/licenses/LICENSE-2.0",
        "materials_license": "CC-BY-4.0",
        "materials_license_url": "https://creativecommons.org/licenses/by/4.0/legalcode",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_repository_rights_{field}", f"rights.{field} must match the problem repository README", EXPECTED_REPOSITORY_NAME))
    mapping = value.get("artifact_license_mapping")
    if not isinstance(mapping, dict):
        issues.append(_issue("invalid_repository_rights_artifact_license_mapping", "artifact_license_mapping must be an object", EXPECTED_REPOSITORY_NAME))
        return 0
    if mapping != EXPECTED_FOLLOW_ON_REPOSITORY_LICENSE_MAPPING:
        issues.append(_issue("repository_rights_artifact_license_mapping_mismatch", "artifact license mapping must distinguish software from other materials", EXPECTED_REPOSITORY_NAME))
    return len(mapping)


def _validate_repository_rights_disclaimers(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_repository_rights_disclaimers", "disclaimers must be an object", EXPECTED_REPOSITORY_NAME))
        return
    expected = {
        "as_is": True,
        "official_google_product": False,
        "as_is_source_phrase": 'distributed on an "AS IS" BASIS',
        "non_official_product_source_phrase": "This is not an official Google product.",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_repository_rights_disclaimers_{field}", f"disclaimers.{field} must preserve the README disclaimer", EXPECTED_REPOSITORY_NAME))


def _validate_repository_rights_role_attribution(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_repository_rights_role_attribution", "role_attribution must be an object", EXPECTED_REPOSITORY_NAME))
        return
    expected_names = {"Javier Gomez-Serrano", "Terence Tao"}
    expected_roles = {"supervision", "problem_selection", "review", "analysis", "commentary"}
    contributors = value.get("contributors")
    if not isinstance(contributors, list):
        issues.append(_issue("invalid_repository_rights_contributors", "contributors must be a list", EXPECTED_REPOSITORY_NAME))
        contributors = []
    names = {item.get("name") for item in contributors if isinstance(item, dict)}
    if names != expected_names:
        issues.append(_issue("repository_rights_contributor_mismatch", "contributors must preserve the README role-attribution names", EXPECTED_REPOSITORY_NAME))
    for contributor in contributors:
        if not isinstance(contributor, dict):
            issues.append(_issue("invalid_repository_rights_contributor", "contributors must be objects", EXPECTED_REPOSITORY_NAME))
            continue
        roles = set(contributor.get("roles") or ())
        if roles != expected_roles:
            issues.append(_issue("repository_rights_contributor_roles_mismatch", "contributor roles must preserve supervision/problem-selection/review/analysis/commentary", EXPECTED_REPOSITORY_NAME))
    phrase = value.get("source_phrase")
    if not isinstance(phrase, str) or "problem selection" not in phrase or "analysis and commentary" not in phrase:
        issues.append(_issue("invalid_repository_rights_role_source_phrase", "role source phrase must preserve README attribution wording", EXPECTED_REPOSITORY_NAME))


def _validate_repository_rights_third_party_origins(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    if not isinstance(value, list):
        issues.append(_issue("invalid_repository_rights_third_party_origins", "third_party_origins must be a list", EXPECTED_REPOSITORY_NAME))
        return
    expected = {
        "problem_id": 65,
        "origin": "official IMO problems website",
        "url": "https://www.imo-official.org/problems.aspx",
        "source_phrase": "Problem 65 originates from https://www.imo-official.org/problems.aspx",
    }
    if len(value) != 1 or not isinstance(value[0], dict):
        issues.append(_issue("repository_rights_third_party_origin_count", "third_party_origins must contain the Problem 65 IMO source row", EXPECTED_REPOSITORY_NAME))
        return
    for field, expected_value in expected.items():
        if value[0].get(field) != expected_value:
            issues.append(_issue(f"invalid_repository_rights_third_party_origin_{field}", f"third_party_origins[0].{field} must match README Problem 65 origin", EXPECTED_REPOSITORY_NAME))


def _validate_repository_rights_boundary(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_repository_rights_boundary", "boundary must be an object", EXPECTED_REPOSITORY_NAME))
        return
    expected = {
        "distinct_from_original_alphaevolve_pdf_rights": True,
        "distinct_from_alphaevolve_results_companion_rights": True,
        "distinct_from_libreevolve_mit_license": True,
        "source_rights_holder_required_for_copied_material": True,
        "generated_artifacts_need_source_relationship": True,
        "local_project_endorsement": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_repository_rights_boundary_{field}", f"boundary.{field} must preserve repository rights separation", EXPECTED_REPOSITORY_NAME))


def _validate_repository_rights_manifest_source(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
    index: int,
) -> AlphaEvolveFollowOnRepositoryRightsValidation:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_repository_rights_manifest_source", f"repository-rights manifest source {index} must be an object", EXPECTED_REPOSITORY_NAME))
        return AlphaEvolveFollowOnRepositoryRightsValidation(False, 0, False, 0, [])
    expected = {
        "manifest_row_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
        "follow_on_source_manifest": EXPECTED_FOLLOW_ON_SOURCE_MANIFEST_FILE,
        "repository_rights_id": "alphaevolve_repository_of_problems_rights",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_repository_rights_manifest_{field}", f"{field} must identify the follow-on problem repository rights row", EXPECTED_REPOSITORY_NAME))
    report = validate_alphaevolve_follow_on_repository_rights(value.get("repository_rights_record"))
    issues.extend(report.issues)
    _validate_repository_rights_claim_artifact_links(value.get("claim_artifact_links"), issues)
    _validate_repository_rights_reuse_policy(value.get("reuse_policy"), issues)
    return report


def _validate_repository_rights_claim_artifact_links(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_repository_rights_claim_artifact_links", "claim_artifact_links must be an object", EXPECTED_REPOSITORY_NAME))
        return
    surfaces = value.get("repository_rights_used_by")
    if not isinstance(surfaces, list) or not all(isinstance(item, str) for item in surfaces):
        issues.append(_issue("invalid_repository_rights_claim_surfaces", "repository_rights_used_by must list docs, papers, and active TODO surfaces", EXPECTED_REPOSITORY_NAME))
    elif set(surfaces) != EXPECTED_FOLLOW_ON_REPOSITORY_RIGHTS_SURFACES:
        issues.append(_issue("repository_rights_claim_surface_mismatch", "repository_rights_used_by must cover docs, papers, and active TODO evidence", EXPECTED_REPOSITORY_NAME))
    if value.get("policy") != (
        "follow_on_problem_repository_rights_must_remain_separate_"
        "from_original_pdf_companion_repository_and_libreevolve_license"
    ):
        issues.append(_issue("invalid_repository_rights_claim_policy", "claim policy must separate problem repository rights from other license surfaces", EXPECTED_REPOSITORY_NAME))


def _validate_repository_rights_reuse_policy(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_repository_rights_reuse_policy", "reuse_policy must be an object", EXPECTED_REPOSITORY_NAME))
        return
    expected = {
        "copied_repository_material_requires_source_attribution": True,
        "generated_local_artifacts_require_source_relationship": True,
        "publication_ready_without_rights_review": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_repository_rights_reuse_policy_{field}", f"reuse_policy.{field} must preserve repository rights review boundaries", EXPECTED_REPOSITORY_NAME))
    scope = value.get("scope")
    if not isinstance(scope, str) or "not original AlphaEvolve PDF rights" not in scope or "LibreEvolve project licensing" not in scope:
        issues.append(_issue("invalid_repository_rights_reuse_policy_scope", "reuse_policy.scope must separate repository rights from PDF rights and project licensing", EXPECTED_REPOSITORY_NAME))


def _validate_runtime_absence_repository(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_runtime_absence_repository", "repository must be an object", EXPECTED_REPOSITORY_NAME))
        return
    expected = {
        "name": EXPECTED_REPOSITORY_NAME,
        "url": EXPECTED_REPOSITORY_URL,
        "commit": EXPECTED_REPOSITORY_COMMIT,
        "snapshot_date": "2026-06-08",
        "readme_raw_url": (
            "https://raw.githubusercontent.com/google-deepmind/"
            f"alphaevolve_repository_of_problems/{EXPECTED_REPOSITORY_COMMIT}/README.md"
        ),
        "tree_api_url": (
            "https://api.github.com/repos/google-deepmind/"
            "alphaevolve_repository_of_problems/git/trees/"
            f"{EXPECTED_REPOSITORY_COMMIT}?recursive=1"
        ),
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_runtime_absence_repository_{field}", f"repository.{field} must match the pinned runtime-absence source", EXPECTED_REPOSITORY_NAME))
    commit = value.get("commit")
    if not isinstance(commit, str) or _COMMIT_RE.fullmatch(commit) is None:
        issues.append(_issue("invalid_runtime_absence_commit", "repository.commit must be a 40-character commit hash", EXPECTED_REPOSITORY_NAME))


def _validate_runtime_absence_notebook_inventory(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_runtime_absence_notebook_inventory", "notebook_inventory must be an object", EXPECTED_REPOSITORY_NAME))
        return 0
    expected_fields = {
        "notebook_count": len(EXPECTED_FOLLOW_ON_NOTEBOOKS),
        "coverage": "many_not_all_problem_notebooks",
        "hash_algorithm": "git_blob_sha1_and_raw_sha256",
        "sha256_inventory_complete": True,
        "problem_id_mapping_complete": True,
        "absence_reason_inventory_complete": True,
    }
    for field, expected_value in expected_fields.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_runtime_absence_notebook_{field}", f"notebook_inventory.{field} must preserve pinned notebook inventory scope", EXPECTED_REPOSITORY_NAME))
    notebooks = value.get("notebooks")
    if not isinstance(notebooks, list):
        issues.append(_issue("invalid_runtime_absence_notebook_list", "notebook_inventory.notebooks must be a list", EXPECTED_REPOSITORY_NAME))
        return 0
    expected_by_path = {
        path: {
            "bytes": byte_count,
            "git_blob_sha": git_blob_sha,
            "sha256": EXPECTED_FOLLOW_ON_NOTEBOOK_SHA256S[path],
        }
        for path, byte_count, git_blob_sha in EXPECTED_FOLLOW_ON_NOTEBOOKS
    }
    actual_paths = [item.get("path") for item in notebooks if isinstance(item, dict)]
    if set(actual_paths) != set(expected_by_path) or len(actual_paths) != len(EXPECTED_FOLLOW_ON_NOTEBOOKS):
        issues.append(_issue("runtime_absence_notebook_inventory_mismatch", "notebook inventory must contain exactly the pinned repository notebooks", EXPECTED_REPOSITORY_NAME))
    for notebook in notebooks:
        if not isinstance(notebook, dict):
            issues.append(_issue("invalid_runtime_absence_notebook", "notebook entries must be objects", EXPECTED_REPOSITORY_NAME))
            continue
        path = notebook.get("path")
        if not isinstance(path, str) or path not in expected_by_path:
            issues.append(_issue("invalid_runtime_absence_notebook_path", "notebook.path must match a pinned notebook path", EXPECTED_REPOSITORY_NAME))
            continue
        expected = expected_by_path[path]
        if notebook.get("bytes") != expected["bytes"]:
            issues.append(_issue("invalid_runtime_absence_notebook_bytes", "notebook.bytes must match the pinned GitHub tree size", path))
        git_blob_sha = notebook.get("git_blob_sha")
        if git_blob_sha != expected["git_blob_sha"]:
            issues.append(_issue("invalid_runtime_absence_notebook_git_blob_sha", "notebook.git_blob_sha must match the pinned GitHub tree blob", path))
        if not isinstance(git_blob_sha, str) or _COMMIT_RE.fullmatch(git_blob_sha) is None:
            issues.append(_issue("invalid_runtime_absence_notebook_git_blob_sha_format", "notebook.git_blob_sha must be a 40-character Git blob hash", path))
        sha256 = notebook.get("sha256")
        if sha256 != expected["sha256"]:
            issues.append(_issue("invalid_runtime_absence_notebook_sha256", "notebook.sha256 must match the pinned raw notebook digest", path))
        if not isinstance(sha256, str) or _SHA256_RE.fullmatch(sha256) is None:
            issues.append(_issue("invalid_runtime_absence_notebook_sha256_format", "notebook.sha256 must be a lowercase 64-hex digest", path))
        if notebook.get("artifact_kinds") != list(EXPECTED_FOLLOW_ON_NOTEBOOK_ARTIFACT_KINDS):
            issues.append(_issue("invalid_runtime_absence_notebook_artifact_kinds", "notebook artifact kinds must preserve prompt/verifier/input/output classification", path))
        if notebook.get("alphaevolve_runtime_available") is not False:
            issues.append(_issue("runtime_absence_notebook_runtime_available_overclaim", "notebooks must not be marked as AlphaEvolve runtime implementations", path))
    return len(notebooks)


def _validate_runtime_absence_boundary(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> tuple[bool, bool]:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_runtime_absence_boundary", "runtime_boundary must be an object", EXPECTED_REPOSITORY_NAME))
        return False, False
    expected = {
        "alphaevolve_runtime_available": False,
        "verifier_code_available": True,
        "verifier_is_not_runtime": True,
        "notebook_artifacts_are_experiment_inputs_and_outputs": True,
        "no_installation_required": True,
        "colab_browser_access_only": True,
        "absence_source_phrase": "This repository does *not* contain the code to run AlphaEvolve.",
        "artifact_source_phrase": (
            "Each notebook contains the prompt, verification code, and initial program "
            "used to launch the AlphaEvolve experiments, along with the final evolved "
            "programs and visualization / analysis code where appropriate."
        ),
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_runtime_absence_boundary_{field}", f"runtime_boundary.{field} must preserve repository README runtime boundary", EXPECTED_REPOSITORY_NAME))
    if value.get("alphaevolve_runtime_available") is not False:
        issues.append(_issue("runtime_absence_runtime_available_overclaim", "the follow-on repository must not be recorded as containing AlphaEvolve runtime code", EXPECTED_REPOSITORY_NAME))
    if value.get("verifier_is_not_runtime") is not True:
        issues.append(_issue("runtime_absence_verifier_runtime_boundary_missing", "verification code availability must stay separate from AlphaEvolve runtime availability", EXPECTED_REPOSITORY_NAME))
    return value.get("alphaevolve_runtime_available") is True, value.get("verifier_code_available") is True


def _validate_runtime_absence_limits(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_runtime_absence_limits", "boundary must be an object", EXPECTED_REPOSITORY_NAME))
        return
    expected = {
        "not_alphaevolve_runtime_implementation": True,
        "not_replayable_alphaevolve_service": True,
        "not_full_notebook_cell_inventory": True,
        "not_cell_artifact_flag_inventory": True,
        "must_not_describe_notebooks_as_runtime_harnesses": True,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_runtime_absence_limits_{field}", f"boundary.{field} must preserve scoped runtime-absence limitations", EXPECTED_REPOSITORY_NAME))


def _validate_remaining_runtime_work(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    expected = {
        "validate_notebook_cell_artifact_flags",
    }
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(_issue("invalid_remaining_runtime_work", "remaining_runtime_work must list unsatisfied runtime-absence follow-ups", EXPECTED_REPOSITORY_NAME))
        return
    if set(value) != expected:
        issues.append(_issue("remaining_runtime_work_mismatch", "remaining_runtime_work must preserve cell-artifact follow-ups", EXPECTED_REPOSITORY_NAME))


def _validate_runtime_absence_manifest_source(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
    index: int,
) -> AlphaEvolveFollowOnRuntimeAbsenceValidation:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_runtime_absence_manifest_source", f"runtime-absence manifest source {index} must be an object", EXPECTED_REPOSITORY_NAME))
        return AlphaEvolveFollowOnRuntimeAbsenceValidation(False, 0, 0, False, False, [])
    expected = {
        "manifest_row_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
        "follow_on_source_manifest": EXPECTED_FOLLOW_ON_SOURCE_MANIFEST_FILE,
        "runtime_absence_id": "alphaevolve_repository_of_problems_runtime_absence",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_runtime_absence_manifest_{field}", f"{field} must identify the follow-on problem repository runtime-absence row", EXPECTED_REPOSITORY_NAME))
    report = validate_alphaevolve_follow_on_runtime_absence(value.get("runtime_absence_record"))
    issues.extend(report.issues)
    _validate_runtime_absence_claim_artifact_links(value.get("claim_artifact_links"), issues)
    _validate_runtime_claim_policy(value.get("runtime_claim_policy"), issues)
    return report


def _validate_runtime_absence_claim_artifact_links(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_runtime_absence_claim_artifact_links", "claim_artifact_links must be an object", EXPECTED_REPOSITORY_NAME))
        return
    surfaces = value.get("runtime_absence_used_by")
    if not isinstance(surfaces, list) or not all(isinstance(item, str) for item in surfaces):
        issues.append(_issue("invalid_runtime_absence_claim_surfaces", "runtime_absence_used_by must list docs, papers, and active TODO surfaces", EXPECTED_REPOSITORY_NAME))
    elif set(surfaces) != EXPECTED_FOLLOW_ON_RUNTIME_SURFACES:
        issues.append(_issue("runtime_absence_claim_surface_mismatch", "runtime_absence_used_by must cover docs, papers, and active TODO evidence", EXPECTED_REPOSITORY_NAME))
    if value.get("policy") != (
        "follow_on_problem_repository_notebooks_must_not_be_treated_"
        "as_alphaevolve_runtime"
    ):
        issues.append(_issue("invalid_runtime_absence_claim_policy", "claim policy must keep notebooks separate from AlphaEvolve runtime availability", EXPECTED_REPOSITORY_NAME))


def _validate_runtime_claim_policy(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_runtime_claim_policy", "runtime_claim_policy must be an object", EXPECTED_REPOSITORY_NAME))
        return
    expected = {
        "prompt_verifier_outputs_are_source_artifacts": True,
        "alphaevolve_runtime_available": False,
        "publication_ready_runtime_claim": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_runtime_claim_policy_{field}", f"runtime_claim_policy.{field} must preserve scoped runtime claim policy", EXPECTED_REPOSITORY_NAME))
    scope = value.get("scope")
    if not isinstance(scope, str) or "runtime absence" not in scope or "not full notebook inventory" not in scope:
        issues.append(_issue("invalid_runtime_claim_policy_scope", "runtime_claim_policy.scope must distinguish runtime absence from full notebook inventory", EXPECTED_REPOSITORY_NAME))


def _validate_tao_blog_post(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_tao_blog_post", "post must be an object", EXPECTED_TAO_BLOG_URL))
        return
    expected = {
        "post_id": EXPECTED_TAO_BLOG_POST_ID,
        "title": EXPECTED_TAO_BLOG_TITLE,
        "author": EXPECTED_TAO_BLOG_AUTHOR,
        "post_date": EXPECTED_TAO_BLOG_POST_DATE,
        "modified_date": EXPECTED_TAO_BLOG_MODIFIED_DATE,
        "site_title": "What's new",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_tao_blog_post_{field}", f"post.{field} must match the pinned WordPress API metadata", EXPECTED_TAO_BLOG_URL))


def _validate_tao_blog_retrieval(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_tao_blog_retrieval", "retrieval must be an object", EXPECTED_TAO_BLOG_URL))
        return
    expected = {
        "retrieved_on": "2026-06-09",
        "api_bytes": EXPECTED_TAO_BLOG_API_BYTES,
        "api_sha256": EXPECTED_TAO_BLOG_API_SHA256,
        "html_bytes": EXPECTED_TAO_BLOG_HTML_BYTES,
        "html_sha256": EXPECTED_TAO_BLOG_HTML_SHA256,
        "hash_algorithm": "sha256",
        "api_surface_preferred": True,
        "html_surface_expected_volatile": True,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_tao_blog_retrieval_{field}", f"retrieval.{field} must match the pinned Tao blog retrieval metadata", EXPECTED_TAO_BLOG_URL))
    for field in ("api_sha256", "html_sha256"):
        digest = value.get(field)
        if not isinstance(digest, str) or _SHA256_RE.fullmatch(digest) is None:
            issues.append(_issue(f"invalid_tao_blog_retrieval_{field}_format", f"retrieval.{field} must be a SHA-256 digest", EXPECTED_TAO_BLOG_URL))


def _validate_tao_blog_linked_sources(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> bool:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_tao_blog_linked_sources", "linked_sources must be an object", EXPECTED_TAO_BLOG_URL))
        return False
    expected = {
        "follow_on_arxiv_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
        "follow_on_arxiv_url": f"https://arxiv.org/abs/{EXPECTED_FOLLOW_ON_ARXIV_ID}",
        "problem_repository_url": EXPECTED_REPOSITORY_URL,
        "problem_repository_commit": EXPECTED_REPOSITORY_COMMIT,
        "alphaevolve_tool_url": (
            "https://deepmind.google/discover/blog/"
            "alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/"
        ),
        "original_whitepaper_url": (
            "https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/"
            "alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/"
            "AlphaEvolve.pdf"
        ),
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_tao_blog_linked_{field}", f"linked_sources.{field} must preserve Tao blog cross-source links", EXPECTED_TAO_BLOG_URL))
    commit = value.get("problem_repository_commit")
    if not isinstance(commit, str) or _COMMIT_RE.fullmatch(commit) is None:
        issues.append(_issue("invalid_tao_blog_repository_commit", "problem_repository_commit must be a 40-character commit hash", EXPECTED_TAO_BLOG_URL))
    return value.get("problem_repository_commit") == EXPECTED_REPOSITORY_COMMIT


def _validate_tao_blog_claim_spans(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_tao_blog_claim_spans", "claim_spans must be a list", EXPECTED_TAO_BLOG_URL))
        return 0
    categories = []
    for claim in value:
        if not isinstance(claim, dict):
            issues.append(_issue("invalid_tao_blog_claim_span", "claim span entries must be objects", EXPECTED_TAO_BLOG_URL))
            continue
        category = claim.get("category")
        categories.append(category)
        if category not in EXPECTED_TAO_BLOG_CLAIM_CATEGORIES:
            issues.append(_issue("invalid_tao_blog_claim_category", "claim category must match the Tao blog category taxonomy", EXPECTED_TAO_BLOG_URL))
        if not isinstance(claim.get("source_lines"), str) or not claim["source_lines"]:
            issues.append(_issue("invalid_tao_blog_claim_source_lines", "claim spans must preserve source line references", EXPECTED_TAO_BLOG_URL))
        summary = claim.get("summary")
        if not isinstance(summary, str) or len(summary) < 40:
            issues.append(_issue("invalid_tao_blog_claim_summary", "claim spans must include bounded paraphrased summaries", EXPECTED_TAO_BLOG_URL))
        if claim.get("requires_backing_artifact") is not True and category != "commentary":
            issues.append(_issue("tao_blog_claim_backing_artifact_missing", "non-commentary Tao blog claims must require backing artifacts", EXPECTED_TAO_BLOG_URL))
    if tuple(categories) != EXPECTED_TAO_BLOG_CLAIM_CATEGORIES:
        issues.append(_issue("tao_blog_claim_category_mismatch", "claim_spans must preserve commentary, experiment, verifier, negative-result, proof-handoff, and future-work categories", EXPECTED_TAO_BLOG_URL))
    return len([category for category in categories if isinstance(category, str)])


def _validate_tao_blog_claim_boundary(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> bool:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_tao_blog_claim_boundary", "claim_boundary must be an object", EXPECTED_TAO_BLOG_URL))
        return False
    expected = {
        "blog_commentary_secondary": True,
        "blog_only_claims_require_paper_repository_or_proof_artifact": True,
        "not_original_alphaevolve_spec": True,
        "not_runtime_implementation_evidence": True,
        "not_repository_snapshot": True,
        "not_proof_artifact": True,
        "not_independent_verification": True,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_tao_blog_claim_boundary_{field}", f"claim_boundary.{field} must preserve Tao blog source limits", EXPECTED_TAO_BLOG_URL))
    return value.get("blog_commentary_secondary") is True


def _validate_tao_blog_remaining_work(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    expected = {
        "map_blog_claims_to_paper_sections",
        "map_blog_claims_to_repository_problem_ids",
        "attach_proof_artifacts_for_handoff_claims",
        "separate_comment_thread_claims_from_post_claims",
    }
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(_issue("invalid_tao_blog_remaining_work", "remaining_work must list unsatisfied Tao blog follow-ups", EXPECTED_TAO_BLOG_URL))
        return
    if set(value) != expected:
        issues.append(_issue("tao_blog_remaining_work_mismatch", "remaining_work must preserve blog-to-paper/repository/proof mapping follow-ups", EXPECTED_TAO_BLOG_URL))


def _validate_tao_blog_manifest_source(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
    index: int,
) -> AlphaEvolveFollowOnTaoBlogValidation:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_tao_blog_manifest_source", f"Tao blog manifest source {index} must be an object", EXPECTED_TAO_BLOG_URL))
        return AlphaEvolveFollowOnTaoBlogValidation(False, 0, 0, False, False, [])
    expected = {
        "manifest_row_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
        "follow_on_source_manifest": EXPECTED_FOLLOW_ON_SOURCE_MANIFEST_FILE,
        "tao_blog_source_id": "terence_tao_2025_11_05_mathematical_exploration",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_tao_blog_manifest_{field}", f"{field} must identify the Tao follow-on blog source row", EXPECTED_TAO_BLOG_URL))
    report = validate_alphaevolve_follow_on_tao_blog(value.get("source_record"))
    issues.extend(report.issues)
    _validate_tao_blog_claim_artifact_links(value.get("claim_artifact_links"), issues)
    _validate_tao_blog_evidence_policy(value.get("evidence_policy"), issues)
    return report


def _validate_tao_blog_claim_artifact_links(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_tao_blog_claim_artifact_links", "claim_artifact_links must be an object", EXPECTED_TAO_BLOG_URL))
        return
    surfaces = value.get("tao_blog_used_by")
    if not isinstance(surfaces, list) or not all(isinstance(item, str) for item in surfaces):
        issues.append(_issue("invalid_tao_blog_claim_surfaces", "tao_blog_used_by must list docs, papers, and active TODO surfaces", EXPECTED_TAO_BLOG_URL))
    elif set(surfaces) != EXPECTED_TAO_BLOG_SURFACES:
        issues.append(_issue("tao_blog_claim_surface_mismatch", "tao_blog_used_by must cover docs, papers, and active TODO evidence", EXPECTED_TAO_BLOG_URL))
    if value.get("policy") != (
        "tao_blog_claims_are_secondary_until_backed_by_"
        "paper_repository_notebook_verifier_or_proof_artifacts"
    ):
        issues.append(_issue("invalid_tao_blog_claim_policy", "claim policy must keep Tao blog claims secondary until backed by artifacts", EXPECTED_TAO_BLOG_URL))


def _validate_tao_blog_evidence_policy(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_tao_blog_evidence_policy", "evidence_policy must be an object", EXPECTED_TAO_BLOG_URL))
        return
    expected = {
        "commentary_secondary": True,
        "publication_ready_without_backing_artifacts": False,
        "comment_thread_included": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_tao_blog_evidence_policy_{field}", f"evidence_policy.{field} must preserve Tao blog evidence boundaries", EXPECTED_TAO_BLOG_URL))
    scope = value.get("scope")
    if not isinstance(scope, str) or "not original AlphaEvolve specification" not in scope:
        issues.append(_issue("invalid_tao_blog_evidence_policy_scope", "evidence_policy.scope must separate Tao blog metadata from the original AlphaEvolve specification", EXPECTED_TAO_BLOG_URL))


def _issue(code: str, message: str, source_id: str | None = None) -> AlphaEvolveFollowOnMathSourceIssue:
    return AlphaEvolveFollowOnMathSourceIssue(code, message, source_id)
