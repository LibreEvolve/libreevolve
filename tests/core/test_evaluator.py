import shutil, tempfile
from pathlib import Path
from alphaevolve.core.evaluator import CascadeEvaluator
from alphaevolve.problems.loader import Problem

def _problem(validate_src: str):
    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(validate_src, encoding="utf-8")
    return Problem(name="t", task_description="t",
                   metrics=[{"name": "score", "primary": True, "bounds": [0.0, 1.0]}],
                   primary_metric="score", primary_bounds=(0.0, 1.0),
                   validate_path=d/"validate.py", initial_programs=[], problem_dir=d), d

# Tier 0 tests
def test_t0_no_diff_blocks():
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    try: assert CascadeEvaluator(p).evaluate("x=1", "no_diff_blocks") == -0.4
    finally: shutil.rmtree(d)

def test_t0_no_valid_changes():
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    try: assert CascadeEvaluator(p).evaluate("x=1", "no_valid_changes") == -0.3
    finally: shutil.rmtree(d)

def test_t0_search_not_found():
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    try: assert CascadeEvaluator(p).evaluate("x=1", "search_not_found") == -0.3
    finally: shutil.rmtree(d)

def test_t0_none_proceeds():
    p, d = _problem("def evaluate(c): return {'score':0.9,'is_valid':True}")
    try: assert CascadeEvaluator(p).evaluate("x=1", None) == 0.9
    finally: shutil.rmtree(d)

# Tier 1
def test_t1_syntax_error():
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    try: assert CascadeEvaluator(p).evaluate("def foo(:\n    pass", None) == -0.2
    finally: shutil.rmtree(d)

# Tier 2
def test_t2_domain_invalid():
    p, d = _problem("def evaluate(c): return {'score':0.0,'is_valid':False}")
    try: assert CascadeEvaluator(p).evaluate("x=1", None) == -0.1
    finally: shutil.rmtree(d)

def test_t2_crash():
    p, d = _problem("def evaluate(c): raise RuntimeError('boom')")
    try: assert CascadeEvaluator(p).evaluate("x=1", None) == -0.2
    finally: shutil.rmtree(d)

def test_t2_success():
    p, d = _problem("def evaluate(c): return {'score':0.42,'is_valid':True}")
    try: assert abs(CascadeEvaluator(p).evaluate("x=1", None) - 0.42) < 1e-9
    finally: shutil.rmtree(d)

def test_t2_timeout():
    p, d = _problem("import time\ndef evaluate(c): time.sleep(30); return {'score':1.0,'is_valid':True}")
    try:
        ev = CascadeEvaluator(p, timeout_sec=0.5)
        assert ev.evaluate("x=1", None) == -0.2
    finally:
        shutil.rmtree(d)

def test_t2_bad_json():
    # validate.py prints non-JSON stdout but exits 0
    p, d = _problem(
        "def evaluate(c):\n"
        "    import sys; sys.stdout.write('not-json\\n'); raise SystemExit(0)"
    )
    try:
        assert CascadeEvaluator(p).evaluate("x=1", None) == -0.2
    finally:
        shutil.rmtree(d)
