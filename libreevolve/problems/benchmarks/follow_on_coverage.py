from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.follow_on_sources import (
    EXPECTED_DECLARED_PROBLEM_COUNT,
    EXPECTED_FOLLOW_ON_NOTEBOOKS,
    EXPECTED_FOLLOW_ON_RUNTIME_ABSENCE_MANIFEST_FILE,
    EXPECTED_REPOSITORY_COMMIT,
    EXPECTED_REPOSITORY_NAME,
    EXPECTED_REPOSITORY_URL,
)


ALPHAEVOLVE_FOLLOW_ON_PROBLEM_COVERAGE_SCHEMA = "libreevolve.alphaevolve_follow_on_problem_coverage.v1"
EXPECTED_SNAPSHOT_DATE = "2026-06-08"
EXPECTED_PROBLEM_IDS = tuple(range(1, EXPECTED_DECLARED_PROBLEM_COUNT + 1))
EXPECTED_EXTRA_NUMBERED_PAGE_IDS = (68,)
EXPECTED_OBSERVED_NUMBERED_HTML_COUNT = 68
EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS = {
    "diagnostic_scope": "extra_numbered_page_68_and_duplicate_logic_puzzles_context",
    "diagnosed_page_ids": (67, 68),
    "classification": "page_68_extra_numbered_duplicate_title_outside_declared_67_navigation",
    "classification_complete": True,
    "all_page_diagnostics_complete": False,
    "resource_link_diagnostics_complete_for_diagnosed_pages": True,
    "duplicate_title_groups": (
        {"title": "Logic puzzles", "page_ids": (67, 68), "paper_section": "6.44"},
    ),
    "pages": (
        {
            "page_id": 67,
            "path": "problems/67.html",
            "title": "67. Logic puzzles",
            "title_key": "Logic puzzles",
            "bytes": 12428,
            "sha256": "bd265b4b409493956a3d577bccd17325c468f66a695efc1dffc67dc7e5f468d8",
            "declared_navigation_total_problems": 67,
            "paper_section": "6.44",
            "colab_url": "#",
            "colab_link_status": "under_construction_placeholder",
            "paper_url": "https://arxiv.org/abs/2511.02864",
            "paper_link_status": "valid_follow_on_arxiv",
            "classification": "declared_range_duplicate_title_context_page",
        },
        {
            "page_id": 68,
            "path": "problems/68.html",
            "title": "68. Logic puzzles",
            "title_key": "Logic puzzles",
            "bytes": 9253,
            "sha256": "51eda861f49691d2db5b1ec2775dbd77c5cc47afde791416c9283c23de2ca75d",
            "declared_navigation_total_problems": None,
            "paper_section": "6.44",
            "colab_url": "https://colab.research.google.com/",
            "colab_link_status": "generic_colab_landing_page",
            "paper_url": "#",
            "paper_link_status": "placeholder",
            "classification": "extra_numbered_page_duplicate_title_outside_declared_67_navigation",
        },
    ),
}
EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS = {
    "diagnostic_scope": "all_numbered_pages_resource_links",
    "diagnosed_page_count": EXPECTED_OBSERVED_NUMBERED_HTML_COUNT,
    "resource_link_diagnostics_complete": True,
    "page_hash_inventory_complete": True,
    "colab_link_status_counts": {
        "generic_colab_landing_page": 1,
        "github_notebook_blob_url": 36,
        "google_colab_url": 6,
        "under_construction_placeholder": 25,
    },
    "colab_link_status_page_ids": {
        "generic_colab_landing_page": (68,),
        "github_notebook_blob_url": (
            1, 2, 3, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 27, 28,
            32, 33, 34, 35, 36, 42, 44, 45, 46, 53, 54, 58, 59, 60, 61,
            62, 63, 64, 65,
        ),
        "google_colab_url": (4, 5, 8, 48, 49, 50),
        "under_construction_placeholder": (
            6, 20, 21, 22, 23, 24, 25, 26, 29, 30, 31, 37, 38, 39, 40, 41,
            43, 47, 51, 52, 55, 56, 57, 66, 67,
        ),
    },
    "paper_link_status_counts": {
        "placeholder": 1,
        "valid_follow_on_arxiv": 67,
    },
    "paper_link_status_page_ids": {
        "placeholder": (68,),
        "valid_follow_on_arxiv": tuple(range(1, 68)),
    },
    "navigation_total_problem_counts": {
        "67": 67,
        "missing": 1,
    },
    "missing_navigation_total_problem_page_ids": (68,),
    "duplicate_title_groups": (
        {"title": "Logic puzzles", "page_ids": (67, 68)},
    ),
    "multi_page_paper_section_groups": (
        {"paper_section": "6.18", "page_ids": (33, 34)},
        {"paper_section": "6.19", "page_ids": (35, 36)},
        {"paper_section": "6.2", "page_ids": (2, 3, 4, 5, 6)},
        {"paper_section": "6.25", "page_ids": (42, 43, 44)},
        {"paper_section": "6.29", "page_ids": (48, 49)},
        {"paper_section": "6.42", "page_ids": (62, 63, 64)},
        {"paper_section": "6.44", "page_ids": (66, 67, 68)},
        {"paper_section": "6.5", "page_ids": (9, 10)},
        {"paper_section": "6.6", "page_ids": (11, 12, 13)},
        {"paper_section": "6.7", "page_ids": (14, 15, 16, 17, 18)},
        {"paper_section": "6.9", "page_ids": (20, 21, 22, 23, 24)},
    ),
}
EXPECTED_ALL_PAGE_HASH_INVENTORY = {
    "diagnostic_scope": "all_numbered_pages_raw_html_hashes",
    "page_count": EXPECTED_OBSERVED_NUMBERED_HTML_COUNT,
    "declared_problem_page_count": EXPECTED_DECLARED_PROBLEM_COUNT,
    "extra_numbered_page_ids": EXPECTED_EXTRA_NUMBERED_PAGE_IDS,
    "page_hash_inventory_complete": True,
    "notebook_mapping_complete": False,
    "artifact_presence_matrix_complete": False,
    "pages": (
        (1, 13949, "b89661360a9be3913286bda2115bd00db8ec57cbd01a364c3d9e9d58f30cf0bf"),
        (2, 15197, "646585d70e1605f6c8693450ec7921b8b38313ebd0f18a5f1b8da565a3bbd3d1"),
        (3, 14141, "ec6e9ad7e42f71456cba200070899e007126d5436fe771d7a0d0220a01cb6feb"),
        (4, 12693, "a0c53173c842a90801f8d8187ffd065355a4ad4c3256768df47eb027caed8221"),
        (5, 13982, "237765d9009c938a6bb101e0d7e11e10fb3e8c270cc485e71f822d4e9d60bb25"),
        (6, 12213, "1a015ed57fde3b2117d43ada01f7168b6ce323d1f8be33f837681e8ee96c5656"),
        (7, 12524, "a41d53032e293a190a6069603c2b25be7f04dfb7fa80675a29ac25d41beb9169"),
        (8, 12752, "ce81f9adaab67df783dfc587b0f457493e5eeff31c818881084da715468cad6b"),
        (9, 14171, "401d94597707a735a75f86597d90a52ebb2b11ef2f5d04808d361cc258f687f0"),
        (10, 12827, "b0f013739a79ead72e305f6098ffaf940ffe49d4b86e9a9b6940a048b33bae92"),
        (11, 14433, "b0b30a161c5870cba1fcc5aaf2789f84a6512525aec5052d0642b00a9df7e9b5"),
        (12, 12330, "6c946e1577113386b20b0177fd03020218d32258f36e4dc640fd06265d4cabc6"),
        (13, 12601, "46e6c69cb09f94fdc5f67083d0c513d63e9b07d5acc2ff59bc1c479e4e3ca50a"),
        (14, 10595, "1ba6026cb829469078afb2d71fc30ba0ae2d8457e1e9b520812820f8e9cc718a"),
        (15, 12818, "e558f5ed9f1a91a3d918a3324b2f31a525e93a39f45cc3534939c7db50bcb31b"),
        (16, 10564, "49eae5bdb9746302e4ac7908df2ee052c77f4d3ff817fe128847f6db58bf64d6"),
        (17, 10522, "b6c37b7cf63391cf07ee10449d1f02359241ec9ed9ab43c1db411b2fc251c58a"),
        (18, 10572, "b99f1130ab0a8ff5c058a632c86db21935a147fb6afaa8a55af317dcd145f76a"),
        (19, 12429, "db8b81c74c700e8c4e95a746926262d44150b7b12d6fc66334f29652b089df2a"),
        (20, 12255, "15ccbb11a5758674b0c290b667480445c71f7856bb13e62f748dec00ef5f857d"),
        (21, 12383, "025b412a3c279815d375826e19bb79639e7eaf4a69598d8bfa40f282d92ba748"),
        (22, 12300, "e7b2e82471c900c27eace5b095d7ffd6d83548bca5f7ab618df88fe797756b84"),
        (23, 12269, "526df2c71cb27be4b779dfb65b8b17acc9068a1421f60c79d300876c95029025"),
        (24, 12595, "ef7172f43de90ab18778bd2c8461e80838ff23ca04f95eee6f3ec9d0d62a1f19"),
        (25, 12356, "dee73d2bae90e8fc64cfcaeaf2a7b453fb9deb814fff2d4789cbb7f22a43ad38"),
        (26, 12436, "78b946f2c2697eebc6de1f63c1d6d92d82f215bd6f59d688df3c3471619bd386"),
        (27, 12354, "0e63e2b650f3298232f2cde14927baa9f15638954c79b115f20cb4f9124732c8"),
        (28, 12855, "bdf43f5b97b550f6db3a0c56c0d78fb70f37db08b25b0758da1c35ecae4e9823"),
        (29, 12417, "c83e89bc2f4961d3c3d323798cbc2425ecf18638e8af8a3d37502699799318ab"),
        (30, 12987, "968ab0775746a3559c15a8495c193afb2cfdb162f67a7e161866e851bb6506d5"),
        (31, 12253, "eb9a6548be484d663443b9f1baa9a6e56541ff6d93a1784ba63a685eabd29964"),
        (32, 12511, "c1d6aa9cdffad09f00fdd9c733aa52c24fdd6a649692beae6a805899529ab481"),
        (33, 10709, "9e9b1a714e31d03d85fc118ebf271fda0ee7b45b04e299349e4b0e822881fc10"),
        (34, 10687, "0013bad821be12af5008d59d3da0e840c68d3ae429afd047622ee734136e2c57"),
        (35, 12438, "e9ad9635b199548429a5f3b8d0b01afc82a4d44bc9f17a73b71d5aa03803b32d"),
        (36, 12875, "7d2b14a0b7cecff708531b79a1e07bcd6f0e18bdb506d87555ee59a81897743c"),
        (37, 12225, "63eff7836816c34d9a454636a753b8cecf38aa3a3d5cdf9ead92e7bdeb4a3b45"),
        (38, 12263, "31a37a7368df5ba826642a6bc5abdbea24e54eadc67a95e8c85afb7450e71acd"),
        (39, 12287, "89ef3ea763d96f3f008da618cc5038b54bd72191e5b04d0575d4ca1815293e8e"),
        (40, 12380, "c5db0d89612f3fe6357d149f4c724f79b2b78f04e28caa52e2c020b5a641a56b"),
        (41, 12185, "dbd01612a65e855e646c1f90414757741cb14cc7d18bd643fd19949daf0f41ed"),
        (42, 11949, "3a93d8c92c5bf6e6c41204c7460cc0771d59a8ed1f43199a9fe71272230cdfa0"),
        (43, 12159, "fb056e5a5197dc5e157df08a1c7162455ab4fdcc9c463837d4c4c355f0976b83"),
        (44, 12679, "02dc537e628c97d9ae4dfb4fc79dce49c1659933190406df1bbd6f2a698bbab4"),
        (45, 12401, "bacde1f9b91f9ff005a066a4eaa38403040177ad21efc70c609848eb61823802"),
        (46, 12339, "a69cc1fdb1e113df11aa2d2f7b170567bbead5c05957af3f102791d35ff9360f"),
        (47, 12570, "750df57c49a70731f764273d07675734838b68743743f5011e986d3250900aa6"),
        (48, 12395, "6b17136dc53788a0c919e428e8aaef0d9d825cd332939d930cf6607a8023912d"),
        (49, 12384, "534da6cc9c9c300d10c7deb671be23a10522a8261c52e3e343de77bf2f319b37"),
        (50, 12517, "67244e697c8a4705dace5530c26c9e1a987a7fc33eaa47e288519e592d4f1d32"),
        (51, 12100, "2ee6b87e1c2fbe84aff1953259ccd889e188fc425964843d5a74ee647a88b268"),
        (52, 12435, "c758a3f7bf832b011dc071ade466245c6863375a771557d1761bd934e3c87ec6"),
        (53, 12246, "608b53f2e266fbdc7a73275ebef023c5037aff04e276474524fa7906ee3f180b"),
        (54, 12210, "834fc2d23c51eb1dc6b5d0f7292c0ccadff7c7d37d24f6c2101c653c0f23a10c"),
        (55, 12206, "ddfe754d5870a5d8826db36e8165abc9d3fa4ba8ab40472949b89ea76158be42"),
        (56, 12225, "d41a6eaa47878d82725fea021ef8d26054fb48d336ef9b574ce3641097036deb"),
        (57, 12386, "0e20f7353adf24ee7fc7702a134a55aafb013e69a31a263660d8e72a1bc07c12"),
        (58, 12367, "fad463b4f9de97726b9862ca9fe2d8b2d9e2b7196abaec1dba24d55143f3d3d1"),
        (59, 12557, "b7ab2d01acdb79e46872cac716b84c6310cb678d870fc317696c2001fabf0dd3"),
        (60, 12329, "0c77502c6361596d1866f8b4c8cc839919ce19eee9f62e62e9fd137e0e76448e"),
        (61, 12552, "94f9081ea0678e8511a5f8a4111d26e1c5bcf5fbaca77452ea44c810e58bd540"),
        (62, 12333, "89fa7520206a164fe6dbe31c00724de565fa80b1092faf3e8fb8498cd59afd84"),
        (63, 12436, "2ea7bb0f780aa31148c300ef2d890a2c76aa75cc12f09a719d9a8863e8d20d9d"),
        (64, 12426, "0c6ed4813ee0423dd5de551639d3b107b4f376ae136c8dfcb984346625b2ee3f"),
        (65, 12553, "e45c057cbe4a20d48aafad1591b1c910d15100ca30d757c6a96ecfc01677ff93"),
        (66, 12688, "70f58325370bc172548b8f95c04efaca81a93e9540233433213f2fd148618784"),
        (67, 12428, "bd265b4b409493956a3d577bccd17325c468f66a695efc1dffc67dc7e5f468d8"),
        (68, 9253, "51eda861f49691d2db5b1ec2775dbd77c5cc47afde791416c9283c23de2ca75d"),
    ),
}
EXPECTED_ALL_PAGE_TITLE_SECTION_ROWS = (
    (1, '1. Kakeya and Nikodym sets in finite fields', 'Kakeya and Nikodym sets in finite fields', '6.1', 67),
    (2, '2. An autocorrelation problem related to Sidon sets', 'An autocorrelation problem related to Sidon sets', '6.2', 67),
    (3, '3. How much can an autocorrelation of a non-negative function resemble an indicator function? ', 'How much can an autocorrelation of a non-negative function resemble an indicator function? ', '6.2', 67),
    (4, '4. An autocorrelation problem with functions that can take negative values', 'An autocorrelation problem with functions that can take negative values', '6.2', 67),
    (5, '5. Erd\u0151s minimum overlap problem', 'Erd\u0151s minimum overlap problem', '6.2', 67),
    (6, '6. An autocorrelation problem related to difference bases', 'An autocorrelation problem related to difference bases', '6.2', 67),
    (7, '7. Difference Bases', 'Difference Bases', '6.3', 67),
    (8, '8. Kissing numbers', 'Kissing numbers', '6.4', 67),
    (9, '9. Kakeya needle problem', 'Kakeya needle problem', '6.5', 67),
    (10, '10. 3D Kakeya problem', '3D Kakeya problem', '6.5', 67),
    (11, '11. Uncertainty principle', 'Uncertainty principle', '6.6', 67),
    (12, '12. Sphere Packing', 'Sphere Packing', '6.6', 67),
    (13, '13. A Linear Programming Bound', 'A Linear Programming Bound', '6.6', 67),
    (14, '14. Hausdorff-Young Inequality', 'Hausdorff-Young Inequality', '6.7', 67),
    (15, '15. Gagliardo-Nirenberg Inequality', 'Gagliardo-Nirenberg Inequality', '6.7', 67),
    (16, '16. Special Case of Gagliardo-Nirenberg Inequality', 'Special Case of Gagliardo-Nirenberg Inequality', '6.7', 67),
    (17, "17. Young's Convolution Inequality", "Young's Convolution Inequality", '6.7', 67),
    (18, '18. Hardy-Littlewood Maximal Inequality', 'Hardy-Littlewood Maximal Inequality', '6.7', 67),
    (19, '19. The Ovals Problem', 'The Ovals Problem', '6.8', 67),
    (20, "20. Sendov's Conjecture", "Sendov's Conjecture", '6.9', 67),
    (21, "21. Schmeisser's Conjecture", "Schmeisser's Conjecture", '6.9', 67),
    (22, "22. Borcea's Conjecture", "Borcea's Conjecture", '6.9', 67),
    (23, "23. Smale's Problem", "Smale's Problem", '6.9', 67),
    (24, '24. de Bruin-Sharma Problem', 'de Bruin-Sharma Problem', '6.9', 67),
    (25, "25. Crouzeix's Conjecture", "Crouzeix's Conjecture", '6.10', 67),
    (26, "26. Sidorenko's Conjecture", "Sidorenko's Conjecture", '6.11', 67),
    (27, '27. The Prime Number Theorem', 'The Prime Number Theorem', '6.12', 67),
    (28, "28. Golay's Merit Factor", "Golay's Merit Factor", '6.13', 67),
    (29, '29. Block Stacking Problem', 'Block Stacking Problem', '6.14', 67),
    (30, '30. The Arithmetic Kakeya Conjecture', 'The Arithmetic Kakeya Conjecture', '6.15', 67),
    (31, '32. Furstenberg-S\xe1rk\xf6zy Problem', 'Furstenberg-S\xe1rk\xf6zy Problem', '6.16', 67),
    (32, '32. Spherical Designs', 'Spherical Designs', '6.17', 67),
    (33, '33. The Thomson Problem', 'The Thomson Problem', '6.18', 67),
    (34, '34. Tammes problem', 'Tammes problem', '6.18', 67),
    (35, '35. Packing in a dilate', 'Packing in a dilate', '6.19', 67),
    (36, '36. Circle packing in a square / rectangle', 'Circle packing in a square / rectangle', '6.19', 67),
    (37, '37. The hypergraph Tur\xe1n number of the tetrahedron', 'The hypergraph Tur\xe1n number of the tetrahedron', '6.20', 67),
    (38, '38. Factoring $N!$ into $N$ numbers', 'Factoring $N!$ into $N$ numbers', '6.21', 67),
    (39, '39. Beat the average game', 'Beat the average game', '6.22', 67),
    (40, '40. Erd\u0151s discrepancy problem', 'Erd\u0151s discrepancy problem', '6.23', 67),
    (41, '41. Points on sphere maximizing the volume', 'Points on sphere maximizing the volume', '6.24', 67),
    (42, '42. Sum-difference problem I', 'Sum-difference problem I', '6.25', 67),
    (43, '43. Sum-difference problem II', 'Sum-difference problem II', '6.25', 67),
    (44, '44. Sum-difference problem III', 'Sum-difference problem III', '6.25', 67),
    (45, '45. Sum-product problems', 'Sum-product problems', '6.26', 67),
    (46, '46. Minimal triangle density in graphs', 'Minimal triangle density in graphs', '6.27', 67),
    (47, '47. Matrix multiplications and AM-GM inequalities', 'Matrix multiplications and AM-GM inequalities', '6.28', 67),
    (48, '48. Heilbronn problem in a fixed bounding box', 'Heilbronn problem in a fixed bounding box', '6.29', 67),
    (49, '49. Heilbronn problem in an arbitrary convex bounding box', 'Heilbronn problem in an arbitrary convex bounding box', '6.29', 67),
    (50, '50. Max to min ratios', 'Max to min ratios', '6.30', 67),
    (51, '51. Erd\u0151s\u2013Gy\xe1rf\xe1s conjecture', 'Erd\u0151s\u2013Gy\xe1rf\xe1s conjecture', '6.31', 67),
    (52, '52. Erd\u0151s squarefree problem', 'Erd\u0151s squarefree problem', '6.32', 67),
    (53, '53. Equidistant points in convex polygons', 'Equidistant points in convex polygons', '6.33', 67),
    (54, '54. Pairwise touching cylinders', 'Pairwise touching cylinders', '6.34', 67),
    (55, '55. Erd\u0151s squares in a square problem', 'Erd\u0151s squares in a square problem', '6.35', 67),
    (56, '56. Good asymptotic constructions of Szemer\xe9di--Trotter', 'Good asymptotic constructions of Szemer\xe9di--Trotter', '6.36', 67),
    (57, '58. Rudin problem for polynomials', 'Rudin problem for polynomials', '6.37', 67),
    (58, '58. Erd\u0151s--Szekeres Happy Ending problem', 'Erd\u0151s--Szekeres Happy Ending problem', '6.38', 67),
    (59, '59. Subsets of the grid with no isosceles triangles', 'Subsets of the grid with no isosceles triangles', '6.39', 67),
    (60, '60. The no 5 on a sphere problem', 'The no 5 on a sphere problem', '6.40', 67),
    (61, '61. The Ring Loading Problem', 'The Ring Loading Problem', '6.41', 67),
    (62, '62. The moving sofa problem', 'The moving sofa problem', '6.42', 67),
    (63, '63. The ambidextrous moving sofa problem', 'The ambidextrous moving sofa problem', '6.42', 67),
    (64, '64. The three-dimensional moving sofa problem with two perpendicular turns', 'The three-dimensional moving sofa problem with two perpendicular turns', '6.42', 67),
    (65, '65. Variant of IMO 2025, Problem 6', 'Variant of IMO 2025, Problem 6', '6.43', 67),
    (66, '66. The function guessing game', 'The function guessing game', '6.44', 67),
    (67, '67. Logic puzzles', 'Logic puzzles', '6.44', 67),
    (68, '68. Logic puzzles', 'Logic puzzles', '6.44', None),
)
EXPECTED_EXISTING_REPOSITORY_NOTEBOOK_LINKS = (
    (1, 'colabURL', 'experiments/finite_field_kakeya_problem/finite_field_kakeya.ipynb'),
    (1, 'colabURL2', 'experiments/finite_field_nikodym_problem/finite_field_nikodym.ipynb'),
    (2, 'colabURL', 'experiments/autocorrelation_problems/autocorrelation_problems.ipynb'),
    (3, 'colabURL', 'experiments/autocorrelation_problems/autocorrelation_problems.ipynb'),
    (7, 'colabURL', 'experiments/difference_bases/difference_bases.ipynb'),
    (9, 'colabURL', 'experiments/kakeya_needle_2d/kakeya_needle_2d.ipynb'),
    (10, 'colabURL', 'experiments/kakeya_needle_3d/kakeya_needle_3d.ipynb'),
    (11, 'colabURL', 'experiments/sphere_packing_uncertainty_principles/sphere_packing_uncertainty_principles.ipynb'),
    (12, 'colabURL', 'experiments/sphere_packing_uncertainty_principles/sphere_packing_uncertainty_principles.ipynb'),
    (13, 'colabURL', 'experiments/sphere_packing_uncertainty_principles/sphere_packing_uncertainty_principles.ipynb'),
    (14, 'colabURL', 'experiments/classical_inequalities/classical_inequalities.ipynb'),
    (15, 'colabURL', 'experiments/classical_inequalities/classical_inequalities.ipynb'),
    (16, 'colabURL', 'experiments/classical_inequalities/classical_inequalities.ipynb'),
    (17, 'colabURL', 'experiments/classical_inequalities/classical_inequalities.ipynb'),
    (18, 'colabURL', 'experiments/classical_inequalities/classical_inequalities.ipynb'),
    (19, 'colabURL', 'experiments/ovals_problem/ovals_problem.ipynb'),
    (27, 'colabURL', 'experiments/prime_number_theorem/prime_number_theorem.ipynb'),
    (28, 'colabURL', 'experiments/flat_polynomials/flat_polynomials.ipynb'),
    (32, 'colabURL', 'experiments/spherical_t_designs/spherical_t_designs.ipynb'),
    (33, 'colabURL', 'experiments/thomson_problem/thomson_problem.ipynb'),
    (34, 'colabURL', 'experiments/tammes_problem/tammes_problem.ipynb'),
    (35, 'colabURL', 'experiments/packing_unit_cubes/packing_unit_cubes.ipynb'),
    (46, 'colabURL', 'experiments/edges_vs_triangles/edges_vs_triangles.ipynb'),
    (53, 'colabURL', 'experiments/equidistant_points_in_convex_polygons/Equidistant_points_in_convex_polygons.ipynb'),
    (54, 'colabURL', 'experiments/kissing_cylinders/kissing_cylinders.ipynb'),
    (60, 'colabURL', 'experiments/no_5_on_a_sphere/no_5_on_a_sphere.ipynb'),
    (61, 'colabURL', 'experiments/ring_loading_problem/ring_loading_problem.ipynb'),
    (62, 'colabURL', 'experiments/the_2d_moving_sofa/the_2d_moving_sofa.ipynb'),
    (63, 'colabURL', 'experiments/the_2d_moving_sofa/the_2d_moving_sofa.ipynb'),
    (64, 'colabURL', 'experiments/the_3d_moving_sofa/the_3d_moving_sofa.ipynb'),
    (65, 'colabURL', 'experiments/imo_2025_p6/imo_2025_p6.ipynb'),
)
EXPECTED_MISSING_REPOSITORY_NOTEBOOK_LINKS = (
    (36, 'colabURL', 'experiments/packing_circles_max_sum_of_radii/packing_circles_max_sum_of_radii.ipynb'),
    (42, 'colabURL', 'experiments/sums_differences_problems/sums_differences_problem.ipynb'),
    (44, 'colabURL', 'experiments/sums_differences_problems/sums_differences_problem.ipynb'),
    (45, 'colabURL', 'experiments/finite_field_sum_product_problem/finite_field_sum_product_problem.ipynb'),
    (58, 'colabURL', 'experiments/erdos_szekeres_happy_ending_problem/erdos_szekeres_happy_ending_problem.ipynb'),
    (59, 'colabURL', 'experiments/subsets_of_the_grid_with_no_isosceles_triangles/subsets_of_the_grid_with_no_isosceles_triangles.ipynb'),
)
EXPECTED_EXTERNAL_ALPHAEVOLVE_RESULTS_COLAB_LINKS = ((4, 'colabURL'), (5, 'colabURL'), (8, 'colabURL'), (48, 'colabURL'), (49, 'colabURL'), (50, 'colabURL'))
EXPECTED_UNDER_CONSTRUCTION_NOTEBOOK_LINKS = (
    (6, 'colabURL'), (20, 'colabURL'), (21, 'colabURL'), (22, 'colabURL'),
    (23, 'colabURL'), (24, 'colabURL'), (25, 'colabURL'), (26, 'colabURL'),
    (29, 'colabURL'), (30, 'colabURL'), (31, 'colabURL'), (37, 'colabURL'),
    (38, 'colabURL'), (39, 'colabURL'), (40, 'colabURL'), (41, 'colabURL'),
    (43, 'colabURL'), (47, 'colabURL'), (51, 'colabURL'), (52, 'colabURL'),
    (55, 'colabURL'), (56, 'colabURL'), (57, 'colabURL'), (66, 'colabURL'),
    (67, 'colabURL'),
)
EXPECTED_GENERIC_COLAB_LANDING_LINKS = ((68, 'colabURL'),)
EXPECTED_UNLINKED_PINNED_NOTEBOOK_PATHS = (
    'experiments/erdos_szekeres_happy_ending_problem/happy_ending_problem.ipynb',
    'experiments/finite_field_sum_product_problem/finite_field_sum_product.ipynb',
    'experiments/packing_circles_max_sum_of_radii/packing_circle_max_sum_of_radii.ipynb',
    'experiments/subsets_of_the_grid_with_no_isosceles_triangles/no_isosceles_triangles.ipynb',
    'experiments/sums_differences_problems/sums_differences_problems.ipynb',
)
EXPECTED_STATUS_BUCKETS = {
    "world_record": (1, 2, 4, 5, 7, 8, 9, 10, 30, 32, 35, 42, 48, 49, 50, 59, 60, 61, 64),
    "former_record": (3, 36, 38, 44),
    "worse_than_record": (6, 11, 18, 27, 28, 39, 40, 43),
    "matched_optimal": (14, 15, 16, 17, 19, 29, 46, 54, 62, 63, 65, 67),
}
EXPECTED_LISTED_STATUS_COUNT = 43
EXPECTED_UNCLASSIFIED_PROBLEM_IDS = (
    12,
    13,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    31,
    33,
    34,
    37,
    41,
    45,
    47,
    51,
    52,
    53,
    55,
    56,
    57,
    58,
    66,
)
EXPECTED_STATUS_ARTIFACTS = {
    "status.json": {
        "bytes": 261,
        "sha256": "".join(
            [
                "84c1",
                "3884",
                "c9f5",
                "750d",
                "3c07",
                "ec4b",
                "05dd",
                "d909",
                "80a3",
                "b30a",
                "2fe6",
                "e3e4",
                "1a57",
                "5849",
                "f604",
                "c3ce",
            ]
        ),
        "kind": "status_bucket_json",
    },
    "status_grid.png": {
        "bytes": 139376,
        "sha256": "".join(
            [
                "6d4c",
                "dd57",
                "4274",
                "3f75",
                "56e5",
                "c030",
                "5044",
                "667b",
                "4adf",
                "c843",
                "8414",
                "7f1b",
                "b0c9",
                "9b9c",
                "8422",
                "474c",
            ]
        ),
        "kind": "status_grid_image",
    },
    "result_distribution.png": {
        "bytes": 212933,
        "sha256": "".join(
            [
                "2931",
                "6632",
                "dee0",
                "06a4",
                "19b2",
                "e7d0",
                "781f",
                "0b38",
                "67e2",
                "cc20",
                "4a35",
                "8aaa",
                "5856",
                "1e6d",
                "52c5",
                "989a",
            ]
        ),
        "kind": "result_distribution_image",
    },
}
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_COMMIT_RE = re.compile(r"[0-9a-f]{40}")


@dataclass(frozen=True)
class AlphaEvolveFollowOnProblemCoverageIssue:
    code: str
    message: str
    problem_id: int | None = None


@dataclass(frozen=True)
class AlphaEvolveFollowOnProblemCoverageValidation:
    ok: bool
    declared_problem_count: int
    listed_status_count: int
    unclassified_problem_count: int
    status_artifact_count: int
    observed_numbered_html_count: int | None
    issues: list[AlphaEvolveFollowOnProblemCoverageIssue]


def _expected_all_page_hash_records() -> list[dict[str, Any]]:
    return [
        {
            "page_id": page_id,
            "path": f"problems/{page_id}.html",
            "hosted_url": (
                "https://google-deepmind.github.io/"
                f"alphaevolve_repository_of_problems/problems/{page_id}.html"
            ),
            "raw_url": (
                "https://raw.githubusercontent.com/google-deepmind/"
                f"alphaevolve_repository_of_problems/{EXPECTED_REPOSITORY_COMMIT}/"
                f"problems/{page_id}.html"
            ),
            "bytes": byte_count,
            "sha256": sha256,
        }
        for page_id, byte_count, sha256 in EXPECTED_ALL_PAGE_HASH_INVENTORY["pages"]
    ]


def _status_bucket_for_page(page_id: int) -> str:
    if page_id in EXPECTED_EXTRA_NUMBERED_PAGE_IDS:
        return "extra_numbered_page"
    for bucket, problem_ids in EXPECTED_STATUS_BUCKETS.items():
        if page_id in problem_ids:
            return bucket
    return "not_listed_in_status_json"


def _link_status_for_page(page_id: int, key: str) -> str:
    page_ids_by_status = EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS[key]
    for status, page_ids in page_ids_by_status.items():
        if page_id in page_ids:
            return status
    return "missing"


def _notebook_metadata_by_path() -> dict[str, dict[str, Any]]:
    return {
        path: {"bytes": byte_count, "git_blob_sha": git_blob_sha}
        for path, byte_count, git_blob_sha in EXPECTED_FOLLOW_ON_NOTEBOOKS
    }


def _colab_url_for_notebook_link(status: str, notebook_path: str | None) -> str:
    if status in {"repository_notebook_path", "repository_notebook_path_not_in_pinned_tree"}:
        return (
            "https://github.com/google-deepmind/"
            f"alphaevolve_repository_of_problems/blob/main/{notebook_path}"
        )
    if status == "external_alphaevolve_results_colab":
        return (
            "https://colab.research.google.com/github/google-deepmind/"
            "alphaevolve_results/blob/master/mathematical_results.ipynb"
        )
    if status == "generic_colab_landing_page":
        return "https://colab.research.google.com/"
    return "#"


def _expected_notebook_link_records_by_page() -> dict[int, list[dict[str, Any]]]:
    notebook_metadata = _notebook_metadata_by_path()
    records_by_page: dict[int, list[dict[str, Any]]] = {page_id: [] for page_id in range(1, EXPECTED_OBSERVED_NUMBERED_HTML_COUNT + 1)}

    def append_record(
        page_id: int,
        link_field: str,
        status: str,
        notebook_path: str | None = None,
        absence_reason: str | None = None,
    ) -> None:
        metadata = notebook_metadata.get(notebook_path or "")
        records_by_page[page_id].append(
            {
                "link_field": link_field,
                "colab_url": _colab_url_for_notebook_link(status, notebook_path),
                "notebook_mapping_status": status,
                "notebook_path": notebook_path,
                "notebook_bytes": metadata["bytes"] if metadata else None,
                "notebook_git_blob_sha": metadata["git_blob_sha"] if metadata else None,
                "absence_reason": absence_reason,
            }
        )

    for page_id, link_field, notebook_path in EXPECTED_EXISTING_REPOSITORY_NOTEBOOK_LINKS:
        append_record(page_id, link_field, "repository_notebook_path", notebook_path)
    for page_id, link_field, notebook_path in EXPECTED_MISSING_REPOSITORY_NOTEBOOK_LINKS:
        append_record(
            page_id,
            link_field,
            "repository_notebook_path_not_in_pinned_tree",
            notebook_path,
            "linked_repository_notebook_path_absent_from_pinned_tree",
        )
    for page_id, link_field in EXPECTED_EXTERNAL_ALPHAEVOLVE_RESULTS_COLAB_LINKS:
        append_record(
            page_id,
            link_field,
            "external_alphaevolve_results_colab",
            None,
            "colab_link_points_to_alphaevolve_results_companion_not_follow_on_repository",
        )
    for page_id, link_field in EXPECTED_UNDER_CONSTRUCTION_NOTEBOOK_LINKS:
        append_record(
            page_id,
            link_field,
            "under_construction_placeholder",
            None,
            "colab_link_under_construction_placeholder",
        )
    for page_id, link_field in EXPECTED_GENERIC_COLAB_LANDING_LINKS:
        append_record(
            page_id,
            link_field,
            "generic_colab_landing_page",
            None,
            "generic_colab_landing_page_not_notebook",
        )
    return records_by_page


def _page_notebook_mapping_status(notebook_links: list[dict[str, Any]]) -> str:
    statuses = {str(link["notebook_mapping_status"]) for link in notebook_links}
    if statuses == {"repository_notebook_path"}:
        return "mapped_repository_notebook"
    if "repository_notebook_path_not_in_pinned_tree" in statuses:
        return "linked_repository_notebook_path_absent_from_pinned_tree"
    if "external_alphaevolve_results_colab" in statuses:
        return "external_alphaevolve_results_companion_colab"
    if "under_construction_placeholder" in statuses:
        return "colab_link_under_construction_placeholder"
    if "generic_colab_landing_page" in statuses:
        return "generic_colab_landing_page_not_notebook"
    return "unknown"


def _expected_all_page_source_inventory_rows() -> list[dict[str, Any]]:
    hash_records = {
        record["page_id"]: record
        for record in _expected_all_page_hash_records()
    }
    notebook_links_by_page = _expected_notebook_link_records_by_page()
    rows = []
    for page_id, title, title_key, paper_section, navigation_total in EXPECTED_ALL_PAGE_TITLE_SECTION_ROWS:
        hash_record = hash_records[page_id]
        notebook_links = notebook_links_by_page[page_id]
        rows.append(
            {
                "page_id": page_id,
                "problem_id": page_id if page_id in EXPECTED_PROBLEM_IDS else None,
                "declared_problem_page": page_id in EXPECTED_PROBLEM_IDS,
                "page_classification": (
                    "extra_numbered_page_duplicate_title_outside_declared_67_navigation"
                    if page_id in EXPECTED_EXTRA_NUMBERED_PAGE_IDS
                    else "declared_problem_page"
                ),
                "title": title,
                "title_key": title_key,
                "paper_section": paper_section,
                "declared_navigation_total_problems": navigation_total,
                "status_bucket": _status_bucket_for_page(page_id),
                "path": hash_record["path"],
                "hosted_url": hash_record["hosted_url"],
                "raw_url": hash_record["raw_url"],
                "bytes": hash_record["bytes"],
                "sha256": hash_record["sha256"],
                "colab_link_status": _link_status_for_page(page_id, "colab_link_status_page_ids"),
                "paper_link_status": _link_status_for_page(page_id, "paper_link_status_page_ids"),
                "notebook_mapping_status": _page_notebook_mapping_status(notebook_links),
                "notebook_links": notebook_links,
                "artifact_presence_status": "not_validated",
            }
        )
    return rows


def alphaevolve_follow_on_problem_coverage_record() -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_FOLLOW_ON_PROBLEM_COVERAGE_SCHEMA,
        "source_family": "alphaevolve_follow_on_problem_repository_coverage",
        "repository": {
            "name": EXPECTED_REPOSITORY_NAME,
            "url": EXPECTED_REPOSITORY_URL,
            "commit": EXPECTED_REPOSITORY_COMMIT,
            "snapshot_date": EXPECTED_SNAPSHOT_DATE,
            "live_update_policy": "live_repository_snapshot_required",
        },
        "coverage_scope": {
            "declared_problem_count": EXPECTED_DECLARED_PROBLEM_COUNT,
            "problem_id_range": [1, EXPECTED_DECLARED_PROBLEM_COUNT],
            "problem_ids": list(EXPECTED_PROBLEM_IDS),
            "problem_pages_declared_complete": True,
            "problem_page_access_mode": "browser_page",
            "notebook_access_mode": "colab_notebook_many_not_all",
            "notebook_inventory_complete": False,
            "notebook_mapping_complete": True,
            "page_hash_inventory_complete": True,
            "source_inventory_rows_emitted": True,
            "notebook_hash_inventory_complete": False,
            "artifact_presence_matrix_complete": False,
        },
        "numbered_page_inventory": {
            "observed_numbered_html_count": EXPECTED_OBSERVED_NUMBERED_HTML_COUNT,
            "expected_declared_problem_count": EXPECTED_DECLARED_PROBLEM_COUNT,
            "included_problem_ids": list(EXPECTED_PROBLEM_IDS),
            "extra_numbered_page_ids": list(EXPECTED_EXTRA_NUMBERED_PAGE_IDS),
            "count_reconciliation_status": "declared_67_with_extra_numbered_page_68_observed",
            "full_page_link_diagnostics_complete": True,
        },
        "page_discrepancy_diagnostics": {
            "diagnostic_scope": EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["diagnostic_scope"],
            "diagnosed_page_ids": list(EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["diagnosed_page_ids"]),
            "classification": EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["classification"],
            "classification_complete": EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["classification_complete"],
            "all_page_diagnostics_complete": EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["all_page_diagnostics_complete"],
            "resource_link_diagnostics_complete_for_diagnosed_pages": (
                EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["resource_link_diagnostics_complete_for_diagnosed_pages"]
            ),
            "duplicate_title_groups": [
                {
                    "title": group["title"],
                    "page_ids": list(group["page_ids"]),
                    "paper_section": group["paper_section"],
                }
                for group in EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["duplicate_title_groups"]
            ],
            "pages": [
                {
                    **page,
                    "hosted_url": (
                        "https://google-deepmind.github.io/"
                        f"alphaevolve_repository_of_problems/{page['path']}"
                    ),
                    "raw_url": (
                        "https://raw.githubusercontent.com/google-deepmind/"
                        f"alphaevolve_repository_of_problems/{EXPECTED_REPOSITORY_COMMIT}/{page['path']}"
                    ),
                }
                for page in EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["pages"]
            ],
        },
        "all_page_resource_link_diagnostics": {
            "diagnostic_scope": EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["diagnostic_scope"],
            "diagnosed_page_count": EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["diagnosed_page_count"],
            "resource_link_diagnostics_complete": EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS[
                "resource_link_diagnostics_complete"
            ],
            "page_hash_inventory_complete": EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS[
                "page_hash_inventory_complete"
            ],
            "colab_link_status_counts": dict(
                EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["colab_link_status_counts"]
            ),
            "colab_link_status_page_ids": {
                status: list(page_ids)
                for status, page_ids in EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS[
                    "colab_link_status_page_ids"
                ].items()
            },
            "paper_link_status_counts": dict(
                EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["paper_link_status_counts"]
            ),
            "paper_link_status_page_ids": {
                status: list(page_ids)
                for status, page_ids in EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS[
                    "paper_link_status_page_ids"
                ].items()
            },
            "navigation_total_problem_counts": dict(
                EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["navigation_total_problem_counts"]
            ),
            "missing_navigation_total_problem_page_ids": list(
                EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS[
                    "missing_navigation_total_problem_page_ids"
                ]
            ),
            "duplicate_title_groups": [
                {"title": group["title"], "page_ids": list(group["page_ids"])}
                for group in EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["duplicate_title_groups"]
            ],
            "multi_page_paper_section_groups": [
                {"paper_section": group["paper_section"], "page_ids": list(group["page_ids"])}
                for group in EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS[
                    "multi_page_paper_section_groups"
                ]
            ],
            "claim_boundary": (
                "All 68 numbered pages have resource-link diagnostics, but "
                "this does not claim notebook mapping or artifact-presence "
                "rows."
            ),
        },
        "all_page_hash_inventory": {
            "diagnostic_scope": EXPECTED_ALL_PAGE_HASH_INVENTORY["diagnostic_scope"],
            "page_count": EXPECTED_ALL_PAGE_HASH_INVENTORY["page_count"],
            "declared_problem_page_count": EXPECTED_ALL_PAGE_HASH_INVENTORY[
                "declared_problem_page_count"
            ],
            "extra_numbered_page_ids": list(
                EXPECTED_ALL_PAGE_HASH_INVENTORY["extra_numbered_page_ids"]
            ),
            "page_hash_inventory_complete": EXPECTED_ALL_PAGE_HASH_INVENTORY[
                "page_hash_inventory_complete"
            ],
            "notebook_mapping_complete": EXPECTED_ALL_PAGE_HASH_INVENTORY[
                "notebook_mapping_complete"
            ],
            "artifact_presence_matrix_complete": EXPECTED_ALL_PAGE_HASH_INVENTORY[
                "artifact_presence_matrix_complete"
            ],
            "pages": _expected_all_page_hash_records(),
            "claim_boundary": (
                "All 68 numbered raw HTML pages are byte-counted and "
                "SHA-256 pinned at the repository commit; this does not "
                "claim notebook mapping, absence reasons, or "
                "artifact-presence rows."
            ),
        },
        "all_page_source_inventory": {
            "diagnostic_scope": "all_numbered_pages_source_inventory_rows",
            "row_count": EXPECTED_OBSERVED_NUMBERED_HTML_COUNT,
            "declared_problem_page_count": EXPECTED_DECLARED_PROBLEM_COUNT,
            "extra_numbered_page_ids": list(EXPECTED_EXTRA_NUMBERED_PAGE_IDS),
            "source_inventory_rows_emitted": True,
            "page_url_hash_link_status_rows_complete": True,
            "status_bucket_membership_attached": True,
            "notebook_mapping_complete": True,
            "notebook_absence_reason_inventory_complete": True,
            "notebook_link_target_count": (
                len(EXPECTED_EXISTING_REPOSITORY_NOTEBOOK_LINKS)
                + len(EXPECTED_MISSING_REPOSITORY_NOTEBOOK_LINKS)
                + len(EXPECTED_EXTERNAL_ALPHAEVOLVE_RESULTS_COLAB_LINKS)
                + len(EXPECTED_UNDER_CONSTRUCTION_NOTEBOOK_LINKS)
                + len(EXPECTED_GENERIC_COLAB_LANDING_LINKS)
            ),
            "notebook_link_target_status_counts": {
                "repository_notebook_path": len(EXPECTED_EXISTING_REPOSITORY_NOTEBOOK_LINKS),
                "repository_notebook_path_not_in_pinned_tree": len(EXPECTED_MISSING_REPOSITORY_NOTEBOOK_LINKS),
                "external_alphaevolve_results_colab": len(EXPECTED_EXTERNAL_ALPHAEVOLVE_RESULTS_COLAB_LINKS),
                "under_construction_placeholder": len(EXPECTED_UNDER_CONSTRUCTION_NOTEBOOK_LINKS),
                "generic_colab_landing_page": len(EXPECTED_GENERIC_COLAB_LANDING_LINKS),
            },
            "unique_mapped_repository_notebook_path_count": len(
                {
                    notebook_path
                    for _, _, notebook_path in EXPECTED_EXISTING_REPOSITORY_NOTEBOOK_LINKS
                }
            ),
            "unlinked_pinned_notebook_paths": list(EXPECTED_UNLINKED_PINNED_NOTEBOOK_PATHS),
            "artifact_presence_matrix_complete": False,
            "rows": _expected_all_page_source_inventory_rows(),
            "claim_boundary": (
                "All 68 numbered pages have emitted source rows with page "
                "URLs, raw-page hashes, section ids, link-status diagnostics, "
                "status-bucket labels, notebook link mappings, and notebook "
                "absence reasons; this does not claim notebook SHA-256 hashes "
                "or prompt/verifier/initial/final/visualization artifact flags."
            ),
        },
        "notebook_inventory_link": {
            "source_manifest": EXPECTED_FOLLOW_ON_RUNTIME_ABSENCE_MANIFEST_FILE,
            "source_boundary": "alphaevolve_follow_on_runtime_absence",
            "pinned_notebook_path_count": len(EXPECTED_FOLLOW_ON_NOTEBOOKS),
            "path_inventory_status": "pinned_git_blob_inventory_recorded",
            "problem_id_mapping_complete": True,
            "sha256_inventory_complete": False,
            "absence_reason_inventory_complete": True,
            "claim_boundary": (
                "The follow-on runtime-absence record pins notebook paths and "
                "git blob ids, and the coverage rows map page-level notebook "
                "links and absence reasons, but this does not claim SHA-256 "
                "notebook hashes or cell-level artifact flags."
            ),
        },
        "status_artifacts": [
            {
                "path": path,
                "kind": metadata["kind"],
                "bytes": metadata["bytes"],
                "sha256": metadata["sha256"],
            }
            for path, metadata in EXPECTED_STATUS_ARTIFACTS.items()
        ],
        "status_buckets": {
            bucket: list(problem_ids)
            for bucket, problem_ids in EXPECTED_STATUS_BUCKETS.items()
        },
        "status_summary": {
            "listed_problem_count": EXPECTED_LISTED_STATUS_COUNT,
            "unclassified_label": "not_listed_in_status_json",
            "unclassified_problem_ids": list(EXPECTED_UNCLASSIFIED_PROBLEM_IDS),
            "unclassified_problem_count": len(EXPECTED_UNCLASSIFIED_PROBLEM_IDS),
            "bucket_semantics": "repository_status_json_explicit_buckets",
        },
        "remaining_coverage_work": [
            "validate_prompt_verifier_initial_final_visualization_flags",
        ],
    }


def validate_alphaevolve_follow_on_problem_coverage(
    recordset: object | str | Path | None = None,
) -> AlphaEvolveFollowOnProblemCoverageValidation:
    data, read_issues = _load_recordset(recordset)
    if read_issues:
        return AlphaEvolveFollowOnProblemCoverageValidation(False, 0, 0, 0, 0, None, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveFollowOnProblemCoverageIssue] = []
    if data.get("schema") != ALPHAEVOLVE_FOLLOW_ON_PROBLEM_COVERAGE_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported follow-on problem coverage schema"))
    if data.get("source_family") != "alphaevolve_follow_on_problem_repository_coverage":
        issues.append(_issue("invalid_source_family", "source_family must identify follow-on problem repository coverage"))
    _validate_repository(data.get("repository"), issues)
    declared_problem_count = _validate_coverage_scope(data.get("coverage_scope"), issues)
    observed_numbered_html_count = _validate_numbered_page_inventory(data.get("numbered_page_inventory"), issues)
    _validate_page_discrepancy_diagnostics(data.get("page_discrepancy_diagnostics"), issues)
    _validate_all_page_resource_link_diagnostics(data.get("all_page_resource_link_diagnostics"), issues)
    _validate_all_page_hash_inventory(data.get("all_page_hash_inventory"), issues)
    _validate_all_page_source_inventory(data.get("all_page_source_inventory"), issues)
    _validate_notebook_inventory_link(data.get("notebook_inventory_link"), issues)
    status_artifact_count = _validate_status_artifacts(data.get("status_artifacts"), issues)
    listed_status_count = _validate_status_buckets(data.get("status_buckets"), issues)
    unclassified_problem_count = _validate_status_summary(data.get("status_summary"), issues)
    _validate_remaining_coverage_work(data.get("remaining_coverage_work"), issues)
    return AlphaEvolveFollowOnProblemCoverageValidation(
        ok=not issues,
        declared_problem_count=declared_problem_count,
        listed_status_count=listed_status_count,
        unclassified_problem_count=unclassified_problem_count,
        status_artifact_count=status_artifact_count,
        observed_numbered_html_count=observed_numbered_html_count,
        issues=issues,
    )


def render_alphaevolve_follow_on_problem_coverage_summary(recordset: object | str | Path | None = None) -> str:
    validation = validate_alphaevolve_follow_on_problem_coverage(recordset)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve follow-on problem coverage evidence",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| declared_problem_count | {validation.declared_problem_count} |",
        f"| listed_status_count | {validation.listed_status_count} |",
        f"| unclassified_problem_count | {validation.unclassified_problem_count} |",
        f"| status_artifact_count | {validation.status_artifact_count} |",
        f"| observed_numbered_html_count | {validation.observed_numbered_html_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(
            f"- {issue.code}: {issue.message}"
            + (f" (problem {issue.problem_id})" if issue.problem_id is not None else "")
            for issue in validation.issues
        )
    return "\n".join(lines)


def _load_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveFollowOnProblemCoverageIssue]]:
    if recordset is None:
        return alphaevolve_follow_on_problem_coverage_record(), []
    if isinstance(recordset, dict):
        return dict(recordset), []
    if isinstance(recordset, (str, Path)):
        path = Path(recordset)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [_issue("read_error", f"failed to read follow-on coverage record: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"invalid follow-on coverage JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [_issue("invalid_shape", "follow-on coverage record must be a JSON object")]


def _validate_repository(value: object, issues: list[AlphaEvolveFollowOnProblemCoverageIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_repository", "repository must be an object"))
        return
    expected = {
        "name": EXPECTED_REPOSITORY_NAME,
        "url": EXPECTED_REPOSITORY_URL,
        "commit": EXPECTED_REPOSITORY_COMMIT,
        "snapshot_date": EXPECTED_SNAPSHOT_DATE,
        "live_update_policy": "live_repository_snapshot_required",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_repository_{field}", f"repository.{field} must match the pinned coverage snapshot"))
    commit = value.get("commit")
    if not isinstance(commit, str) or _COMMIT_RE.fullmatch(commit) is None:
        issues.append(_issue("invalid_repository_commit_format", "repository.commit must be a 40-character commit hash"))


def _validate_coverage_scope(value: object, issues: list[AlphaEvolveFollowOnProblemCoverageIssue]) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_coverage_scope", "coverage_scope must be an object"))
        return 0
    expected = {
        "declared_problem_count": EXPECTED_DECLARED_PROBLEM_COUNT,
        "problem_id_range": [1, EXPECTED_DECLARED_PROBLEM_COUNT],
        "problem_ids": list(EXPECTED_PROBLEM_IDS),
        "problem_pages_declared_complete": True,
        "problem_page_access_mode": "browser_page",
        "notebook_access_mode": "colab_notebook_many_not_all",
        "notebook_inventory_complete": False,
        "notebook_mapping_complete": True,
        "page_hash_inventory_complete": True,
        "source_inventory_rows_emitted": True,
        "notebook_hash_inventory_complete": False,
        "artifact_presence_matrix_complete": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            code = f"invalid_coverage_scope_{field}"
            if field.endswith("_complete") and expected_value is False:
                code = f"{field}_overclaim"
            issues.append(_issue(code, f"coverage_scope.{field} must match the current scoped coverage evidence"))
    return int(value.get("declared_problem_count")) if isinstance(value.get("declared_problem_count"), int) else 0


def _validate_numbered_page_inventory(value: object, issues: list[AlphaEvolveFollowOnProblemCoverageIssue]) -> int | None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_numbered_page_inventory", "numbered_page_inventory must be an object"))
        return None
    expected = {
        "observed_numbered_html_count": EXPECTED_OBSERVED_NUMBERED_HTML_COUNT,
        "expected_declared_problem_count": EXPECTED_DECLARED_PROBLEM_COUNT,
        "included_problem_ids": list(EXPECTED_PROBLEM_IDS),
        "extra_numbered_page_ids": list(EXPECTED_EXTRA_NUMBERED_PAGE_IDS),
        "count_reconciliation_status": "declared_67_with_extra_numbered_page_68_observed",
        "full_page_link_diagnostics_complete": True,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            code = f"invalid_numbered_page_inventory_{field}"
            if field == "full_page_link_diagnostics_complete":
                code = "full_page_link_diagnostics_overclaim"
            issues.append(_issue(code, f"numbered_page_inventory.{field} must preserve the pinned page-count boundary"))
    observed = value.get("observed_numbered_html_count")
    return observed if isinstance(observed, int) else None


def _validate_page_discrepancy_diagnostics(
    value: object,
    issues: list[AlphaEvolveFollowOnProblemCoverageIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_page_discrepancy_diagnostics", "page_discrepancy_diagnostics must be an object"))
        return
    expected = {
        "diagnostic_scope": EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["diagnostic_scope"],
        "diagnosed_page_ids": list(EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["diagnosed_page_ids"]),
        "classification": EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["classification"],
        "classification_complete": True,
        "all_page_diagnostics_complete": False,
        "resource_link_diagnostics_complete_for_diagnosed_pages": True,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            code = f"invalid_page_discrepancy_diagnostics_{field}"
            if field == "all_page_diagnostics_complete":
                code = "page_discrepancy_all_page_diagnostics_overclaim"
            issues.append(_issue(code, f"page_discrepancy_diagnostics.{field} must preserve the page-68 diagnostic boundary"))
    expected_groups = [
        {
            "title": group["title"],
            "page_ids": list(group["page_ids"]),
            "paper_section": group["paper_section"],
        }
        for group in EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["duplicate_title_groups"]
    ]
    if value.get("duplicate_title_groups") != expected_groups:
        issues.append(_issue("invalid_page_discrepancy_duplicate_title_groups", "page 67 and 68 must remain a duplicate-title diagnostic group"))
    pages = value.get("pages")
    if not isinstance(pages, list):
        issues.append(_issue("invalid_page_discrepancy_pages", "page_discrepancy_diagnostics.pages must be a list"))
        return
    pages_by_id = {
        record.get("page_id"): record
        for record in pages
        if isinstance(record, dict)
    }
    for expected_page in EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["pages"]:
        page_id = expected_page["page_id"]
        record = pages_by_id.get(page_id)
        if not isinstance(record, dict):
            issues.append(_issue("missing_page_discrepancy_page", "diagnosed page is missing", page_id))
            continue
        for field, expected_value in expected_page.items():
            if record.get(field) != expected_value:
                issues.append(
                    _issue(
                        f"invalid_page_discrepancy_page_{field}",
                        f"page {page_id} diagnostic field {field} must match the pinned source",
                        page_id,
                    )
                )
        hosted_url = record.get("hosted_url")
        raw_url = record.get("raw_url")
        if not isinstance(hosted_url, str) or f"/{expected_page['path']}" not in hosted_url:
            issues.append(_issue("invalid_page_discrepancy_hosted_url", "diagnosed page must include its hosted URL", page_id))
        if (
            not isinstance(raw_url, str)
            or EXPECTED_REPOSITORY_COMMIT not in raw_url
            or f"/{expected_page['path']}" not in raw_url
        ):
            issues.append(_issue("invalid_page_discrepancy_raw_url", "diagnosed page must include its pinned raw URL", page_id))
    unexpected_page_ids = sorted(page_id for page_id in pages_by_id if page_id not in {67, 68})
    for page_id in unexpected_page_ids:
        issues.append(_issue("unexpected_page_discrepancy_page", "diagnostics are scoped only to pages 67 and 68", page_id))


def _validate_all_page_resource_link_diagnostics(
    value: object,
    issues: list[AlphaEvolveFollowOnProblemCoverageIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_all_page_resource_link_diagnostics", "all_page_resource_link_diagnostics must be an object"))
        return
    expected = {
        "diagnostic_scope": EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["diagnostic_scope"],
        "diagnosed_page_count": EXPECTED_OBSERVED_NUMBERED_HTML_COUNT,
        "resource_link_diagnostics_complete": True,
        "page_hash_inventory_complete": True,
        "colab_link_status_counts": EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["colab_link_status_counts"],
        "paper_link_status_counts": EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["paper_link_status_counts"],
        "navigation_total_problem_counts": EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["navigation_total_problem_counts"],
        "missing_navigation_total_problem_page_ids": list(
            EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["missing_navigation_total_problem_page_ids"]
        ),
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            code = f"invalid_all_page_resource_link_diagnostics_{field}"
            if field == "page_hash_inventory_complete":
                code = "invalid_all_page_resource_link_page_hash_inventory_complete"
            issues.append(_issue(code, f"all_page_resource_link_diagnostics.{field} must match the pinned all-page link evidence"))
    expected_colab_ids = {
        status: list(page_ids)
        for status, page_ids in EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS[
            "colab_link_status_page_ids"
        ].items()
    }
    if value.get("colab_link_status_page_ids") != expected_colab_ids:
        issues.append(_issue("invalid_all_page_colab_link_status_page_ids", "all-page Colab link page-id buckets must match the pinned source"))
    expected_paper_ids = {
        status: list(page_ids)
        for status, page_ids in EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS[
            "paper_link_status_page_ids"
        ].items()
    }
    if value.get("paper_link_status_page_ids") != expected_paper_ids:
        issues.append(_issue("invalid_all_page_paper_link_status_page_ids", "all-page paper link page-id buckets must match the pinned source"))
    expected_title_groups = [
        {"title": group["title"], "page_ids": list(group["page_ids"])}
        for group in EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["duplicate_title_groups"]
    ]
    if value.get("duplicate_title_groups") != expected_title_groups:
        issues.append(_issue("invalid_all_page_duplicate_title_groups", "all-page duplicate-title groups must match the pinned source"))
    expected_section_groups = [
        {"paper_section": group["paper_section"], "page_ids": list(group["page_ids"])}
        for group in EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["multi_page_paper_section_groups"]
    ]
    if value.get("multi_page_paper_section_groups") != expected_section_groups:
        issues.append(_issue("invalid_all_page_multi_page_paper_section_groups", "multi-page paper-section groups must match the pinned source"))
    claim_boundary = value.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "does not claim" not in claim_boundary
        or "artifact-presence rows" not in claim_boundary
    ):
        issues.append(_issue("missing_all_page_resource_link_claim_boundary", "all-page link diagnostics must preserve artifact-row gaps"))


def _validate_all_page_hash_inventory(
    value: object,
    issues: list[AlphaEvolveFollowOnProblemCoverageIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_all_page_hash_inventory", "all_page_hash_inventory must be an object"))
        return
    expected = {
        "diagnostic_scope": EXPECTED_ALL_PAGE_HASH_INVENTORY["diagnostic_scope"],
        "page_count": EXPECTED_OBSERVED_NUMBERED_HTML_COUNT,
        "declared_problem_page_count": EXPECTED_DECLARED_PROBLEM_COUNT,
        "extra_numbered_page_ids": list(EXPECTED_EXTRA_NUMBERED_PAGE_IDS),
        "page_hash_inventory_complete": True,
        "notebook_mapping_complete": False,
        "artifact_presence_matrix_complete": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            code = f"invalid_all_page_hash_inventory_{field}"
            if field in {"notebook_mapping_complete", "artifact_presence_matrix_complete"}:
                code = f"all_page_hash_inventory_{field}_overclaim"
            issues.append(_issue(code, f"all_page_hash_inventory.{field} must match the pinned raw-page hash evidence"))
    pages = value.get("pages")
    if not isinstance(pages, list):
        issues.append(_issue("invalid_all_page_hash_inventory_pages", "all_page_hash_inventory.pages must be a list"))
        return
    expected_pages = {record["page_id"]: record for record in _expected_all_page_hash_records()}
    actual_pages = {
        record.get("page_id"): record
        for record in pages
        if isinstance(record, dict) and isinstance(record.get("page_id"), int)
    }
    if set(actual_pages) != set(expected_pages):
        issues.append(_issue("all_page_hash_inventory_page_id_mismatch", "all-page hash inventory must contain exactly pages 1..68"))
    for page_id, expected_page in expected_pages.items():
        record = actual_pages.get(page_id)
        if not isinstance(record, dict):
            issues.append(_issue("missing_all_page_hash_inventory_page", "page hash inventory record is missing", page_id))
            continue
        for field, expected_value in expected_page.items():
            if record.get(field) != expected_value:
                issues.append(
                    _issue(
                        f"invalid_all_page_hash_inventory_page_{field}",
                        f"page {page_id} hash inventory field {field} must match the pinned raw HTML source",
                        page_id,
                    )
                )
        sha256 = record.get("sha256")
        if not isinstance(sha256, str) or _SHA256_RE.fullmatch(sha256) is None:
            issues.append(_issue("invalid_all_page_hash_inventory_page_sha256_format", "page hash must be lowercase 64-hex", page_id))
    claim_boundary = value.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "does not claim" not in claim_boundary
        or "artifact-presence rows" not in claim_boundary
    ):
        issues.append(_issue("missing_all_page_hash_inventory_claim_boundary", "all-page hash inventory must preserve notebook and artifact-row gaps"))


def _validate_all_page_source_inventory(
    value: object,
    issues: list[AlphaEvolveFollowOnProblemCoverageIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_all_page_source_inventory", "all_page_source_inventory must be an object"))
        return
    expected = {
        "diagnostic_scope": "all_numbered_pages_source_inventory_rows",
        "row_count": EXPECTED_OBSERVED_NUMBERED_HTML_COUNT,
        "declared_problem_page_count": EXPECTED_DECLARED_PROBLEM_COUNT,
        "extra_numbered_page_ids": list(EXPECTED_EXTRA_NUMBERED_PAGE_IDS),
        "source_inventory_rows_emitted": True,
        "page_url_hash_link_status_rows_complete": True,
        "status_bucket_membership_attached": True,
        "notebook_mapping_complete": True,
        "notebook_absence_reason_inventory_complete": True,
        "notebook_link_target_count": 69,
        "notebook_link_target_status_counts": {
            "repository_notebook_path": 31,
            "repository_notebook_path_not_in_pinned_tree": 6,
            "external_alphaevolve_results_colab": 6,
            "under_construction_placeholder": 25,
            "generic_colab_landing_page": 1,
        },
        "unique_mapped_repository_notebook_path_count": 23,
        "unlinked_pinned_notebook_paths": list(EXPECTED_UNLINKED_PINNED_NOTEBOOK_PATHS),
        "artifact_presence_matrix_complete": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            code = f"invalid_all_page_source_inventory_{field}"
            if field == "artifact_presence_matrix_complete":
                code = f"all_page_source_inventory_{field}_overclaim"
            issues.append(_issue(code, f"all_page_source_inventory.{field} must match the emitted row evidence boundary"))
    rows = value.get("rows")
    if not isinstance(rows, list):
        issues.append(_issue("invalid_all_page_source_inventory_rows", "all_page_source_inventory.rows must be a list"))
        return
    expected_rows = {
        record["page_id"]: record
        for record in _expected_all_page_source_inventory_rows()
    }
    actual_rows = {
        record.get("page_id"): record
        for record in rows
        if isinstance(record, dict) and isinstance(record.get("page_id"), int)
    }
    if set(actual_rows) != set(expected_rows):
        issues.append(_issue("all_page_source_inventory_page_id_mismatch", "all-page source inventory must contain exactly pages 1..68"))
    for page_id, expected_row in expected_rows.items():
        record = actual_rows.get(page_id)
        if not isinstance(record, dict):
            issues.append(_issue("missing_all_page_source_inventory_row", "page source inventory row is missing", page_id))
            continue
        for field, expected_value in expected_row.items():
            if record.get(field) != expected_value:
                issues.append(
                    _issue(
                        f"invalid_all_page_source_inventory_row_{field}",
                        f"page {page_id} source inventory field {field} must match the pinned source row",
                        page_id,
                    )
                )
    claim_boundary = value.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "does not claim" not in claim_boundary
        or "notebook SHA-256 hashes" not in claim_boundary
        or "artifact flags" not in claim_boundary
    ):
        issues.append(_issue("missing_all_page_source_inventory_claim_boundary", "all-page source inventory must preserve notebook and artifact gaps"))


def _validate_notebook_inventory_link(value: object, issues: list[AlphaEvolveFollowOnProblemCoverageIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_notebook_inventory_link", "notebook_inventory_link must be an object"))
        return
    expected = {
        "source_manifest": EXPECTED_FOLLOW_ON_RUNTIME_ABSENCE_MANIFEST_FILE,
        "source_boundary": "alphaevolve_follow_on_runtime_absence",
        "pinned_notebook_path_count": len(EXPECTED_FOLLOW_ON_NOTEBOOKS),
        "path_inventory_status": "pinned_git_blob_inventory_recorded",
        "problem_id_mapping_complete": True,
        "sha256_inventory_complete": False,
        "absence_reason_inventory_complete": True,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            code = f"invalid_notebook_inventory_link_{field}"
            if field.endswith("_complete") and expected_value is False:
                code = f"notebook_inventory_link_{field}_overclaim"
            issues.append(_issue(code, f"notebook_inventory_link.{field} must preserve the pinned notebook-inventory boundary"))
    claim_boundary = value.get("claim_boundary")
    if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary:
        issues.append(_issue("missing_notebook_inventory_link_claim_boundary", "notebook_inventory_link must state that per-problem notebook coverage is not claimed"))


def _validate_status_artifacts(value: object, issues: list[AlphaEvolveFollowOnProblemCoverageIssue]) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_status_artifacts", "status_artifacts must be a list"))
        return 0
    records_by_path = {
        str(record.get("path")): record
        for record in value
        if isinstance(record, dict) and isinstance(record.get("path"), str)
    }
    for path, expected in EXPECTED_STATUS_ARTIFACTS.items():
        record = records_by_path.get(path)
        if record is None:
            issues.append(_issue("missing_status_artifact", f"status artifact {path} is missing"))
            continue
        if record.get("kind") != expected["kind"]:
            issues.append(_issue("invalid_status_artifact_kind", f"status artifact {path} has the wrong kind"))
        if record.get("bytes") != expected["bytes"]:
            issues.append(_issue("invalid_status_artifact_bytes", f"status artifact {path} byte count must match the pinned snapshot"))
        sha256 = record.get("sha256")
        if not isinstance(sha256, str) or _SHA256_RE.fullmatch(sha256) is None:
            issues.append(_issue("invalid_status_artifact_sha256", f"status artifact {path} must have a lowercase 64-hex digest"))
        elif sha256 != expected["sha256"]:
            issues.append(_issue("status_artifact_sha256_drift", f"status artifact {path} digest must match the pinned snapshot"))
    for path in sorted(set(records_by_path) - set(EXPECTED_STATUS_ARTIFACTS)):
        issues.append(_issue("unexpected_status_artifact", f"unexpected status artifact {path}"))
    return len(records_by_path)


def _validate_status_buckets(value: object, issues: list[AlphaEvolveFollowOnProblemCoverageIssue]) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_status_buckets", "status_buckets must be an object"))
        return 0
    listed: list[int] = []
    for bucket, expected_ids in EXPECTED_STATUS_BUCKETS.items():
        actual = value.get(bucket)
        if actual != list(expected_ids):
            issues.append(_issue("status_bucket_membership_drift", f"status_buckets.{bucket} must match the pinned status.json membership"))
        if isinstance(actual, list):
            listed.extend(problem_id for problem_id in actual if isinstance(problem_id, int))
    if set(value) != set(EXPECTED_STATUS_BUCKETS):
        issues.append(_issue("invalid_status_bucket_names", "status_buckets must contain exactly the pinned status.json bucket names"))
    duplicates = sorted(problem_id for problem_id in set(listed) if listed.count(problem_id) > 1)
    for problem_id in duplicates:
        issues.append(_issue("duplicate_status_problem_id", "problem id appears in multiple status buckets", problem_id))
    for problem_id in sorted(problem_id for problem_id in listed if problem_id not in EXPECTED_PROBLEM_IDS):
        issues.append(_issue("status_problem_id_out_of_range", "status bucket problem id is outside the declared 1..67 range", problem_id))
    if len(listed) != EXPECTED_LISTED_STATUS_COUNT:
        issues.append(_issue("invalid_listed_status_count", "listed status problem count must match the pinned status.json count"))
    return len(listed)


def _validate_status_summary(value: object, issues: list[AlphaEvolveFollowOnProblemCoverageIssue]) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_status_summary", "status_summary must be an object"))
        return 0
    expected = {
        "listed_problem_count": EXPECTED_LISTED_STATUS_COUNT,
        "unclassified_label": "not_listed_in_status_json",
        "unclassified_problem_ids": list(EXPECTED_UNCLASSIFIED_PROBLEM_IDS),
        "unclassified_problem_count": len(EXPECTED_UNCLASSIFIED_PROBLEM_IDS),
        "bucket_semantics": "repository_status_json_explicit_buckets",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_status_summary_{field}", f"status_summary.{field} must match the pinned coverage summary"))
    actual = value.get("unclassified_problem_ids")
    return len(actual) if isinstance(actual, list) else 0


def _validate_remaining_coverage_work(value: object, issues: list[AlphaEvolveFollowOnProblemCoverageIssue]) -> None:
    required = {
        "validate_prompt_verifier_initial_final_visualization_flags",
    }
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(_issue("invalid_remaining_coverage_work", "remaining_coverage_work must be a list of remaining work ids"))
        return
    for work_id in sorted(required - set(value)):
        issues.append(_issue("missing_remaining_coverage_work", f"remaining_coverage_work is missing {work_id}"))


def _issue(
    code: str,
    message: str,
    problem_id: int | None = None,
) -> AlphaEvolveFollowOnProblemCoverageIssue:
    return AlphaEvolveFollowOnProblemCoverageIssue(code, message, problem_id)
