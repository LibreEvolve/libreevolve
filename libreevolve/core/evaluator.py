from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
import copy
import ctypes
import hashlib
import json, math, sys, tempfile
import os
import re
import signal
import subprocess
import time
import unicodedata
from statistics import NormalDist
from ctypes import wintypes
from dataclasses import dataclass, field
from pathlib import Path
import fnmatch
from uuid import uuid4
from libreevolve.core.candidate import (
    CandidateMaterializationError,
    CandidateWorkspace,
)
from libreevolve.core.config import MAX_EVALUATOR_STDIN_CHARS, _require_bool, _require_int, _require_positive_number, _validate_evaluator_stdin_text, _validate_artifact_glob_list, _validate_eval_stages, _validate_validator_network_policy, canonicalize_env_var_allowlist
from libreevolve.core.jsonl import strict_json_dumps
from libreevolve.core.redaction import redact_sensitive_text
from libreevolve.population.program import (
    validate_program_metadata,
    validate_program_metrics,
)
from libreevolve.problems.loader import Problem

_PENALTIES = {
    "no_diff_blocks": -0.4,
    "non_text_mutation_payload": -0.4,
    "blank_mutation_payload": -0.4,
    "oversized_mutation_payload": -0.4,
    "no_valid_changes": -0.3,
    "search_not_found": -0.3,
    "ambiguous_search_match": -0.3,
    "malformed_proposal_metadata:multiline_continuation": -0.4,
    "malformed_proposal_metadata:unterminated_section": -0.4,
}
_DIFF_ERROR_DETAIL_MAX_CHARS = 500
_DEFAULT_VALIDATOR_ENV_NAMES = ("SYSTEMROOT", "WINDIR", "TEMP", "TMP")
_PREFLIGHT_TIMEOUT_SEC = 5.0
_DEFAULT_EVALUATOR_OUTPUT_MAX_CHARS = 20_000
_EVALUATION_RESULT_TEXT_MAX_CHARS = 1_000_000
_TIMEOUT_CLEANUP_OUTPUT_MAX_CHARS = 2_000
MAX_ARTIFACT_CONTENT_EXCERPT_CHARS = 300
_PROCESS_TERMINATE = 0x0001
_JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
_JobObjectExtendedLimitInformation = 9


class _JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_int64),
        ("PerJobUserTimeLimit", ctypes.c_int64),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class _IO_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_uint64),
        ("WriteOperationCount", ctypes.c_uint64),
        ("OtherOperationCount", ctypes.c_uint64),
        ("ReadTransferCount", ctypes.c_uint64),
        ("WriteTransferCount", ctypes.c_uint64),
        ("OtherTransferCount", ctypes.c_uint64),
    ]


class _JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("IoInfo", _IO_COUNTERS),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]
_EVALUATOR_PROGRAM_OUTPUT_MAX_JSON_CHARS = 4_000
_ACCOUNTING_KEYS = (
    "subprocess_attempts",
    "configured_stage_samples",
    "retry_attempts",
    "timeout_count",
    "sample_budget_exhaustions",
    "stage_budget_exhaustions",
)

# Runner script executed in a temporary local subprocess. This is process
# separation, not a security sandbox.
# Uses importlib to load validate.py and calls evaluate(code). The evaluator
# return value is written to a runner-owned result file so stdout/stderr remain
# diagnostic-only channels.
_RUNNER = (
    "import sys,json,importlib.util,inspect,os,math,builtins,io\n"
    "sys.dont_write_bytecode=True\n"
    "def _install_network_policy():\n"
    "    _policy=os.environ.get('LIBREEVOLVE_VALIDATOR_NETWORK_POLICY','host')\n"
    "    if _policy!='deny': return\n"
    "    import socket as _socket\n"
    "    def _deny(*args,**kwargs):\n"
    "        raise OSError('validator network egress denied by libreevolve python_socket policy')\n"
    "    _socket.socket=_deny\n"
    "    _socket.create_connection=_deny\n"
    "    _socket.getaddrinfo=_deny\n"
    "    _socket.gethostbyname=_deny\n"
    "    _socket.gethostbyname_ex=_deny\n"
    "    _socket.gethostbyaddr=_deny\n"
    "    _socket.getnameinfo=_deny\n"
    "_install_network_policy()\n"
    "workspace=sys.argv[3]\n"
    "result_path=sys.argv[5]\n"
    "problem_root=os.path.abspath(sys.argv[6])\n"
    "allowed_problem_files={os.path.abspath(item) for item in json.loads(sys.argv[7])}\n"
    "with open(sys.argv[4],encoding='utf-8') as _stage_handle:\n"
    "    stage=json.load(_stage_handle)\n"
    "_rng_seed=stage.get('rng_seed') if isinstance(stage,dict) else None\n"
    "if _rng_seed is not None:\n"
    "    import random\n"
    "    _rng_seed=int(_rng_seed)\n"
    "    random.seed(_rng_seed)\n"
    "    try:\n"
    "        import numpy as _np\n"
    "        _np.random.seed(_rng_seed)\n"
    "    except Exception:\n"
    "        pass\n"
    "entrypoint=os.path.abspath(sys.argv[1])\n"
    "validate_dir=os.path.dirname(entrypoint)\n"
    "allowed_problem_files.add(entrypoint)\n"
    "is_package=os.path.basename(entrypoint)=='__init__.py'\n"
    "for path in (workspace, problem_root if is_package else '', validate_dir):\n"
    "    if path and path not in sys.path: sys.path.insert(0,path)\n"
    "os.chdir(workspace)\n"
    "def _within(path,root):\n"
    "    try:\n"
    "        return os.path.commonpath([os.path.abspath(path),root])==root\n"
    "    except ValueError:\n"
    "        return False\n"
    "def _path_arg(value):\n"
    "    if isinstance(value,int): return None\n"
    "    try:\n"
    "        return os.path.abspath(os.fsdecode(os.fspath(value)))\n"
    "    except (TypeError,ValueError,OSError):\n"
    "        return None\n"
    "def _problem_scope_violation(path):\n"
    "    if path is None: return None\n"
    "    resolved=os.path.abspath(path)\n"
    "    if not _within(resolved,problem_root): return None\n"
    "    if resolved in allowed_problem_files: return None\n"
    "    return os.path.relpath(resolved,problem_root)\n"
    "_real_open=builtins.open\n"
    "_real_io_open=io.open\n"
    "def _checked_open(file,*args,**kwargs):\n"
    "    violation=_problem_scope_violation(_path_arg(file))\n"
    "    if violation is not None:\n"
    "        raise PermissionError('problem-local evaluator dependency is not in declared provenance: '+violation)\n"
    "    return _real_open(file,*args,**kwargs)\n"
    "def _checked_io_open(file,*args,**kwargs):\n"
    "    violation=_problem_scope_violation(_path_arg(file))\n"
    "    if violation is not None:\n"
    "        raise PermissionError('problem-local evaluator dependency is not in declared provenance: '+violation)\n"
    "    return _real_io_open(file,*args,**kwargs)\n"
    "builtins.open=_checked_open\n"
    "io.open=_checked_io_open\n"
    "def _enforce_problem_module_scope():\n"
    "    for _name,_module in list(sys.modules.items()):\n"
    "        violation=_problem_scope_violation(_path_arg(getattr(_module,'__file__',None)))\n"
    "        if violation is not None:\n"
    "            raise PermissionError('problem-local evaluator module is not in declared provenance: '+violation)\n"
    "def _module_name(entrypoint, problem_root):\n"
    "    if os.path.basename(entrypoint)!='__init__.py': return 'v'\n"
    "    rel=os.path.relpath(os.path.dirname(entrypoint), problem_root)\n"
    "    parts=[] if rel=='.' else rel.split(os.sep)\n"
    "    if not parts or any(not part.isidentifier() for part in parts):\n"
    "        return '_libreevolve_validator_package'\n"
    "    return '.'.join(parts)\n"
    "module_name=_module_name(entrypoint, problem_root)\n"
    "submodules=[validate_dir] if is_package else None\n"
    "spec=importlib.util.spec_from_file_location(module_name,entrypoint,submodule_search_locations=submodules)\n"
    "mod=importlib.util.module_from_spec(spec);sys.modules[module_name]=mod;spec.loader.exec_module(mod)\n"
    "_enforce_problem_module_scope()\n"
    "code=open(sys.argv[2],encoding='utf-8').read()\n"
    "params=inspect.signature(mod.evaluate).parameters\n"
    "result=mod.evaluate(code, workspace, stage) if len(params) >= 3 else (mod.evaluate(code, workspace) if len(params) >= 2 else mod.evaluate(code))\n"
    "_enforce_problem_module_scope()\n"
    "def _validate_json_value(value,path='$',active=None,depth=0,max_depth=100):\n"
    "    if depth > max_depth:\n"
    "        raise ValueError(f'JSON nesting exceeds maximum depth at {path}')\n"
    "    if isinstance(value,float) and not math.isfinite(value):\n"
    "        raise ValueError('Out of range float values are not JSON compliant')\n"
    "    if isinstance(value,dict):\n"
    "        active = set() if active is None else active\n"
    "        obj_id=id(value)\n"
    "        if obj_id in active:\n"
    "            raise ValueError(f'Circular reference detected at {path}')\n"
    "        active.add(obj_id)\n"
    "        try:\n"
    "            key_types=sorted({type(key).__name__ for key in value.keys() if not isinstance(key,str)})\n"
    "            if key_types:\n"
    "                raise TypeError('evaluator result keys must be strings; non_string_key_types='+','.join(key_types))\n"
    "            for key,item in value.items():\n"
    "                child = path + '.' + key.replace('\\\\','\\\\\\\\').replace('.', '\\\\.')\n"
    "                _validate_json_value(item,child,active,depth+1,max_depth)\n"
    "        finally:\n"
    "            active.remove(obj_id)\n"
    "        return\n"
    "    if isinstance(value,tuple):\n"
    "        raise TypeError(f'JSON value at {path} must use list, not tuple')\n"
    "    if isinstance(value,list):\n"
    "        active = set() if active is None else active\n"
    "        obj_id=id(value)\n"
    "        if obj_id in active:\n"
    "            raise ValueError(f'Circular reference detected at {path}')\n"
    "        active.add(obj_id)\n"
    "        try:\n"
    "            for index,item in enumerate(value):\n"
    "                _validate_json_value(item,f'{path}[{index}]',active,depth+1,max_depth)\n"
    "        finally:\n"
    "            active.remove(obj_id)\n"
    "try:\n"
    "    _validate_json_value(result)\n"
    "    payload=json.dumps({'ok':True,'result':result},allow_nan=False)\n"
    "except (TypeError,ValueError) as exc:\n"
    "    payload=json.dumps({'ok':False,'error':'result_not_json_serializable','message':str(exc)})\n"
    "with open(result_path,'w',encoding='utf-8') as handle:\n"
    "    handle.write(payload)\n"
)

_EMBEDDED_EVALUATE_RUNNER = (
    "import sys,json,importlib.util,inspect,os,math\n"
    "sys.dont_write_bytecode=True\n"
    "def _install_network_policy():\n"
    "    _policy=os.environ.get('LIBREEVOLVE_VALIDATOR_NETWORK_POLICY','host')\n"
    "    if _policy!='deny': return\n"
    "    import socket as _socket\n"
    "    def _deny(*args,**kwargs):\n"
    "        raise OSError('candidate evaluate network egress denied by libreevolve python_socket policy')\n"
    "    _socket.socket=_deny\n"
    "    _socket.create_connection=_deny\n"
    "    _socket.getaddrinfo=_deny\n"
    "    _socket.gethostbyname=_deny\n"
    "    _socket.gethostbyname_ex=_deny\n"
    "    _socket.gethostbyaddr=_deny\n"
    "    _socket.getnameinfo=_deny\n"
    "_install_network_policy()\n"
    "workspace=os.path.abspath(sys.argv[1])\n"
    "primary_path=os.path.abspath(sys.argv[2])\n"
    "stage=json.loads(sys.argv[3])\n"
    "result_path=sys.argv[4]\n"
    "allowed_workspace_files={os.path.abspath(item) for item in json.loads(sys.argv[5])}\n"
    "allowed_workspace_files.add(primary_path)\n"
    "_rng_seed=stage.get('rng_seed') if isinstance(stage,dict) else None\n"
    "if _rng_seed is not None:\n"
    "    import random\n"
    "    _rng_seed=int(_rng_seed)\n"
    "    random.seed(_rng_seed)\n"
    "    try:\n"
    "        import numpy as _np\n"
    "        _np.random.seed(_rng_seed)\n"
    "    except Exception:\n"
    "        pass\n"
    "def _emit(ok,result=None,error='',message=''):\n"
    "    payload={'ok':ok}\n"
    "    if ok: payload['result']=result\n"
    "    else:\n"
    "        payload['error']=error or 'candidate_evaluate_error'\n"
    "        payload['message']=message or payload['error']\n"
    "    with open(result_path,'w',encoding='utf-8') as handle:\n"
    "        handle.write(json.dumps(payload,allow_nan=False))\n"
    "os.chdir(workspace)\n"
    "if workspace not in sys.path: sys.path.insert(0,workspace)\n"
    "def _within(path,root):\n"
    "    try:\n"
    "        return os.path.commonpath([os.path.abspath(path),root])==root\n"
    "    except ValueError:\n"
    "        return False\n"
    "def _path_arg(value):\n"
    "    if isinstance(value,int): return None\n"
    "    try:\n"
    "        return os.path.abspath(os.fsdecode(os.fspath(value)))\n"
    "    except (TypeError,ValueError,OSError):\n"
    "        return None\n"
    "def _workspace_scope_violation(path):\n"
    "    if path is None: return None\n"
    "    resolved=os.path.abspath(path)\n"
    "    if not _within(resolved,workspace): return None\n"
    "    if resolved in allowed_workspace_files: return None\n"
    "    return os.path.relpath(resolved,workspace)\n"
    "def _read_mode(args,kwargs):\n"
    "    mode=kwargs.get('mode', args[0] if args else 'r')\n"
    "    if not isinstance(mode,str): return True\n"
    "    return 'r' in mode or '+' in mode\n"
    "import builtins,io\n"
    "_real_open=builtins.open\n"
    "_real_io_open=io.open\n"
    "def _checked_open(file,*args,**kwargs):\n"
    "    violation=_workspace_scope_violation(_path_arg(file)) if _read_mode(args,kwargs) else None\n"
    "    if violation is not None:\n"
    "        raise PermissionError('candidate workspace file is not in materialized candidate manifest: '+violation)\n"
    "    return _real_open(file,*args,**kwargs)\n"
    "def _checked_io_open(file,*args,**kwargs):\n"
    "    violation=_workspace_scope_violation(_path_arg(file)) if _read_mode(args,kwargs) else None\n"
    "    if violation is not None:\n"
    "        raise PermissionError('candidate workspace file is not in materialized candidate manifest: '+violation)\n"
    "    return _real_io_open(file,*args,**kwargs)\n"
    "builtins.open=_checked_open\n"
    "io.open=_checked_io_open\n"
    "def _enforce_workspace_module_scope():\n"
    "    for _name,_module in list(sys.modules.items()):\n"
    "        violation=_workspace_scope_violation(_path_arg(getattr(_module,'__file__',None)))\n"
    "        if violation is not None:\n"
    "            raise PermissionError('candidate workspace module is not in materialized candidate manifest: '+violation)\n"
    "try:\n"
    "    spec=importlib.util.spec_from_file_location('_libreevolve_candidate_embedded_evaluate',primary_path)\n"
    "    if spec is None or spec.loader is None:\n"
    "        _emit(False,error='candidate_import_error',message='candidate primary module could not be imported')\n"
    "        sys.exit(0)\n"
    "    mod=importlib.util.module_from_spec(spec)\n"
    "    sys.modules[spec.name]=mod\n"
    "    spec.loader.exec_module(mod)\n"
    "    _enforce_workspace_module_scope()\n"
    "    func=getattr(mod,'evaluate',None)\n"
    "    if not callable(func):\n"
    "        _emit(False,error='missing_candidate_evaluate',message='candidate primary module must define callable evaluate(eval_inputs)')\n"
    "        sys.exit(0)\n"
    "    signature=inspect.signature(func)\n"
    "    params=list(signature.parameters.values())\n"
    "    allowed=(inspect.Parameter.POSITIONAL_ONLY,inspect.Parameter.POSITIONAL_OR_KEYWORD)\n"
    "    if len(params)!=1 or params[0].kind not in allowed:\n"
    "        _emit(False,error='unsupported_candidate_evaluate_signature',message=f'candidate evaluate must have signature evaluate(eval_inputs), got {signature}')\n"
    "        sys.exit(0)\n"
    "    result=func(stage.get('eval_inputs',{}))\n"
    "    _enforce_workspace_module_scope()\n"
    "except Exception as exc:\n"
    "    _emit(False,error='candidate_evaluate_error',message=f'{exc.__class__.__name__}: {exc}')\n"
    "    sys.exit(0)\n"
    "def _validate_json_value(value,path='$',active=None,depth=0,max_depth=100):\n"
    "    if depth > max_depth:\n"
    "        raise ValueError(f'JSON nesting exceeds maximum depth at {path}')\n"
    "    if isinstance(value,float) and not math.isfinite(value):\n"
    "        raise ValueError('Out of range float values are not JSON compliant')\n"
    "    if isinstance(value,dict):\n"
    "        active = set() if active is None else active\n"
    "        obj_id=id(value)\n"
    "        if obj_id in active:\n"
    "            raise ValueError(f'Circular reference detected at {path}')\n"
    "        active.add(obj_id)\n"
    "        try:\n"
    "            key_types=sorted({type(key).__name__ for key in value.keys() if not isinstance(key,str)})\n"
    "            if key_types:\n"
    "                raise TypeError('evaluator result keys must be strings; non_string_key_types='+','.join(key_types))\n"
    "            for key,item in value.items():\n"
    "                child = path + '.' + key.replace('\\\\','\\\\\\\\').replace('.', '\\\\.')\n"
    "                _validate_json_value(item,child,active,depth+1,max_depth)\n"
    "        finally:\n"
    "            active.remove(obj_id)\n"
    "        return\n"
    "    if isinstance(value,tuple):\n"
    "        raise TypeError(f'JSON value at {path} must use list, not tuple')\n"
    "    if isinstance(value,list):\n"
    "        active = set() if active is None else active\n"
    "        obj_id=id(value)\n"
    "        if obj_id in active:\n"
    "            raise ValueError(f'Circular reference detected at {path}')\n"
    "        active.add(obj_id)\n"
    "        try:\n"
    "            for index,item in enumerate(value):\n"
    "                _validate_json_value(item,f'{path}[{index}]',active,depth+1,max_depth)\n"
    "        finally:\n"
    "            active.remove(obj_id)\n"
    "try:\n"
    "    _validate_json_value(result)\n"
    "    _emit(True,result=result)\n"
    "except (TypeError,ValueError) as exc:\n"
    "    _emit(False,error='result_not_json_serializable',message=str(exc))\n"
)

_WINDOWS_VALIDATOR_BOOTSTRAP = (
    "import os,runpy,sys,time\n"
    "release=os.environ.pop('LIBREEVOLVE_VALIDATOR_RELEASE', '')\n"
    "deadline=time.monotonic()+10.0\n"
    "while release and not os.path.exists(release) and time.monotonic()<deadline:\n"
    "    time.sleep(0.005)\n"
    "if release and not os.path.exists(release):\n"
    "    raise SystemExit('validator release timeout')\n"
    "script=sys.argv[1]\n"
    "sys.argv=sys.argv[1:]\n"
    "runpy.run_path(script, run_name='__main__')\n"
)

_PREFLIGHT_RUNNER = (
    "import sys,json,importlib.util,inspect,os,builtins,io\n"
    "sys.dont_write_bytecode=True\n"
    "def _install_network_policy():\n"
    "    _policy=os.environ.get('LIBREEVOLVE_VALIDATOR_NETWORK_POLICY','host')\n"
    "    if _policy!='deny': return\n"
    "    import socket as _socket\n"
    "    def _deny(*args,**kwargs):\n"
    "        raise OSError('validator network egress denied by libreevolve python_socket policy')\n"
    "    _socket.socket=_deny\n"
    "    _socket.create_connection=_deny\n"
    "    _socket.getaddrinfo=_deny\n"
    "    _socket.gethostbyname=_deny\n"
    "    _socket.gethostbyname_ex=_deny\n"
    "    _socket.gethostbyaddr=_deny\n"
    "    _socket.getnameinfo=_deny\n"
    "_install_network_policy()\n"
    "path=sys.argv[1]\n"
    "problem_root=os.path.abspath(sys.argv[2])\n"
    "allowed_problem_files={os.path.abspath(item) for item in json.loads(sys.argv[3])}\n"
    "def emit(ok,message=''):\n"
    "    print(json.dumps({'ok':ok,'message':message}))\n"
    "    sys.exit(0 if ok else 1)\n"
    "entrypoint=os.path.abspath(path)\n"
    "validate_dir=os.path.dirname(entrypoint)\n"
    "allowed_problem_files.add(entrypoint)\n"
    "is_package=os.path.basename(entrypoint)=='__init__.py'\n"
    "for candidate in (problem_root if is_package else '', validate_dir):\n"
    "    if candidate and candidate not in sys.path: sys.path.insert(0,candidate)\n"
    "def _within(candidate,root):\n"
    "    try:\n"
    "        return os.path.commonpath([os.path.abspath(candidate),root])==root\n"
    "    except ValueError:\n"
    "        return False\n"
    "def _path_arg(value):\n"
    "    if isinstance(value,int): return None\n"
    "    try:\n"
    "        return os.path.abspath(os.fsdecode(os.fspath(value)))\n"
    "    except (TypeError,ValueError,OSError):\n"
    "        return None\n"
    "def _problem_scope_violation(candidate):\n"
    "    if candidate is None: return None\n"
    "    resolved=os.path.abspath(candidate)\n"
    "    if not _within(resolved,problem_root): return None\n"
    "    if resolved in allowed_problem_files: return None\n"
    "    return os.path.relpath(resolved,problem_root)\n"
    "_real_open=builtins.open\n"
    "_real_io_open=io.open\n"
    "def _checked_open(file,*args,**kwargs):\n"
    "    violation=_problem_scope_violation(_path_arg(file))\n"
    "    if violation is not None:\n"
    "        raise PermissionError('problem-local evaluator dependency is not in declared provenance: '+violation)\n"
    "    return _real_open(file,*args,**kwargs)\n"
    "def _checked_io_open(file,*args,**kwargs):\n"
    "    violation=_problem_scope_violation(_path_arg(file))\n"
    "    if violation is not None:\n"
    "        raise PermissionError('problem-local evaluator dependency is not in declared provenance: '+violation)\n"
    "    return _real_io_open(file,*args,**kwargs)\n"
    "builtins.open=_checked_open\n"
    "io.open=_checked_io_open\n"
    "def _enforce_problem_module_scope():\n"
    "    for _name,_module in list(sys.modules.items()):\n"
    "        violation=_problem_scope_violation(_path_arg(getattr(_module,'__file__',None)))\n"
    "        if violation is not None:\n"
    "            raise PermissionError('problem-local evaluator module is not in declared provenance: '+violation)\n"
    "def _module_name(entrypoint, problem_root):\n"
    "    if os.path.basename(entrypoint)!='__init__.py': return '_libreevolve_validator_preflight'\n"
    "    rel=os.path.relpath(os.path.dirname(entrypoint), problem_root)\n"
    "    parts=[] if rel=='.' else rel.split(os.sep)\n"
    "    if not parts or any(not part.isidentifier() for part in parts):\n"
    "        return '_libreevolve_validator_package_preflight'\n"
    "    return '.'.join(parts)\n"
    "module_name=_module_name(entrypoint, problem_root)\n"
    "submodules=[validate_dir] if is_package else None\n"
    "spec=importlib.util.spec_from_file_location(module_name,entrypoint,submodule_search_locations=submodules)\n"
    "if spec is None or spec.loader is None: emit(False,'cannot load module')\n"
    "module=importlib.util.module_from_spec(spec)\n"
    "try:\n"
    "    sys.modules[module_name]=module\n"
    "    spec.loader.exec_module(module)\n"
    "    _enforce_problem_module_scope()\n"
    "except SyntaxError as exc:\n"
    "    emit(False,f'syntax error: {exc}')\n"
    "except Exception as exc:\n"
    "    emit(False,f'import failed: {exc}')\n"
    "evaluate=getattr(module,'evaluate',None)\n"
    "if not callable(evaluate): emit(False,'missing callable evaluate')\n"
    "if inspect.iscoroutinefunction(evaluate):\n"
    "    emit(False,'async evaluate functions are unsupported')\n"
    "if inspect.isgeneratorfunction(evaluate) or inspect.isasyncgenfunction(evaluate):\n"
    "    emit(False,'generator evaluate functions are unsupported')\n"
    "try:\n"
    "    signature=inspect.signature(evaluate)\n"
    "except (TypeError,ValueError):\n"
    "    emit(False,'cannot inspect evaluate signature')\n"
    "parameters=list(signature.parameters.values())\n"
    "bad_kind={inspect.Parameter.VAR_POSITIONAL,inspect.Parameter.VAR_KEYWORD,inspect.Parameter.KEYWORD_ONLY}\n"
    "if len(parameters) not in {1,2,3} or any(parameter.kind in bad_kind for parameter in parameters):\n"
    "    emit(False,f'unsupported evaluate signature {signature}')\n"
    "param_count=len(parameters)\n"
    "arg_count=3 if param_count >= 3 else (2 if param_count >= 2 else 1)\n"
    "try:\n"
    "    signature.bind(*([None]*arg_count))\n"
    "except TypeError:\n"
    "    emit(False,f'unsupported evaluate signature {signature}')\n"
    "emit(True)\n"
)


class CascadeEvaluator:
    """Local staged evaluator with a default diff/syntax/subprocess cascade.

    Inspired by staged evaluation and lazy-penalty ideas in adjacent systems.
    This local implementation supports configured validator stages, samples,
    retries, thresholds, and artifact collection, but is not a reproduction of
    AlphaEvolve's distributed evaluator workers.
    """

    def __init__(
        self,
        problem: Problem,
        timeout_sec: float = 60.0,
        stages: list[dict] | None = None,
        validator_env_allowlist: list[str] | None = None,
        artifact_dir: Path | None = None,
        artifact_include: list[str] | None = None,
        artifact_exclude: list[str] | None = None,
        artifact_max_files: int = 20,
        artifact_max_bytes: int = 1_000_000,
        artifact_redact_secrets: bool = True,
        data_include: list[str] | None = None,
        data_exclude: list[str] | None = None,
        output_max_chars: int = _DEFAULT_EVALUATOR_OUTPUT_MAX_CHARS,
        stdin_text: str | None = None,
        stdin_file: str | Path | None = None,
        validator_network_policy: str = "host",
    ):
        stage_specs = copy.deepcopy(stages or [])
        _validate_eval_stages(stage_specs)
        _require_positive_number("timeout_sec", timeout_sec)
        top_level_artifact_include = [] if artifact_include is None else artifact_include
        top_level_artifact_exclude = [] if artifact_exclude is None else artifact_exclude
        top_level_data_include = [] if data_include is None else data_include
        top_level_data_exclude = [] if data_exclude is None else data_exclude
        _validate_artifact_glob_list("artifact_include", top_level_artifact_include)
        _validate_artifact_glob_list("artifact_exclude", top_level_artifact_exclude)
        _validate_artifact_glob_list("data_include", top_level_data_include)
        _validate_artifact_glob_list("data_exclude", top_level_data_exclude)
        _require_int("artifact_max_files", artifact_max_files, minimum=0)
        _require_int("artifact_max_bytes", artifact_max_bytes, minimum=0)
        _require_bool("artifact_redact_secrets", artifact_redact_secrets)
        self._problem = problem
        self._timeout = float(timeout_sec)
        self._stages = stage_specs
        self._validator_env_allowlist = canonicalize_env_var_allowlist(
            "validator_env_allowlist",
            validator_env_allowlist or [],
        )
        self._validator_network_policy = _validate_validator_network_policy(
            validator_network_policy
        )
        self._artifact_dir = artifact_dir
        self._artifact_include = list(top_level_artifact_include)
        self._artifact_exclude = list(top_level_artifact_exclude)
        self._artifact_max_files = artifact_max_files
        self._artifact_max_bytes = artifact_max_bytes
        self._artifact_redact_secrets = artifact_redact_secrets
        self._data_include = list(top_level_data_include)
        self._data_exclude = list(top_level_data_exclude)
        if isinstance(output_max_chars, bool) or not isinstance(output_max_chars, int) or output_max_chars < 0:
            raise ValueError("output_max_chars must be an integer >= 0")
        self._output_max_chars = output_max_chars
        _validate_evaluator_stdin_text("stdin_text", stdin_text)
        self._stdin_text = stdin_text
        self._stdin_file = None if stdin_file is None else str(stdin_file)
        self._preflight_validated = False

    def evaluate(
        self, code: str | CandidateWorkspace, diff_error: object | None
    ) -> "EvaluationResult":
        workspace = code if isinstance(code, CandidateWorkspace) else CandidateWorkspace.from_code(code)
        if diff_error is not None:
            diff_reason, score, diff_metadata = _normalize_diff_error(diff_error)
            metrics = _synthetic_failure_metrics(self._problem, score)
            synthetic_metadata = _synthetic_failure_metric_metadata(self._problem, score)
            return EvaluationResult(
                fitness=score,
                metrics=metrics,
                is_valid=False,
                stages=[
                    EvaluationStageResult(
                        name="diff",
                        passed=False,
                        score=score,
                        metrics=metrics,
                        error=diff_reason,
                        metadata={"diff_error": diff_metadata},
                    )
                ],
                error=diff_reason,
                metadata={
                    "primary_file": workspace.primary_file,
                    "files": sorted(workspace.files),
                    "diff_error": diff_metadata,
                    "synthetic_metrics": synthetic_metadata,
                },
            )
        syntax_errors = _syntax_errors(workspace)
        if syntax_errors:
            syntax_error = "; ".join(error["summary"] for error in syntax_errors)
            metrics = _synthetic_failure_metrics(self._problem, -0.2)
            return EvaluationResult(
                fitness=-0.2,
                metrics=metrics,
                is_valid=False,
                stages=[
                    EvaluationStageResult(
                        name="syntax",
                        passed=False,
                        score=-0.2,
                        metrics=metrics,
                        error=syntax_error,
                    )
                ],
                error="syntax_error",
                metadata={
                    "primary_file": workspace.primary_file,
                    "files": sorted(workspace.files),
                    "syntax_errors": syntax_errors,
                    "synthetic_metrics": _synthetic_failure_metric_metadata(self._problem, -0.2),
                },
            )
        syntax_stage = EvaluationStageResult(name="syntax", passed=True)
        self._preflight_contracts_once()
        if self._stages:
            return self._run_configured_stages(workspace, syntax_stage)
        result = self._run_subprocess(workspace, stage_name="validate", timeout_sec=self._timeout)
        result.stages.insert(0, syntax_stage)
        return result

    def _preflight_contracts_once(self) -> None:
        if self._preflight_validated:
            return
        preflight_evaluator_contracts(
            self._problem,
            self._stages,
            validator_env_allowlist=self._validator_env_allowlist,
            validator_network_policy=self._validator_network_policy,
            evaluator_data_include=self._data_include,
            evaluator_data_exclude=self._data_exclude,
        )
        self._preflight_validated = True

    def _run_configured_stages(
        self, workspace: CandidateWorkspace, syntax_stage: "EvaluationStageResult"
    ) -> "EvaluationResult":
        stages = [syntax_stage]
        configured_stage_results: list[dict] = []
        last: EvaluationResult | None = None
        for index, stage in enumerate(self._stages):
            name = str(stage.get("name", f"stage_{index}"))
            result = self._run_stage(workspace, stage, stage_index=index, stage_name=name)
            stages.extend(result.stages)
            last = result
            min_score = stage.get("min_score")
            threshold_result = _stage_threshold_result(
                result,
                min_score,
                stage.get("metric_thresholds"),
                stage,
            )
            threshold_passed = threshold_result["passed"]
            hypothesis_test_result = _stage_hypothesis_test_result(
                result,
                stage.get("hypothesis_test"),
            )
            passed = (
                result.is_valid
                and threshold_passed
                and hypothesis_test_result["passed"]
            )
            configured_stage_results.append(
                _configured_stage_result_record(
                    name=name,
                    stage_index=index,
                    result=result,
                    min_score=min_score,
                    threshold_passed=threshold_passed,
                    threshold_result=threshold_result,
                    hypothesis_test_result=hypothesis_test_result,
                    passed=passed,
                )
            )
            if not passed:
                stop_reason = result.error or (
                    "hypothesis_test_not_met"
                    if hypothesis_test_result["configured"]
                    and not hypothesis_test_result["passed"]
                    else "stage_threshold_not_met"
                )
                configured_stage_results[-1]["stop_reason"] = stop_reason
                return EvaluationResult(
                    fitness=result.fitness,
                    metrics=result.metrics,
                    is_valid=False,
                    stages=stages,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    error=stop_reason,
                    elapsed_sec=sum(s.elapsed_sec for s in stages),
                    metadata={
                        **result.metadata,
                        "stopped_at": name,
                        "configured_stage_results": configured_stage_results,
                    },
                )
        assert last is not None
        last.stages = stages
        last.elapsed_sec = sum(s.elapsed_sec for s in stages)
        last.metadata["configured_stage_results"] = configured_stage_results
        return last

    def _run_stage(
        self,
        workspace: CandidateWorkspace,
        stage: dict,
        stage_index: int,
        stage_name: str,
    ) -> "EvaluationResult":
        timeout = float(stage.get("timeout_sec", self._timeout))
        stage_deadline = _StageDeadline.from_config(stage.get("max_stage_seconds"))
        evaluator_mode = str(stage.get("mode", "external_validator"))
        validate_path = (
            None
            if evaluator_mode == "embedded_evaluate"
            else self._resolve_validate_path(stage.get("validate_path"))
        )
        data_policy = (
            {"context": _embedded_evaluate_data_context(stage.get("eval_inputs", {}))}
            if evaluator_mode == "embedded_evaluate"
            else self._data_policy(stage, validate_path)
        )
        seeds = list(stage.get("seeds", []))
        samples = int(stage.get("samples", len(seeds) or 1))
        sample_workers = min(int(stage.get("sample_workers", 1)), samples)
        retries = int(stage.get("retries", 0))
        artifact_policy = self._artifact_policy(stage)
        results: list[EvaluationResult] = []
        sequential_stop_decision: dict | None = None
        stage_wall_clock_started = time.perf_counter()
        if sample_workers > 1:
            with ThreadPoolExecutor(
                max_workers=sample_workers,
                thread_name_prefix=f"libreevolve-eval-{stage_name}",
            ) as executor:
                futures = [
                    executor.submit(
                        self._run_stage_sample,
                        workspace=workspace,
                        validate_path=validate_path,
                        evaluator_mode=evaluator_mode,
                        stage=stage,
                        stage_index=stage_index,
                        stage_name=stage_name,
                        sample_index=sample_index,
                        samples=samples,
                        seed=seeds[sample_index] if sample_index < len(seeds) else None,
                        timeout=timeout,
                        retries=retries,
                        artifact_policy=artifact_policy,
                        data_policy=data_policy,
                        stage_deadline=stage_deadline,
                    )
                    for sample_index in range(samples)
                ]
                results = [future.result() for future in futures]
        else:
            for sample_index in range(samples):
                result = self._run_stage_sample(
                    workspace=workspace,
                    validate_path=validate_path,
                    evaluator_mode=evaluator_mode,
                    stage=stage,
                    stage_index=stage_index,
                    stage_name=stage_name,
                    sample_index=sample_index,
                    samples=samples,
                    seed=seeds[sample_index] if sample_index < len(seeds) else None,
                    timeout=timeout,
                    retries=retries,
                    artifact_policy=artifact_policy,
                    data_policy=data_policy,
                    stage_deadline=stage_deadline,
                )
                results.append(result)
                if result.error == "stage_budget_exhausted":
                    break
                sequential_stop = self._hypothesis_test_sequential_stop(
                    stage_name,
                    results,
                    validate_path,
                    stage,
                    planned_samples=samples,
                )
                if sequential_stop is not None:
                    sequential_stop_decision = sequential_stop
                    break
        stage_wall_clock_elapsed_sec = time.perf_counter() - stage_wall_clock_started
        if len(results) == 1:
            results[0].metadata["sample_execution"] = _sample_execution_metadata(
                requested_workers=int(stage.get("sample_workers", 1)),
                effective_workers=sample_workers,
                planned_samples=samples,
                completed_samples=len(results),
                sample_elapsed_sec_sum=results[0].elapsed_sec,
                wall_clock_elapsed_sec=stage_wall_clock_elapsed_sec,
            )
            return results[0]
        aggregate = self._aggregate_sample_results(stage_name, results, validate_path, stage)
        aggregate.metadata["sample_execution"] = _sample_execution_metadata(
            requested_workers=int(stage.get("sample_workers", 1)),
            effective_workers=sample_workers,
            planned_samples=samples,
            completed_samples=len(results),
            sample_elapsed_sec_sum=sum(result.elapsed_sec for result in results),
            wall_clock_elapsed_sec=stage_wall_clock_elapsed_sec,
        )
        if sequential_stop_decision is not None:
            aggregate.metadata["hypothesis_test_sequential_stopping"] = (
                sequential_stop_decision
            )
        return aggregate

    def _run_stage_sample(
        self,
        *,
        workspace: CandidateWorkspace,
        validate_path: Path | None,
        evaluator_mode: str,
        stage: dict,
        stage_index: int,
        stage_name: str,
        sample_index: int,
        samples: int,
        seed: object,
        timeout: float,
        retries: int,
        artifact_policy: dict,
        data_policy: dict,
        stage_deadline: "_StageDeadline | None",
    ) -> "EvaluationResult":
        sample_deadline = _StageDeadline.from_config(stage.get("max_sample_seconds"))
        if "stdin_text" in stage or "stdin_file" in stage:
            stdin_text = stage.get("stdin_text")
            stdin_file = stage.get("stdin_file")
        else:
            stdin_text = self._stdin_text
            stdin_file = self._stdin_file
        context = {
            "name": stage_name,
            "stage_index": stage_index,
            "sample_index": sample_index,
            "seed": seed,
            "mode": evaluator_mode,
            "config": _stage_context_config(
                stage,
                stdin_text,
                stdin_file,
                self._problem.problem_dir,
            ),
            "evaluator_data": data_policy["context"],
        }
        if "workload" in stage:
            context["workload"] = copy.deepcopy(stage["workload"])
        if evaluator_mode == "embedded_evaluate":
            context["eval_inputs"] = stage.get("eval_inputs", {})
        if stage_deadline.exhausted():
            return _stage_budget_exhausted_result(
                workspace,
                validate_path,
                self._problem,
                f"{stage_name}[{sample_index}]" if samples > 1 else stage_name,
                context,
                stage_deadline,
                self._validator_network_policy,
            )
        return self._run_sample_with_retries(
            workspace=workspace,
            validate_path=validate_path,
            evaluator_mode=evaluator_mode,
            stage_name=f"{stage_name}[{sample_index}]" if samples > 1 else stage_name,
            timeout_sec=timeout,
            stage_context=context,
            stdin_text=stdin_text,
            stdin_file=stdin_file,
            retries=retries,
            artifact_policy=artifact_policy,
            min_score=stage.get("min_score"),
            metric_thresholds=stage.get("metric_thresholds"),
            stage_deadline=stage_deadline,
            sample_deadline=sample_deadline,
        )

    def _hypothesis_test_sequential_stop(
        self,
        stage_name: str,
        results: list["EvaluationResult"],
        validate_path: Path | None,
        stage: dict,
        *,
        planned_samples: int,
    ) -> dict | None:
        hypothesis_test = stage.get("hypothesis_test")
        if (
            not isinstance(hypothesis_test, dict)
            or hypothesis_test.get("sequential_stopping") is not True
        ):
            return None
        min_samples = int(hypothesis_test.get("min_samples", 2))
        if len(results) < min_samples or len(results) >= planned_samples:
            return None
        partial = self._aggregate_sample_results(
            stage_name,
            results,
            validate_path,
            stage,
        )
        hypothesis_result = _stage_hypothesis_test_result(
            partial,
            hypothesis_test,
        )
        decision = {
            "enabled": True,
            "stopped_early": partial.is_valid and hypothesis_result["passed"],
            "stop_reason": (
                "hypothesis_test_passed_after_min_samples"
                if partial.is_valid and hypothesis_result["passed"]
                else None
            ),
            "evaluated_samples": len(results),
            "planned_samples": planned_samples,
            "min_samples": min_samples,
            "hypothesis_test_result": hypothesis_result,
        }
        if decision["stopped_early"]:
            return decision
        return None

    def _run_sample_with_retries(
        self,
        workspace: CandidateWorkspace,
        validate_path: Path | None,
        evaluator_mode: str,
        stage_name: str,
        timeout_sec: float,
        stage_context: dict,
        stdin_text: str | None,
        stdin_file: str | Path | None,
        retries: int,
        artifact_policy: dict,
        min_score: object = None,
        metric_thresholds: object = None,
        stage_deadline: "_StageDeadline | None" = None,
        sample_deadline: "_StageDeadline | None" = None,
    ) -> "EvaluationResult":
        last: EvaluationResult | None = None
        attempts: list[dict] = []
        for attempt in range(retries + 1):
            context = dict(stage_context)
            context["attempt"] = attempt
            context = _stage_context_with_rng_seed(context)
            if stage_deadline is not None and stage_deadline.exhausted():
                result = _stage_budget_exhausted_result(
                    workspace,
                    validate_path,
                    self._problem,
                    stage_name,
                    context,
                    stage_deadline,
                    self._validator_network_policy,
                )
                result.metadata["attempts"] = attempts
                result.metadata["attempt_count"] = len(attempts)
                return result
            if sample_deadline is not None and sample_deadline.exhausted():
                result = _sample_budget_exhausted_result(
                    workspace,
                    validate_path,
                    self._problem,
                    stage_name,
                    context,
                    sample_deadline,
                    stage_deadline,
                    self._validator_network_policy,
                )
                result.metadata["attempts"] = attempts
                result.metadata["attempt_count"] = len(attempts)
                return result
            attempt_timeout = timeout_sec
            budget_limited_by = None
            if stage_deadline is not None:
                remaining = stage_deadline.remaining()
                if remaining is not None:
                    clipped = max(0.001, min(attempt_timeout, remaining))
                    if clipped < attempt_timeout:
                        attempt_timeout = clipped
                        budget_limited_by = "stage"
            if sample_deadline is not None:
                remaining = sample_deadline.remaining()
                if remaining is not None:
                    clipped = max(0.001, min(attempt_timeout, remaining))
                    if clipped < attempt_timeout:
                        attempt_timeout = clipped
                        budget_limited_by = "sample"
            if evaluator_mode == "external_validator":
                result = self._run_subprocess(
                    workspace=workspace,
                    stage_name=stage_name,
                    timeout_sec=attempt_timeout,
                    validate_path=validate_path,
                    stage_context=context,
                    stdin_text=stdin_text,
                    stdin_file=stdin_file,
                    artifact_policy=artifact_policy,
                )
            elif evaluator_mode == "embedded_evaluate":
                result = self._run_embedded_evaluate_subprocess(
                    workspace=workspace,
                    stage_name=stage_name,
                    timeout_sec=attempt_timeout,
                    stage_context=context,
                    artifact_policy=artifact_policy,
                )
            if budget_limited_by == "stage" and result.error == "timeout" and stage_deadline is not None:
                _mark_stage_budget_exhausted(result, stage_deadline)
            if budget_limited_by == "sample" and result.error == "timeout" and sample_deadline is not None:
                _mark_sample_budget_exhausted(result, sample_deadline, stage_deadline)
            result.metadata["attempt"] = attempt
            threshold_result = _stage_threshold_result(
                result,
                min_score,
                metric_thresholds,
                stage_context.get("config"),
            )
            threshold_passed = threshold_result["passed"]
            attempts.append(
                _retry_attempt_record(
                    result,
                    attempt,
                    context,
                    self._problem.problem_dir,
                    threshold=None if min_score is None else float(min_score),
                    threshold_passed=threshold_passed,
                    threshold_result=threshold_result,
                )
            )
            last = result
            if result.is_valid and threshold_passed:
                result.metadata["attempts"] = attempts
                result.metadata["attempt_count"] = len(attempts)
                return result
        assert last is not None
        last.metadata["attempts"] = attempts
        last.metadata["attempt_count"] = len(attempts)
        return last

    def _run_subprocess(
        self,
        workspace: CandidateWorkspace,
        stage_name: str,
        timeout_sec: float,
        validate_path: Path | None = None,
        stage_context: dict | None = None,
        stdin_text: str | None = None,
        stdin_file: str | Path | None = None,
        artifact_policy: dict | None = None,
        use_default_stdin: bool = True,
        materialized_workspace_root: Path | None = None,
        materialized_primary_path: Path | None = None,
    ) -> "EvaluationResult":
        if (materialized_workspace_root is None) != (
            materialized_primary_path is None
        ):
            raise ValueError(
                "materialized workspace root and primary path must be provided together"
            )
        validate_path = validate_path or self._resolve_validate_path(None)
        stage_context = stage_context or {"name": stage_name}
        artifact_policy = artifact_policy or self._artifact_policy({})
        if use_default_stdin and stdin_text is None and stdin_file is None:
            stdin_text = self._stdin_text
            stdin_file = self._stdin_file
        stage_context = self._stage_context_with_default_data(validate_path, stage_context)
        stage_context = _stage_context_with_rng_seed(stage_context)
        stdin_text, stdin_metadata = _validator_stdin_source(
            stdin_text,
            stdin_file,
            self._problem.problem_dir,
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runner = tmp_path / "_runner.py"
            result_path = tmp_path / "evaluator_result.json"
            stage_context_path = tmp_path / "stage_context.json"
            cand_root = materialized_workspace_root or (tmp_path / "candidate")
            runner.write_text(_RUNNER, encoding="utf-8")
            stage_context_path.write_text(
                strict_json_dumps(stage_context),
                encoding="utf-8",
            )
            started = time.perf_counter()
            if materialized_primary_path is not None:
                primary = materialized_primary_path
            else:
                try:
                    primary = workspace.materialize(cand_root)
                except Exception as exc:
                    elapsed = time.perf_counter() - started
                    metadata = _eval_metadata(
                        workspace,
                        validate_path,
                        self._problem.problem_dir,
                        stage_context,
                        network_policy=self._validator_network_policy,
                        stdin_metadata=stdin_metadata,
                    )
                    metadata["materialization_error"] = (
                        _materialization_error_metadata(exc)
                    )
                    metadata["synthetic_metrics"] = (
                        _synthetic_failure_metric_metadata(self._problem, -0.2)
                    )
                    metrics = _synthetic_failure_metrics(self._problem, -0.2)
                    return EvaluationResult(
                        fitness=-0.2,
                        metrics=metrics,
                        is_valid=False,
                        stages=[
                            EvaluationStageResult(
                                name=stage_name,
                                passed=False,
                                score=-0.2,
                                metrics=metrics,
                                error="materialization_error",
                                elapsed_sec=elapsed,
                            )
                        ],
                        error="materialization_error",
                        elapsed_sec=elapsed,
                        metadata=metadata,
                    )
            validator_env = _validator_env(self._validator_env_allowlist)
            if stage_context.get("rng_seed") is not None:
                validator_env["PYTHONHASHSEED"] = str(stage_context["rng_seed"])
            validator_env_meta = _validator_env_metadata(
                validator_env, self._validator_env_allowlist
            )
            allowed_dependency_paths = _evaluator_allowed_dependency_paths(
                validate_path,
                self._problem.problem_dir,
                stage_context,
            )
            # Use list form (not shell=True) to prevent injection.
            res = _run_validator_process(
                [sys.executable, str(runner),
                 str(validate_path), str(primary), str(cand_root),
                 str(stage_context_path), str(result_path),
                 str(self._problem.problem_dir),
                 json.dumps([str(path) for path in allowed_dependency_paths])],
                cwd=cand_root,
                timeout_sec=timeout_sec,
                env=validator_env,
                stdin_text=stdin_text,
                validator_network_policy=self._validator_network_policy,
            )
            stdout, stderr, diagnostic_output = _validator_output_diagnostics(
                res.stdout,
                res.stderr,
                self._output_max_chars,
                stream_decoding=res.stream_decoding,
            )
            artifact_metadata = _collect_evaluator_artifacts(
                cand_root,
                artifact_policy["dir"],
                include=artifact_policy["include"],
                exclude=artifact_policy["exclude"],
                max_files=artifact_policy["max_files"],
                max_bytes=artifact_policy["max_bytes"],
                redact_secrets=artifact_policy["redact_secrets"],
                stage_context=stage_context,
            )
            if res.timed_out:
                elapsed = time.perf_counter() - started
                metadata = _eval_metadata(
                    workspace,
                    validate_path,
                    self._problem.problem_dir,
                    stage_context,
                    validator_env_meta,
                    network_policy=self._validator_network_policy,
                    stdin_metadata=stdin_metadata,
                )
                metadata["timeout_cleanup"] = res.cleanup
                metadata["artifacts"] = artifact_metadata
                metadata["diagnostic_output"] = diagnostic_output
                metadata["synthetic_metrics"] = _synthetic_failure_metric_metadata(
                    self._problem, -0.2
                )
                metrics = _synthetic_failure_metrics(self._problem, -0.2)
                return EvaluationResult(
                    fitness=-0.2,
                    metrics=metrics,
                    is_valid=False,
                    stages=[
                        EvaluationStageResult(
                            name=stage_name,
                            passed=False,
                            score=-0.2,
                            metrics=metrics,
                            stdout=stdout,
                            stderr=stderr,
                            error="timeout",
                            elapsed_sec=elapsed,
                        )
                    ],
                    stdout=stdout,
                    stderr=stderr,
                    error="timeout",
                    elapsed_sec=elapsed,
                    metadata=metadata,
                )
            elapsed = time.perf_counter() - started
            if res.returncode != 0:
                metadata = _eval_metadata(
                    workspace,
                    validate_path,
                    self._problem.problem_dir,
                    stage_context,
                    validator_env_meta,
                    artifact_metadata,
                    network_policy=self._validator_network_policy,
                    stdin_metadata=stdin_metadata,
                )
                metadata["diagnostic_output"] = diagnostic_output
                metadata["synthetic_metrics"] = _synthetic_failure_metric_metadata(
                    self._problem, -0.2
                )
                metrics = _synthetic_failure_metrics(self._problem, -0.2)
                return EvaluationResult(
                    fitness=-0.2,
                    metrics=metrics,
                    is_valid=False,
                    stages=[
                        EvaluationStageResult(
                            name=stage_name,
                            passed=False,
                            score=-0.2,
                            metrics=metrics,
                            stdout=stdout,
                            stderr=stderr,
                            error=f"returncode_{res.returncode}",
                            elapsed_sec=elapsed,
                        )
                    ],
                    stdout=stdout,
                    stderr=stderr,
                    error="subprocess_error",
                    elapsed_sec=elapsed,
                    metadata=metadata,
                )
            try:
                raw_result = _read_evaluator_result(result_path)
                raw_metrics, program_outputs = _split_evaluator_result(raw_result)
                m = _validate_metrics(raw_metrics, self._problem)
                metadata = _eval_metadata(
                    workspace,
                    validate_path,
                    self._problem.problem_dir,
                    stage_context,
                    validator_env_meta,
                    artifact_metadata,
                    network_policy=self._validator_network_policy,
                    stdin_metadata=stdin_metadata,
                )
                metadata["diagnostic_output"] = diagnostic_output
                if program_outputs is not None:
                    metadata["program_outputs"] = program_outputs
                _add_metric_bound_diagnostics(metadata, self._problem, m)
                if not m.get("is_valid", False):
                    return EvaluationResult(
                        fitness=-0.1,
                        metrics=m,
                        is_valid=False,
                        stages=[
                            EvaluationStageResult(
                                name=stage_name,
                                passed=False,
                                score=-0.1,
                                metrics=m,
                                stdout=stdout,
                                stderr=stderr,
                                error="domain_invalid",
                                elapsed_sec=elapsed,
                            )
                        ],
                        stdout=stdout,
                        stderr=stderr,
                        error="domain_invalid",
                        elapsed_sec=elapsed,
                        metadata=metadata,
                    )
                fitness = self._problem.fitness_from_metrics(m)
                return EvaluationResult(
                    fitness=fitness,
                    metrics=m,
                    is_valid=True,
                    stages=[
                        EvaluationStageResult(
                            name=stage_name,
                            passed=True,
                            score=fitness,
                            metrics=m,
                            stdout=stdout,
                            stderr=stderr,
                            elapsed_sec=elapsed,
                        )
                    ],
                    stdout=stdout,
                    stderr=stderr,
                    elapsed_sec=elapsed,
                    metadata=metadata,
                )
            except (json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
                metadata = _eval_metadata(
                    workspace,
                    validate_path,
                    self._problem.problem_dir,
                    stage_context,
                    validator_env_meta,
                    artifact_metadata,
                    network_policy=self._validator_network_policy,
                    stdin_metadata=stdin_metadata,
                )
                metadata["malformed_metrics"] = _malformed_metrics_metadata(exc)
                metadata["diagnostic_output"] = diagnostic_output
                metadata["synthetic_metrics"] = _synthetic_failure_metric_metadata(
                    self._problem, -0.2
                )
                metrics = _synthetic_failure_metrics(self._problem, -0.2)
                return EvaluationResult(
                    fitness=-0.2,
                    metrics=metrics,
                    is_valid=False,
                    stages=[
                        EvaluationStageResult(
                            name=stage_name,
                            passed=False,
                            score=-0.2,
                            metrics=metrics,
                            stdout=stdout,
                            stderr=stderr,
                            error="malformed_metrics",
                            elapsed_sec=elapsed,
                        )
                    ],
                    stdout=stdout,
                    stderr=stderr,
                    error="malformed_metrics",
                    elapsed_sec=elapsed,
                    metadata=metadata,
                )

    def _run_embedded_evaluate_subprocess(
        self,
        workspace: CandidateWorkspace,
        stage_name: str,
        timeout_sec: float,
        stage_context: dict | None = None,
        artifact_policy: dict | None = None,
    ) -> "EvaluationResult":
        stage_context = stage_context or {"name": stage_name, "mode": "embedded_evaluate"}
        artifact_policy = artifact_policy or self._artifact_policy({})
        stage_context = _stage_context_with_rng_seed(stage_context)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runner = tmp_path / "_embedded_evaluate_runner.py"
            result_path = tmp_path / "evaluator_result.json"
            cand_root = tmp_path / "candidate"
            runner.write_text(_EMBEDDED_EVALUATE_RUNNER, encoding="utf-8")
            started = time.perf_counter()
            try:
                primary = workspace.materialize(cand_root)
            except Exception as exc:
                elapsed = time.perf_counter() - started
                metadata = _eval_metadata(
                    workspace,
                    None,
                    self._problem.problem_dir,
                    stage_context,
                    network_policy=self._validator_network_policy,
                )
                metadata["materialization_error"] = _materialization_error_metadata(exc)
                metadata["synthetic_metrics"] = _synthetic_failure_metric_metadata(
                    self._problem, -0.2
                )
                metrics = _synthetic_failure_metrics(self._problem, -0.2)
                return EvaluationResult(
                    fitness=-0.2,
                    metrics=metrics,
                    is_valid=False,
                    stages=[
                        EvaluationStageResult(
                            name=stage_name,
                            passed=False,
                            score=-0.2,
                            metrics=metrics,
                            error="materialization_error",
                            elapsed_sec=elapsed,
                        )
                    ],
                    error="materialization_error",
                    elapsed_sec=elapsed,
                    metadata=metadata,
                )
            validator_env = _validator_env(self._validator_env_allowlist)
            if stage_context.get("rng_seed") is not None:
                validator_env["PYTHONHASHSEED"] = str(stage_context["rng_seed"])
            validator_env_meta = _validator_env_metadata(
                validator_env, self._validator_env_allowlist
            )
            res = _run_validator_process(
                [
                    sys.executable,
                    str(runner),
                    str(cand_root),
                    str(primary),
                    json.dumps(stage_context),
                    str(result_path),
                    json.dumps([str(cand_root / path) for path in workspace.files]),
                ],
                cwd=cand_root,
                timeout_sec=timeout_sec,
                env=validator_env,
                stdin_text=None,
                validator_network_policy=self._validator_network_policy,
            )
            stdout, stderr, diagnostic_output = _validator_output_diagnostics(
                res.stdout,
                res.stderr,
                self._output_max_chars,
                stream_decoding=res.stream_decoding,
            )
            artifact_metadata = _collect_evaluator_artifacts(
                cand_root,
                artifact_policy["dir"],
                include=artifact_policy["include"],
                exclude=artifact_policy["exclude"],
                max_files=artifact_policy["max_files"],
                max_bytes=artifact_policy["max_bytes"],
                redact_secrets=artifact_policy["redact_secrets"],
                stage_context=stage_context,
            )
            if res.timed_out:
                elapsed = time.perf_counter() - started
                metadata = _eval_metadata(
                    workspace,
                    None,
                    self._problem.problem_dir,
                    stage_context,
                    validator_env_meta,
                    network_policy=self._validator_network_policy,
                )
                metadata["timeout_cleanup"] = res.cleanup
                metadata["artifacts"] = artifact_metadata
                metadata["diagnostic_output"] = diagnostic_output
                metadata["synthetic_metrics"] = _synthetic_failure_metric_metadata(
                    self._problem, -0.2
                )
                metrics = _synthetic_failure_metrics(self._problem, -0.2)
                return EvaluationResult(
                    fitness=-0.2,
                    metrics=metrics,
                    is_valid=False,
                    stages=[
                        EvaluationStageResult(
                            name=stage_name,
                            passed=False,
                            score=-0.2,
                            metrics=metrics,
                            stdout=stdout,
                            stderr=stderr,
                            error="timeout",
                            elapsed_sec=elapsed,
                        )
                    ],
                    stdout=stdout,
                    stderr=stderr,
                    error="timeout",
                    elapsed_sec=elapsed,
                    metadata=metadata,
                )
            elapsed = time.perf_counter() - started
            if res.returncode != 0:
                metadata = _eval_metadata(
                    workspace,
                    None,
                    self._problem.problem_dir,
                    stage_context,
                    validator_env_meta,
                    artifact_metadata,
                    network_policy=self._validator_network_policy,
                )
                metadata["diagnostic_output"] = diagnostic_output
                metadata["synthetic_metrics"] = _synthetic_failure_metric_metadata(
                    self._problem, -0.2
                )
                metrics = _synthetic_failure_metrics(self._problem, -0.2)
                return EvaluationResult(
                    fitness=-0.2,
                    metrics=metrics,
                    is_valid=False,
                    stages=[
                        EvaluationStageResult(
                            name=stage_name,
                            passed=False,
                            score=-0.2,
                            metrics=metrics,
                            stdout=stdout,
                            stderr=stderr,
                            error=f"returncode_{res.returncode}",
                            elapsed_sec=elapsed,
                        )
                    ],
                    stdout=stdout,
                    stderr=stderr,
                    error="subprocess_error",
                    elapsed_sec=elapsed,
                    metadata=metadata,
                )
            try:
                raw_result = _read_evaluator_result(result_path)
                raw_metrics, program_outputs = _split_evaluator_result(raw_result)
                m = _validate_metrics(raw_metrics, self._problem)
                metadata = _eval_metadata(
                    workspace,
                    None,
                    self._problem.problem_dir,
                    stage_context,
                    validator_env_meta,
                    artifact_metadata,
                    network_policy=self._validator_network_policy,
                )
                metadata["diagnostic_output"] = diagnostic_output
                if program_outputs is not None:
                    metadata["program_outputs"] = program_outputs
                _add_metric_bound_diagnostics(metadata, self._problem, m)
                if not m.get("is_valid", False):
                    return EvaluationResult(
                        fitness=-0.1,
                        metrics=m,
                        is_valid=False,
                        stages=[
                            EvaluationStageResult(
                                name=stage_name,
                                passed=False,
                                score=-0.1,
                                metrics=m,
                                stdout=stdout,
                                stderr=stderr,
                                error="domain_invalid",
                                elapsed_sec=elapsed,
                            )
                        ],
                        stdout=stdout,
                        stderr=stderr,
                        error="domain_invalid",
                        elapsed_sec=elapsed,
                        metadata=metadata,
                    )
                fitness = self._problem.fitness_from_metrics(m)
                return EvaluationResult(
                    fitness=fitness,
                    metrics=m,
                    is_valid=True,
                    stages=[
                        EvaluationStageResult(
                            name=stage_name,
                            passed=True,
                            score=fitness,
                            metrics=m,
                            stdout=stdout,
                            stderr=stderr,
                            elapsed_sec=elapsed,
                        )
                    ],
                    stdout=stdout,
                    stderr=stderr,
                    elapsed_sec=elapsed,
                    metadata=metadata,
                )
            except (json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
                metadata = _eval_metadata(
                    workspace,
                    None,
                    self._problem.problem_dir,
                    stage_context,
                    validator_env_meta,
                    artifact_metadata,
                    network_policy=self._validator_network_policy,
                )
                metadata["malformed_metrics"] = _malformed_metrics_metadata(exc)
                metadata["diagnostic_output"] = diagnostic_output
                metadata["synthetic_metrics"] = _synthetic_failure_metric_metadata(
                    self._problem, -0.2
                )
                metrics = _synthetic_failure_metrics(self._problem, -0.2)
                return EvaluationResult(
                    fitness=-0.2,
                    metrics=metrics,
                    is_valid=False,
                    stages=[
                        EvaluationStageResult(
                            name=stage_name,
                            passed=False,
                            score=-0.2,
                            metrics=metrics,
                            stdout=stdout,
                            stderr=stderr,
                            error="malformed_metrics",
                            elapsed_sec=elapsed,
                        )
                    ],
                    stdout=stdout,
                    stderr=stderr,
                    error="malformed_metrics",
                    elapsed_sec=elapsed,
                    metadata=metadata,
                )


    def _resolve_validate_path(self, raw: object) -> Path:
        if raw is None:
            path = self._problem.validate_path
        else:
            path = Path(str(raw))
            if not path.is_absolute():
                path = self._problem.problem_dir / path
        return _validate_problem_local_evaluator_path(path, self._problem.problem_dir)

    def _artifact_policy(self, stage: dict) -> dict:
        return {
            "dir": self._artifact_dir,
            "include": list(stage.get("artifact_include", self._artifact_include)),
            "exclude": list(stage.get("artifact_exclude", self._artifact_exclude)),
            "max_files": int(stage.get("artifact_max_files", self._artifact_max_files)),
            "max_bytes": int(stage.get("artifact_max_bytes", self._artifact_max_bytes)),
            "redact_secrets": bool(
                stage.get("artifact_redact_secrets", self._artifact_redact_secrets)
            ),
        }

    def _data_policy(self, stage: dict, validate_path: Path) -> dict:
        include = list(stage.get("data_include", self._data_include))
        exclude = list(stage.get("data_exclude", self._data_exclude))
        declared = _evaluator_declared_data_sources(
            validate_path,
            self._problem.problem_dir,
            include=include,
            exclude=exclude,
        )
        return {"context": _evaluator_data_context(declared)}

    def _stage_context_with_default_data(
        self, validate_path: Path, stage_context: dict
    ) -> dict:
        if "evaluator_data" in stage_context:
            return stage_context
        declared = _evaluator_declared_data_sources(
            validate_path,
            self._problem.problem_dir,
            include=self._data_include,
            exclude=self._data_exclude,
        )
        enriched = dict(stage_context)
        enriched["evaluator_data"] = _evaluator_data_context(declared)
        return enriched

    def _aggregate_sample_results(
        self,
        stage_name: str,
        results: list["EvaluationResult"],
        validate_path: Path | None,
        stage: dict,
    ) -> "EvaluationResult":
        valid = all(r.is_valid for r in results)
        aggregation_policy = _normalized_metric_aggregation(stage.get("metric_aggregation"))
        metrics = _aggregate_metrics([r.metrics for r in results], aggregation_policy)
        if self._problem.primary_metric in metrics:
            fitness = self._problem.fitness_from_metrics(metrics)
        else:
            fitness = sum(r.fitness for r in results) / len(results)
        if not valid:
            fitness = min(r.fitness for r in results)
            metrics.setdefault(self._problem.primary_metric, fitness)
            metrics["is_valid"] = False
        stages = [stage for result in results for stage in result.stages]
        stdout_join = "\n".join(r.stdout for r in results if r.stdout)
        stderr_join = "\n".join(r.stderr for r in results if r.stderr)
        stdout, stdout_meta = _bounded_diagnostic_stream(stdout_join, self._output_max_chars)
        stderr, stderr_meta = _bounded_diagnostic_stream(stderr_join, self._output_max_chars)
        metadata = {
            "stage": stage_name,
            "sample_count": len(results),
            "planned_sample_count": int(stage.get("samples", len(results))),
            "metric_aggregation": aggregation_policy,
            "samples": [r.to_dict() for r in results],
            "diagnostic_output": {
                "policy": "aggregate_sample_outputs_then_truncate",
                "max_chars": self._output_max_chars,
                "stdout": stdout_meta,
                "stderr": stderr_meta,
            },
        }
        evaluator_mode = (
            results[0].metadata.get("evaluator_mode")
            if results and isinstance(results[0].metadata, dict)
            else None
        )
        if isinstance(evaluator_mode, str):
            metadata["evaluator_mode"] = evaluator_mode
        if validate_path is not None:
            metadata.update(_evaluator_path_metadata(validate_path, self._problem.problem_dir))
        else:
            metadata["evaluator_mode"] = "embedded_evaluate"
            metadata["candidate_evaluator"] = _candidate_evaluator_metadata(
                results[0].metadata if results else {}
            )
        _add_metric_bound_diagnostics(metadata, self._problem, metrics)
        return EvaluationResult(
            fitness=fitness,
            metrics=metrics,
            is_valid=valid,
            stages=stages,
            stdout=stdout,
            stderr=stderr,
            error=None if valid else next((r.error for r in results if r.error), "sample_invalid"),
            elapsed_sec=sum(r.elapsed_sec for r in results),
            metadata=metadata,
        )


def _sample_execution_metadata(
    *,
    requested_workers: int,
    effective_workers: int,
    planned_samples: int,
    completed_samples: int,
    sample_elapsed_sec_sum: float,
    wall_clock_elapsed_sec: float,
) -> dict:
    sample_elapsed_sec_sum = max(0.0, float(sample_elapsed_sec_sum))
    wall_clock_elapsed_sec = max(0.0, float(wall_clock_elapsed_sec))
    compression_ratio = (
        sample_elapsed_sec_sum / wall_clock_elapsed_sec
        if wall_clock_elapsed_sec > 0.0
        else None
    )
    return {
        "mode": "thread_pool" if effective_workers > 1 else "serial",
        "requested_workers": requested_workers,
        "effective_workers": effective_workers,
        "planned_samples": planned_samples,
        "completed_samples": completed_samples,
        "deterministic_result_order": "sample_index",
        "sample_elapsed_sec_sum": sample_elapsed_sec_sum,
        "wall_clock_elapsed_sec": wall_clock_elapsed_sec,
        "wall_clock_compression_ratio": compression_ratio,
        "wall_clock_compression_observed": (
            compression_ratio is not None and compression_ratio > 1.0
        ),
    }


@dataclass
class EvaluationStageResult:
    name: str
    passed: bool
    score: float | None = None
    metrics: dict = field(default_factory=dict)
    stdout: str = ""
    stderr: str = ""
    error: str | None = None
    elapsed_sec: float = 0.0
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.name = _validate_evaluation_stage_name(self.name)
        self.passed = _validate_evaluation_bool("EvaluationStageResult.passed", self.passed)
        self.score = _validate_evaluation_number(
            "EvaluationStageResult.score",
            self.score,
            allow_none=True,
        )
        self.metrics = _validate_evaluation_metrics(
            "EvaluationStageResult.metrics",
            self.metrics,
        )
        self.stdout = _validate_evaluation_text("EvaluationStageResult.stdout", self.stdout)
        self.stderr = _validate_evaluation_text("EvaluationStageResult.stderr", self.stderr)
        self.error = _validate_evaluation_text(
            "EvaluationStageResult.error",
            self.error,
            allow_none=True,
        )
        self.elapsed_sec = _validate_evaluation_number(
            "EvaluationStageResult.elapsed_sec",
            self.elapsed_sec,
            minimum=0.0,
        )
        self.metadata = _validate_evaluation_metadata(
            "EvaluationStageResult.metadata",
            self.metadata,
        )

    def to_dict(self) -> dict:
        self.__post_init__()
        return {
            "name": self.name,
            "passed": self.passed,
            "score": self.score,
            "metrics": self.metrics,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error": self.error,
            "elapsed_sec": self.elapsed_sec,
            "metadata": self.metadata,
        }


@dataclass
class EvaluationResult:
    fitness: float
    metrics: dict
    is_valid: bool
    stages: list[EvaluationStageResult] = field(default_factory=list)
    stdout: str = ""
    stderr: str = ""
    error: str | None = None
    elapsed_sec: float = 0.0
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.fitness = _validate_evaluation_number("EvaluationResult.fitness", self.fitness)
        self.metrics = _validate_evaluation_metrics("EvaluationResult.metrics", self.metrics)
        self.is_valid = _validate_evaluation_bool("EvaluationResult.is_valid", self.is_valid)
        if not isinstance(self.stages, list):
            raise ValueError("EvaluationResult.stages must be a list of EvaluationStageResult")
        normalized_stages: list[EvaluationStageResult] = []
        for index, stage in enumerate(self.stages):
            if not isinstance(stage, EvaluationStageResult):
                raise ValueError(
                    "EvaluationResult.stages "
                    f"must contain EvaluationStageResult objects at index {index}"
                )
            stage.__post_init__()
            normalized_stages.append(stage)
        self.stages = normalized_stages
        self.stdout = _validate_evaluation_text("EvaluationResult.stdout", self.stdout)
        self.stderr = _validate_evaluation_text("EvaluationResult.stderr", self.stderr)
        self.error = _validate_evaluation_text(
            "EvaluationResult.error",
            self.error,
            allow_none=True,
        )
        self.elapsed_sec = _validate_evaluation_number(
            "EvaluationResult.elapsed_sec",
            self.elapsed_sec,
            minimum=0.0,
        )
        self.metadata = _validate_evaluation_metadata(
            "EvaluationResult.metadata",
            self.metadata,
        )

    def __float__(self) -> float:
        return self.fitness

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (int, float)):
            return self.fitness == float(other)
        return super().__eq__(other)

    def __sub__(self, other: object) -> float:
        if isinstance(other, (int, float)):
            return self.fitness - float(other)
        return NotImplemented

    def __rsub__(self, other: object) -> float:
        if isinstance(other, (int, float)):
            return float(other) - self.fitness
        return NotImplemented

    def to_dict(self) -> dict:
        self.__post_init__()
        return {
            "fitness": self.fitness,
            "metrics": self.metrics,
            "is_valid": self.is_valid,
            "stages": [stage.to_dict() for stage in self.stages],
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error": self.error,
            "elapsed_sec": self.elapsed_sec,
            "metadata": self.metadata,
            "accounting": evaluation_accounting(self),
        }


def _validate_evaluation_stage_name(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("EvaluationStageResult.name must be a manifest-safe stage label")
    if redact_sensitive_text(value) != value:
        raise ValueError("EvaluationStageResult.name must be a manifest-safe stage label")
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:\-\[\]]{0,191}", value) is None:
        raise ValueError("EvaluationStageResult.name must be a manifest-safe stage label")
    return value


def _validate_evaluation_bool(label: str, value: object) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be boolean")
    return value


def _validate_evaluation_number(
    label: str,
    value: object,
    *,
    allow_none: bool = False,
    minimum: float | None = None,
) -> float | None:
    if value is None and allow_none:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    if minimum is not None and number < minimum:
        raise ValueError(f"{label} must be >= {minimum}")
    return number


def _validate_evaluation_metrics(label: str, value: object) -> dict:
    try:
        return validate_program_metrics(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be JSON-safe finite metrics") from exc


def _validate_evaluation_metadata(label: str, value: object) -> dict:
    try:
        return validate_program_metadata(value, label)
    except ValueError as exc:
        raise ValueError(f"{label} must be JSON-safe metadata") from exc


def _validate_evaluation_text(
    label: str,
    value: object,
    *,
    allow_none: bool = False,
) -> str | None:
    if value is None and allow_none:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")
    text = _redact_secrets(value)
    if len(text) > _EVALUATION_RESULT_TEXT_MAX_CHARS:
        raise ValueError(
            f"{label} must be <= {_EVALUATION_RESULT_TEXT_MAX_CHARS} characters"
        )
    return text


def evaluation_accounting(result: EvaluationResult | dict) -> dict:
    """Return durable evaluator work counters for a structured evaluation."""
    accounting = {key: 0 for key in _ACCOUNTING_KEYS}
    accounting["schema"] = "evaluator_accounting_v1"
    _add_evaluation_accounting(accounting, result)
    return accounting


def _add_evaluation_accounting(accounting: dict, result: EvaluationResult | dict) -> None:
    if isinstance(result, EvaluationResult):
        metadata = result.metadata if isinstance(result.metadata, dict) else {}
        error = result.error
    elif isinstance(result, dict):
        embedded = result.get("accounting")
        if isinstance(embedded, dict):
            _add_embedded_accounting(accounting, embedded)
            return
        metadata = result.get("metadata") if isinstance(result.get("metadata"), dict) else {}
        error = result.get("error")
    else:
        return

    configured = metadata.get("configured_stage_results")
    if isinstance(configured, list):
        for record in configured:
            if not isinstance(record, dict):
                continue
            embedded_result = {
                "metadata": record.get("metadata") if isinstance(record.get("metadata"), dict) else {},
                "error": record.get("error"),
            }
            _add_evaluation_accounting(accounting, embedded_result)
        return

    samples = metadata.get("samples")
    if isinstance(samples, list):
        for sample in samples:
            if isinstance(sample, dict):
                _add_evaluation_accounting(accounting, sample)
        return

    attempts = metadata.get("attempts")
    if isinstance(attempts, list):
        if _is_configured_stage_metadata(metadata):
            accounting["configured_stage_samples"] += 1
        accounting["subprocess_attempts"] += len(attempts)
        accounting["retry_attempts"] += max(0, len(attempts) - 1)
        for attempt in attempts:
            if isinstance(attempt, dict):
                _add_accounting_error(accounting, attempt.get("error"))
        if not attempts:
            _add_accounting_error(accounting, error)
        return

    if _metadata_has_subprocess_attempt(metadata):
        accounting["subprocess_attempts"] += 1
    _add_accounting_error(accounting, error)


def _add_embedded_accounting(accounting: dict, embedded: dict) -> None:
    for key in _ACCOUNTING_KEYS:
        value = embedded.get(key, 0)
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            accounting[key] += value


def _is_configured_stage_metadata(metadata: dict) -> bool:
    stage = metadata.get("stage")
    return isinstance(stage, dict) and "stage_index" in stage


def _metadata_has_subprocess_attempt(metadata: dict) -> bool:
    if not isinstance(metadata.get("validate_path"), str):
        return False
    if "materialization_error" in metadata:
        return False
    return True


def _add_accounting_error(accounting: dict, error: object) -> None:
    if error == "timeout" or (
        isinstance(error, str)
        and error
        in {
            "candidate_build_timeout",
            "candidate_runner_timeout",
            "candidate_toolchain_probe_timeout",
        }
    ):
        accounting["timeout_count"] += 1
    elif error == "sample_budget_exhausted":
        accounting["sample_budget_exhaustions"] += 1
    elif error == "stage_budget_exhausted":
        accounting["stage_budget_exhaustions"] += 1


@dataclass
class _ValidatorProcessResult:
    returncode: int | None
    stdout: str
    stderr: str
    stream_decoding: dict = field(default_factory=dict)
    timed_out: bool = False
    cleanup: dict = field(default_factory=dict)


@dataclass
class _StageDeadline:
    max_seconds: float | None = None
    started: float = field(default_factory=time.perf_counter)

    @classmethod
    def from_config(cls, value: object) -> "_StageDeadline":
        if value is None:
            return cls(None)
        return cls(float(value))

    def elapsed(self) -> float:
        return time.perf_counter() - self.started

    def remaining(self) -> float | None:
        if self.max_seconds is None:
            return None
        return max(0.0, self.max_seconds - self.elapsed())

    def exhausted(self) -> bool:
        remaining = self.remaining()
        return remaining is not None and remaining <= 0.0


def _stage_budget_metadata(deadline: _StageDeadline) -> dict:
    remaining = deadline.remaining()
    return {
        "policy": "max_stage_seconds",
        "max_stage_seconds": deadline.max_seconds,
        "elapsed_sec": deadline.elapsed(),
        "remaining_sec": remaining,
        "exhausted": remaining is not None and remaining <= 0.0,
    }


def _sample_budget_metadata(deadline: _StageDeadline) -> dict:
    remaining = deadline.remaining()
    return {
        "policy": "max_sample_seconds",
        "max_sample_seconds": deadline.max_seconds,
        "elapsed_sec": deadline.elapsed(),
        "remaining_sec": remaining,
        "exhausted": remaining is not None and remaining <= 0.0,
    }


def _stage_budget_exhausted_result(
    workspace: CandidateWorkspace,
    validate_path: Path | None,
    problem: Problem,
    stage_name: str,
    stage_context: dict,
    deadline: _StageDeadline,
    validator_network_policy: str = "host",
) -> EvaluationResult:
    elapsed = deadline.elapsed()
    metadata = _eval_metadata(
        workspace,
        validate_path,
        problem.problem_dir,
        stage_context,
        network_policy=validator_network_policy,
    )
    metadata["stage_budget"] = _stage_budget_metadata(deadline)
    metadata["synthetic_metrics"] = _synthetic_failure_metric_metadata(problem, -0.2)
    metrics = _synthetic_failure_metrics(problem, -0.2)
    return EvaluationResult(
        fitness=-0.2,
        metrics=metrics,
        is_valid=False,
        stages=[
            EvaluationStageResult(
                name=stage_name,
                passed=False,
                score=-0.2,
                metrics=metrics,
                error="stage_budget_exhausted",
                elapsed_sec=elapsed,
                metadata={"stage_budget": metadata["stage_budget"]},
            )
        ],
        error="stage_budget_exhausted",
        elapsed_sec=elapsed,
        metadata=metadata,
    )


def _sample_budget_exhausted_result(
    workspace: CandidateWorkspace,
    validate_path: Path | None,
    problem: Problem,
    stage_name: str,
    stage_context: dict,
    sample_deadline: _StageDeadline,
    stage_deadline: _StageDeadline | None = None,
    validator_network_policy: str = "host",
) -> EvaluationResult:
    elapsed = sample_deadline.elapsed()
    metadata = _eval_metadata(
        workspace,
        validate_path,
        problem.problem_dir,
        stage_context,
        network_policy=validator_network_policy,
    )
    metadata["sample_budget"] = _sample_budget_metadata(sample_deadline)
    if stage_deadline is not None and stage_deadline.max_seconds is not None:
        metadata["stage_budget"] = _stage_budget_metadata(stage_deadline)
    metadata["synthetic_metrics"] = _synthetic_failure_metric_metadata(problem, -0.2)
    stage_metadata = {"sample_budget": metadata["sample_budget"]}
    if "stage_budget" in metadata:
        stage_metadata["stage_budget"] = metadata["stage_budget"]
    metrics = _synthetic_failure_metrics(problem, -0.2)
    return EvaluationResult(
        fitness=-0.2,
        metrics=metrics,
        is_valid=False,
        stages=[
            EvaluationStageResult(
                name=stage_name,
                passed=False,
                score=-0.2,
                metrics=metrics,
                error="sample_budget_exhausted",
                elapsed_sec=elapsed,
                metadata=stage_metadata,
            )
        ],
        error="sample_budget_exhausted",
        elapsed_sec=elapsed,
        metadata=metadata,
    )


def _mark_stage_budget_exhausted(result: EvaluationResult, deadline: _StageDeadline) -> None:
    budget = _stage_budget_metadata(deadline)
    result.error = "stage_budget_exhausted"
    result.metadata["stage_budget"] = budget
    for stage in result.stages:
        if stage.error == "timeout":
            stage.error = "stage_budget_exhausted"
            stage.metadata["stage_budget"] = budget


def _mark_sample_budget_exhausted(
    result: EvaluationResult,
    sample_deadline: _StageDeadline,
    stage_deadline: _StageDeadline | None = None,
) -> None:
    budget = _sample_budget_metadata(sample_deadline)
    result.error = "sample_budget_exhausted"
    result.metadata["sample_budget"] = budget
    if stage_deadline is not None and stage_deadline.max_seconds is not None:
        result.metadata["stage_budget"] = _stage_budget_metadata(stage_deadline)
    for stage in result.stages:
        if stage.error == "timeout":
            stage.error = "sample_budget_exhausted"
            stage.metadata["sample_budget"] = budget
            if "stage_budget" in result.metadata:
                stage.metadata["stage_budget"] = result.metadata["stage_budget"]


def _syntax_errors(workspace: CandidateWorkspace) -> list[dict]:
    errors: list[dict] = []
    for rel_path, content in sorted(workspace.files.items()):
        if not rel_path.endswith(".py"):
            continue
        try:
            compile(content, rel_path, "exec")
        except SyntaxError as exc:
            errors.append(
                {
                    "path": rel_path,
                    "line": exc.lineno,
                    "offset": exc.offset,
                    "message": exc.msg,
                    "summary": f"{rel_path}: {exc.__class__.__name__}: {exc}",
                }
            )
    return errors


def _run_validator_process(
    args: list[str],
    cwd: Path,
    timeout_sec: float,
    env: dict[str, str],
    stdin_text: str | None = None,
    validator_network_policy: str = "host",
    python_script_bootstrap: bool = True,
) -> _ValidatorProcessResult:
    launch_args = list(args)
    launch_env = dict(env)
    launch_env["LIBREEVOLVE_VALIDATOR_NETWORK_POLICY"] = (
        _validate_validator_network_policy(validator_network_policy)
    )
    release_file: Path | None = None
    if (
        python_script_bootstrap
        and os.name == "nt"
        and len(args) > 1
        and args[1] != "-c"
    ):
        release_file = cwd / f".libreevolve-validator-release-{uuid4().hex}"
        launch_env["LIBREEVOLVE_VALIDATOR_RELEASE"] = str(release_file)
        launch_args = [
            args[0],
            "-c",
            _WINDOWS_VALIDATOR_BOOTSTRAP,
            *args[1:],
        ]
    stdin_bytes = None if stdin_text is None else stdin_text.encode("utf-8")
    kwargs = {
        "cwd": str(cwd),
        "stdin": subprocess.DEVNULL if stdin_bytes is None else subprocess.PIPE,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "env": launch_env,
    }
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        kwargs["start_new_session"] = True
    proc = subprocess.Popen(launch_args, **kwargs)
    job = _assign_windows_kill_job(proc)
    if release_file is not None:
        release_file.write_text("go", encoding="utf-8")
    try:
        stdout_raw, stderr_raw = proc.communicate(
            input=stdin_bytes,
            timeout=timeout_sec,
        )
        if job is not None:
            _close_windows_job(job)
        stdout, stdout_meta = _decode_validator_stream(stdout_raw)
        stderr, stderr_meta = _decode_validator_stream(stderr_raw)
        return _ValidatorProcessResult(
            proc.returncode,
            stdout,
            stderr,
            stream_decoding={
                "policy": "utf-8_replace",
                "stdout": stdout_meta,
                "stderr": stderr_meta,
            },
        )
    except subprocess.TimeoutExpired:
        job_cleanup = _close_windows_job(job) if job is not None else None
        cleanup = _terminate_process_tree(proc)
        if job is not None:
            cleanup["job_object"] = job_cleanup
        try:
            stdout_raw, stderr_raw = proc.communicate(timeout=2.0)
        except subprocess.TimeoutExpired:
            cleanup["direct_kill_after_tree_timeout"] = True
            proc.kill()
            stdout_raw, stderr_raw = proc.communicate(timeout=2.0)
        stdout, stdout_meta = _decode_validator_stream(stdout_raw)
        stderr, stderr_meta = _decode_validator_stream(stderr_raw)
        return _ValidatorProcessResult(
            proc.returncode,
            stdout,
            stderr,
            stream_decoding={
                "policy": "utf-8_replace",
                "stdout": stdout_meta,
                "stderr": stderr_meta,
            },
            timed_out=True,
            cleanup=cleanup,
        )


def _terminate_process_tree(proc: subprocess.Popen) -> dict:
    result = {
        "pid": proc.pid,
        "attempted": True,
        "output_policy": {
            "policy": "redact_then_truncate",
            "max_chars": _TIMEOUT_CLEANUP_OUTPUT_MAX_CHARS,
        },
    }
    if proc.poll() is not None:
        result.update({"method": "already_exited", "returncode": proc.returncode})
        return result
    if os.name == "nt":
        result["method"] = "taskkill"
        try:
            completed = subprocess.run(
                ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                capture_output=True,
                text=True,
                timeout=5.0,
            )
            result.update(
                {
                    "returncode": completed.returncode,
                    **_bounded_cleanup_output(completed.stdout, completed.stderr),
                }
            )
            if completed.returncode != 0:
                child_pids = _reported_taskkill_child_pids(
                    completed.stdout,
                    completed.stderr,
                    root_pid=proc.pid,
                )
                if child_pids:
                    result["reported_child_pids"] = child_pids
                    result["direct_child_kill"] = _terminate_windows_reported_pids(child_pids)
        except (FileNotFoundError, subprocess.SubprocessError) as exc:
            result.update({"fallback": "kill", **_bounded_cleanup_error(exc)})
            proc.kill()
    else:
        result["method"] = "killpg"
        try:
            os.killpg(proc.pid, signal.SIGKILL)
            result["returncode"] = 0
        except ProcessLookupError:
            result.update({"returncode": 0, "already_exited": True})
        except OSError as exc:
            result.update({"fallback": "kill", **_bounded_cleanup_error(exc)})
            proc.kill()
    return result


def _reported_taskkill_child_pids(
    stdout: str | None,
    stderr: str | None,
    *,
    root_pid: int,
) -> list[int]:
    text = "\n".join(part for part in (stdout or "", stderr or "") if part)
    pids = sorted({int(value) for value in re.findall(r"\bPID\s+(\d+)\b", text)})
    return [pid for pid in pids if pid != root_pid]


def _terminate_windows_reported_pids(pids: list[int]) -> list[dict]:
    attempts = []
    for pid in pids:
        record: dict = {
            "pid": pid,
            "method": "taskkill_pid",
            "output_policy": {
                "policy": "redact_then_truncate",
                "max_chars": _TIMEOUT_CLEANUP_OUTPUT_MAX_CHARS,
            },
        }
        try:
            completed = subprocess.run(
                ["taskkill", "/PID", str(pid), "/F"],
                capture_output=True,
                text=True,
                timeout=5.0,
            )
            record.update(
                {
                    "returncode": completed.returncode,
                    **_bounded_cleanup_output(completed.stdout, completed.stderr),
                }
            )
            if completed.returncode != 0:
                record["fallback"] = "terminate_process"
                record["terminate_process"] = _terminate_windows_pid(pid)
        except (FileNotFoundError, subprocess.SubprocessError) as exc:
            record.update({"fallback": "terminate_process", **_bounded_cleanup_error(exc)})
            record["terminate_process"] = _terminate_windows_pid(pid)
        attempts.append(record)
    return attempts


def _terminate_windows_pid(pid: int) -> dict:
    result = {"pid": pid, "attempted": True, "method": "TerminateProcess"}
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.OpenProcess(_PROCESS_TERMINATE, False, int(pid))
        if not handle:
            result["opened"] = False
            result["error"] = f"OpenProcess failed: {ctypes.get_last_error()}"
            return result
        result["opened"] = True
        try:
            ok = bool(kernel32.TerminateProcess(handle, 1))
            result["terminated"] = ok
            if not ok:
                result["error"] = f"TerminateProcess failed: {ctypes.get_last_error()}"
        finally:
            result["closed"] = bool(kernel32.CloseHandle(handle))
    except Exception as exc:
        result.update(_bounded_cleanup_error(exc))
    return result


def _assign_windows_kill_job(proc: subprocess.Popen):
    if os.name != "nt":
        return None
    assignment = {"attempted": True, "assigned": False, "kill_on_close": True}
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.CreateJobObjectW(None, None)
        if not handle:
            assignment["error"] = f"CreateJobObjectW failed: {ctypes.get_last_error()}"
            return assignment
        info = _JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        ok = kernel32.SetInformationJobObject(
            handle,
            _JobObjectExtendedLimitInformation,
            ctypes.byref(info),
            ctypes.sizeof(info),
        )
        if not ok:
            assignment["error"] = f"SetInformationJobObject failed: {ctypes.get_last_error()}"
            kernel32.CloseHandle(handle)
            return assignment
        if not kernel32.AssignProcessToJobObject(handle, int(proc._handle)):
            assignment["error"] = f"AssignProcessToJobObject failed: {ctypes.get_last_error()}"
            kernel32.CloseHandle(handle)
            return assignment
        assignment.update({"assigned": True, "handle": handle})
        return assignment
    except Exception as exc:
        assignment.update(_bounded_cleanup_error(exc))
        return assignment


def _close_windows_job(assignment: dict) -> dict:
    result = {
        key: value for key, value in assignment.items()
        if key != "handle"
    }
    result.setdefault("closed", False)
    if not assignment.get("assigned") or "handle" not in assignment:
        return result
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        result["closed"] = bool(kernel32.CloseHandle(assignment["handle"]))
    except Exception as exc:
        result.update(_bounded_cleanup_error(exc))
    return result


def _decode_validator_stream(raw: object) -> tuple[str, dict]:
    if raw is None:
        raw_bytes = b""
    elif isinstance(raw, bytes):
        raw_bytes = raw
    elif isinstance(raw, str):
        text = raw
        encoded = text.encode("utf-8", errors="replace")
        return text, {
            "encoding": "utf-8",
            "errors": "replace",
            "byte_count": len(encoded),
            "decoded_chars": len(text),
            "replacement_chars": text.count("\ufffd"),
            "malformed": False,
            "source": "text",
        }
    else:
        text = str(raw)
        encoded = text.encode("utf-8", errors="replace")
        return text, {
            "encoding": "utf-8",
            "errors": "replace",
            "byte_count": len(encoded),
            "decoded_chars": len(text),
            "replacement_chars": text.count("\ufffd"),
            "malformed": False,
            "source": "coerced",
        }
    text = raw_bytes.decode("utf-8", errors="replace")
    replacement_chars = text.count("\ufffd")
    return text, {
        "encoding": "utf-8",
        "errors": "replace",
        "byte_count": len(raw_bytes),
        "decoded_chars": len(text),
        "replacement_chars": replacement_chars,
        "malformed": replacement_chars > 0,
        "source": "bytes",
    }


def _bounded_cleanup_output(stdout: str | None, stderr: str | None) -> dict:
    stored_stdout, stdout_meta = _bounded_diagnostic_stream(
        stdout or "", _TIMEOUT_CLEANUP_OUTPUT_MAX_CHARS
    )
    stored_stderr, stderr_meta = _bounded_diagnostic_stream(
        stderr or "", _TIMEOUT_CLEANUP_OUTPUT_MAX_CHARS
    )
    return {
        "stdout": stored_stdout,
        "stderr": stored_stderr,
        "stdout_diagnostics": stdout_meta,
        "stderr_diagnostics": stderr_meta,
    }


def _bounded_cleanup_error(exc: BaseException) -> dict:
    message = f"{exc.__class__.__name__}: {exc}"
    stored, diagnostics = _bounded_diagnostic_stream(
        message, _TIMEOUT_CLEANUP_OUTPUT_MAX_CHARS
    )
    return {"error": stored, "error_diagnostics": diagnostics}


def _eval_metadata(
    workspace: CandidateWorkspace,
    validate_path: Path | None,
    problem_dir: Path,
    stage_context: dict,
    validator_env: dict | None = None,
    artifacts: dict | None = None,
    network_policy: str = "host",
    stdin_metadata: dict | None = None,
) -> dict:
    evaluator_mode = str(stage_context.get("mode", "external_validator"))
    metadata = {
        "primary_file": workspace.primary_file,
        "files": sorted(workspace.files),
        "evaluator_mode": evaluator_mode,
        "validator_boundary": _validator_boundary_metadata(network_policy),
        "stage": _stage_context_metadata(stage_context, problem_dir),
    }
    if validate_path is not None:
        metadata.update(_evaluator_path_metadata(validate_path, problem_dir))
        metadata["evaluator_dependency_policy"] = _evaluator_dependency_metadata(
            validate_path,
            problem_dir,
            stage_context,
        )
    else:
        metadata["candidate_evaluator"] = {
            "entrypoint": workspace.primary_file,
            "callable": "evaluate",
            "signature": "evaluate(eval_inputs)",
            "eval_inputs": _eval_inputs_metadata(
                stage_context.get("eval_inputs", {})
            ),
        }
        metadata["evaluator_dependency_policy"] = {
            "policy": "candidate_primary_module_embedded_evaluate_v1",
            "allowed_scope": "materialized_candidate_workspace",
            "workspace_dependency_policy": (
                "materialized_candidate_files_only_for_workspace_local_modules_and_reads"
            ),
            "runtime_enforced": True,
            "file_count": len(workspace.files),
            "problem_local_dependency_policy": "not_used",
            "outside_problem_policy": "not_constrained_by_this_policy",
        }
    if validator_env is not None:
        metadata["validator_env"] = validator_env
        metadata["stdin"] = stdin_metadata or _validator_stdin_metadata(None)
    if artifacts is not None:
        metadata["artifacts"] = artifacts
    return metadata


def _candidate_evaluator_metadata(metadata: dict) -> dict:
    candidate = metadata.get("candidate_evaluator")
    if isinstance(candidate, dict):
        return copy.deepcopy(candidate)
    return {
        "entrypoint": metadata.get("primary_file"),
        "callable": "evaluate",
        "signature": "evaluate(eval_inputs)",
    }


def _embedded_evaluate_data_context(eval_inputs: object) -> dict:
    return {
        "enabled": True,
        "policy": "embedded_candidate_eval_inputs",
        "eval_inputs": _eval_inputs_metadata(eval_inputs),
    }


def _eval_inputs_metadata(eval_inputs: object) -> dict:
    payload = strict_json_dumps(eval_inputs)
    raw = payload.encode("utf-8")
    return {
        "schema": "libreevolve.eval_inputs_provenance.v1",
        "type": type(eval_inputs).__name__,
        "json_bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "retained": False,
    }


def _validator_stdin_source(
    stdin_text: str | None,
    stdin_file: str | Path | None,
    problem_dir: Path,
) -> tuple[str | None, dict]:
    if stdin_text is not None and stdin_file is not None:
        raise ValueError("validator stdin cannot set both stdin_text and stdin_file")
    if stdin_file is None:
        return stdin_text, _validator_stdin_metadata(stdin_text)
    path = Path(str(stdin_file))
    if not path.is_absolute():
        path = problem_dir / path
    resolved = _validate_problem_local_stdin_file_path(path, problem_dir)
    raw = resolved.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("validator stdin_file must be UTF-8 text") from exc
    if len(text) > MAX_EVALUATOR_STDIN_CHARS:
        raise ValueError(
            f"validator stdin_file must be <= {MAX_EVALUATOR_STDIN_CHARS} characters"
        )
    metadata = _validator_stdin_metadata(text)
    metadata.update(
        {
            "policy": "configured_file",
            "source": "problem_local_file",
            "path": _configured_stdin_file_display(resolved, problem_dir),
            "path_hash": hashlib.sha256(str(resolved).encode("utf-8")).hexdigest(),
            "file_bytes": len(raw),
            "file_sha256": hashlib.sha256(raw).hexdigest(),
        }
    )
    return text, metadata


def _validator_filesystem_capabilities() -> dict:
    return {
        "schema": "libreevolve.validator_filesystem_capabilities.v1",
        "policy": "candidate_root_plus_declared_problem_files",
        "enforcement": "python_runner_problem_local_provenance_checks",
        "cwd": {
            "path": "materialized_candidate_root",
            "read": True,
            "write": True,
            "execute": True,
            "lifetime": "temporary_per_attempt",
        },
        "candidate_workspace": {
            "scope": "materialized_candidate_files",
            "read": True,
            "write": True,
            "execute": True,
            "host_filesystem_sandbox": "unsupported",
        },
        "declared_problem_files": {
            "scope": "entrypoint_companion_data_and_stdin_provenance",
            "read": True,
            "write": False,
            "execute": True,
            "undeclared_problem_local_reads": "python_open_and_import_checks_denied",
        },
        "evaluator_artifacts": {
            "write": "bounded_include_globs",
            "copy_out": "hashed_redacted_optional",
            "symlink_policy": "link_metadata_not_unbounded_follow",
        },
        "host_filesystem": {
            "os_sandbox": "unsupported",
            "ambient_access_possible": True,
            "undeclared_host_paths": "not_capability_enforced",
        },
    }


def _validator_resource_limit_policy() -> dict:
    return {
        "schema": "libreevolve.validator_resource_limit_policy.v1",
        "policy": "wall_clock_timeout_only",
        "enforcement": "local_subprocess_timeout_cleanup",
        "wall_clock_timeout": {
            "supported": True,
            "source": "configured_stage_or_sample_timeout",
            "cleanup": "process_group_or_windows_job_object_plus_tree_kill",
        },
        "cpu": {"supported": False, "quota": "unsupported"},
        "memory": {"supported": False, "quota": "unsupported"},
        "gpu": {"supported": False, "quota": "unsupported"},
        "disk": {"supported": False, "quota": "unsupported"},
        "process_count": {"supported": False, "quota": "unsupported"},
        "container_runtime_limits": "unsupported",
        "remaining_gap": (
            "CPU/memory/GPU/disk/process quotas require an external sandbox "
            "or worker runtime"
        ),
    }


def _validator_network_boundary(network_policy: str) -> dict:
    network_policy = _validate_validator_network_policy(network_policy)
    if network_policy == "deny":
        return {
            "network_policy": network_policy,
            "network_egress": "python_socket_denied_not_os_sandbox",
            "network_denial": "python_socket_monkeypatch",
        }
    return {
        "network_policy": network_policy,
        "network_egress": "host_inherited_not_sandboxed",
        "network_denial": "unsupported",
    }


def _validator_boundary_metadata(network_policy: str = "host") -> dict:
    network = _validator_network_boundary(network_policy)
    return {
        "policy": "local_subprocess_boundary_v1",
        "execution": "temporary_local_subprocess",
        "security_sandbox": "unsupported",
        "container": "unsupported",
        "filesystem_capability_model": "candidate_root_plus_declared_problem_files",
        "filesystem_capabilities": _validator_filesystem_capabilities(),
        "network_policy": network["network_policy"],
        "network_egress": network["network_egress"],
        "network_denial": network["network_denial"],
        "network_denial_scope": "python_socket_api_only_not_kernel_or_container",
        "resource_limits": {
            "wall_clock_timeout": "configured_stage_or_sample_timeout",
            "cpu": "unsupported",
            "memory": "unsupported",
            "gpu": "unsupported",
            "disk": "unsupported",
            "process_count": "unsupported",
        },
        "resource_limit_policy": _validator_resource_limit_policy(),
        "secret_boundary": "minimal_environment_allowlist_with_redacted_diagnostics",
    }


def _validator_stdin_metadata(stdin_text: str | None) -> dict:
    if stdin_text is None:
        return {
            "policy": "devnull",
            "interactive_input": "unsupported",
            "generated_input": "unsupported",
        }
    raw = stdin_text.encode("utf-8")
    redacted = redact_sensitive_text(stdin_text)
    return {
        "policy": "configured_text",
        "interactive_input": "fixture_text",
        "generated_input": "unsupported",
        "encoding": "utf-8",
        "chars": len(stdin_text),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "text_retained": False,
        "redacted": redacted != stdin_text,
        "max_chars": MAX_EVALUATOR_STDIN_CHARS,
    }


def _validate_problem_local_stdin_file_path(path: Path, problem_dir: Path) -> Path:
    resolved_root = problem_dir.resolve()
    resolved = path.resolve(strict=False)
    if resolved_root != resolved and resolved_root not in resolved.parents:
        raise ValueError(
            "validator stdin_file escapes problem directory: "
            f"{_configured_stdin_file_display(resolved, problem_dir)}"
        )
    if not resolved.exists():
        raise ValueError(
            "validator stdin_file does not exist: "
            f"{_configured_stdin_file_display(resolved, problem_dir)}"
        )
    if not resolved.is_file():
        raise ValueError(
            "validator stdin_file is not a file: "
            f"{_configured_stdin_file_display(resolved, problem_dir)}"
        )
    return resolved


def _configured_stdin_file_display(path: Path, problem_dir: Path) -> str:
    resolved = path.resolve(strict=False)
    try:
        display = resolved.relative_to(problem_dir.resolve()).as_posix()
    except ValueError:
        display = f"<outside-problem>/{resolved.name}"
    return redact_sensitive_text(_escape_diagnostic_controls(display))


def _stage_context_config(
    stage: dict,
    stdin_text: str | None,
    stdin_file: str | Path | None,
    problem_dir: Path,
) -> dict:
    config = copy.deepcopy(stage)
    if "eval_inputs" in config:
        config["eval_inputs"] = _eval_inputs_metadata(config["eval_inputs"])
    if "stdin_text" in config or "stdin_file" in config:
        config.pop("stdin_text", None)
        config.pop("stdin_file", None)
        _, stdin_metadata = _validator_stdin_source(
            stdin_text,
            stdin_file,
            problem_dir,
        )
        config["stdin"] = stdin_metadata
    return config


def _materialization_error_metadata(exc: Exception) -> dict:
    message = _bounded_redacted_text(str(exc), 500)
    record = {
        "exception_type": exc.__class__.__name__,
        "message": message,
    }
    if isinstance(exc, CandidateMaterializationError):
        record["reason"] = _bounded_redacted_text(exc.reason, 100)
        record["paths"] = [
            _bounded_redacted_text(path, 240)
            for path in exc.paths[:4]
        ]
    return record


def _validator_output_diagnostics(
    stdout: str,
    stderr: str,
    max_chars: int,
    *,
    stream_decoding: dict | None = None,
) -> tuple[str, str, dict]:
    stored_stdout, stdout_meta = _bounded_diagnostic_stream(stdout, max_chars)
    stored_stderr, stderr_meta = _bounded_diagnostic_stream(stderr, max_chars)
    diagnostic_output = {
        "policy": "decode_utf8_replace_then_redact_then_truncate",
        "max_chars": max_chars,
        "stdout": stdout_meta,
        "stderr": stderr_meta,
    }
    if stream_decoding is not None:
        diagnostic_output["stream_decoding"] = stream_decoding
    return (
        stored_stdout,
        stored_stderr,
        diagnostic_output,
    )


def _bounded_diagnostic_stream(text: str, max_chars: int) -> tuple[str, dict]:
    redacted = _redact_secrets(text)
    stored = _truncate_diagnostic_text(redacted, max_chars)
    return stored, {
        "redacted": redacted != text,
        "redacted_chars": len(redacted),
        "stored_chars": len(stored),
        "truncated": len(stored) < len(redacted),
        "omitted_chars": max(0, len(redacted) - len(stored)),
    }


def _truncate_diagnostic_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    if max_chars <= 0:
        return ""
    suffix = "...<truncated>"
    if max_chars <= len(suffix):
        return suffix[:max_chars]
    return text[: max_chars - len(suffix)] + suffix


def _malformed_metrics_metadata(exc: Exception) -> dict:
    return {
        "reason": _malformed_metrics_reason(exc),
        "exception_type": exc.__class__.__name__,
        "message": _bounded_redacted_text(str(exc), 500),
    }


def _malformed_metrics_reason(exc: Exception) -> str:
    if isinstance(exc, json.JSONDecodeError):
        return "invalid_json"
    message = str(exc)
    if "evaluator result keys must be strings" in message:
        return "non_string_keys"
    if "evaluator outputs" in message or "program_output" in message or (
        "outputs" in message and "JSON value" in message
    ):
        return "malformed_outputs"
    if "not JSON serializable" in message or "Out of range float values" in message:
        return "not_json_serializable"
    if "missing declared metrics" in message:
        return "missing_declared_metrics"
    if "undeclared metrics" in message:
        return "undeclared_metrics"
    if "is_valid" in message:
        return "invalid_is_valid"
    if "must be numeric" in message:
        return "invalid_metric_type"
    if "must be finite" in message:
        return "nonfinite_metric"
    if "must be a metrics dictionary" in message:
        return "non_mapping_result"
    return "malformed_metrics"


def _bounded_redacted_text(text: str, max_chars: int) -> str:
    text = _redact_secrets(text)
    if len(text) <= max_chars:
        return text
    suffix = "...<truncated>"
    return text[: max_chars - len(suffix)] + suffix


def _synthetic_failure_metrics(problem: Problem, penalty: float) -> dict:
    metrics = {
        str(metric["name"]): float(penalty)
        for metric in problem.metrics
        if str(metric.get("name")) != "is_valid"
    }
    metrics["is_valid"] = False
    return metrics


def _synthetic_failure_metric_metadata(problem: Problem, penalty: float) -> dict:
    metric_names = [
        str(metric["name"])
        for metric in problem.metrics
        if str(metric.get("name")) != "is_valid"
    ]
    return {
        "schema": "synthetic_failure_metrics_v1",
        "policy": "declared_metric_penalty",
        "penalty": float(penalty),
        "metric_names": metric_names,
    }


def _normalize_diff_error(diff_error: object) -> tuple[str, float, dict]:
    if isinstance(diff_error, str) and diff_error in _PENALTIES:
        reason = diff_error
        score = _PENALTIES[reason]
        return reason, score, {
            "schema": "diff_error_v1",
            "reason": reason,
            "known": True,
            "value_type": "str",
            "penalty": score,
        }

    score = -0.4
    reason = "unknown_diff_error" if isinstance(diff_error, str) else "malformed_diff_error"
    raw = diff_error if isinstance(diff_error, str) else repr(diff_error)
    redacted = _redact_secrets(raw)
    escaped = _escape_diagnostic_controls(redacted)
    detail = _truncate_diagnostic_text(escaped, _DIFF_ERROR_DETAIL_MAX_CHARS)
    return reason, score, {
        "schema": "diff_error_v1",
        "reason": reason,
        "known": False,
        "value_type": type(diff_error).__name__,
        "penalty": score,
        "detail": detail,
        "detail_chars": len(escaped),
        "stored_detail_chars": len(detail),
        "detail_redacted": redacted != raw,
        "detail_escaped": escaped != redacted,
        "detail_truncated": len(detail) < len(escaped),
    }


def _escape_diagnostic_controls(text: str) -> str:
    parts = []
    for char in text:
        category = unicodedata.category(char)
        if category.startswith("C"):
            parts.append(f"\\u{ord(char):04x}")
        else:
            parts.append(char)
    return "".join(parts)


def _evaluator_path_metadata(validate_path: Path, problem_dir: Path) -> dict:
    resolved = validate_path.resolve()
    raw_path = str(resolved)
    try:
        raw_display_path = resolved.relative_to(problem_dir.resolve()).as_posix()
        path_scope = "problem_relative"
    except ValueError:
        raw_display_path = raw_path
        path_scope = "redacted_absolute"
    display_path = redact_sensitive_text(_escape_diagnostic_controls(raw_display_path))
    return {
        "validate_path": display_path,
        "validate_path_scope": path_scope,
        "validate_path_hash": hashlib.sha256(raw_path.encode("utf-8")).hexdigest(),
        "validate_path_redacted": display_path != raw_path,
    }


def _stage_context_metadata(value: object, problem_dir: Path) -> object:
    if isinstance(value, dict):
        sanitized: dict = {}
        for key, item in value.items():
            if key == "validate_path" and isinstance(item, (str, Path)):
                sanitized[key] = _configured_validate_path_display(item, problem_dir)
            elif key == "eval_inputs":
                if isinstance(item, dict) and item.get("schema") == "libreevolve.eval_inputs_provenance.v1":
                    sanitized[key] = copy.deepcopy(item)
                else:
                    sanitized[key] = _eval_inputs_metadata(item)
            else:
                sanitized[key] = _stage_context_metadata(item, problem_dir)
        return sanitized
    if isinstance(value, list):
        return [_stage_context_metadata(item, problem_dir) for item in value]
    return value


def _configured_validate_path_display(value: str | Path, problem_dir: Path) -> str:
    raw = str(value)
    path = Path(raw)
    if not path.is_absolute():
        path = problem_dir / path
    resolved = path.resolve(strict=False)
    try:
        display = resolved.relative_to(problem_dir.resolve()).as_posix()
    except ValueError:
        display = raw
    return redact_sensitive_text(_escape_diagnostic_controls(display))


def _evaluator_path_error_context(path: Path, problem_dir: Path) -> str:
    resolved = path.resolve(strict=False)
    raw_path = str(resolved)
    resolved_root = problem_dir.resolve()
    try:
        raw_display = resolved.relative_to(resolved_root).as_posix()
        scope = "problem_relative"
    except ValueError:
        safe_name = redact_sensitive_text(
            _escape_diagnostic_controls(resolved.name)
        ) or "<unnamed>"
        raw_display = f"<outside-problem>/{safe_name}"
        scope = "outside_problem"
    display = redact_sensitive_text(_escape_diagnostic_controls(raw_display))
    digest = hashlib.sha256(raw_path.encode("utf-8")).hexdigest()[:16]
    return f"{display} (path_scope={scope}, path_hash={digest})"


def _validate_problem_local_evaluator_path(path: Path, problem_dir: Path) -> Path:
    resolved_root = problem_dir.resolve()
    resolved = path.resolve(strict=False)
    context = _evaluator_path_error_context(path, problem_dir)
    if resolved_root != resolved and resolved_root not in resolved.parents:
        raise ValueError(f"Evaluator validate_path escapes problem directory: {context}")
    if not resolved.exists():
        raise ValueError(f"Evaluator validate_path does not exist: {context}")
    if resolved.is_dir():
        init_path = resolved / "__init__.py"
        if not init_path.exists():
            raise ValueError(
                "Evaluator validate_path package directory is missing __init__.py: "
                f"{context}"
            )
        return _validate_problem_local_evaluator_path(init_path, problem_dir)
    if not resolved.is_file():
        raise ValueError(f"Evaluator validate_path is not a file: {context}")
    if resolved.suffix != ".py":
        raise ValueError(f"Evaluator validate_path must be a Python file: {context}")
    return resolved


def _collect_evaluator_artifacts(
    cand_root: Path,
    artifact_dir: Path | None,
    *,
    include: list[str],
    exclude: list[str],
    max_files: int,
    max_bytes: int,
    redact_secrets: bool,
    stage_context: dict,
) -> dict:
    metadata = {
        "enabled": bool(artifact_dir and include),
        "include": include,
        "exclude": exclude,
        "max_files": max_files,
        "max_bytes": max_bytes,
        "redact_secrets": redact_secrets,
        "files": [],
        "skipped": [],
        "total_bytes": 0,
        "path_root": "artifact_dir_parent",
        "byte_limit_policy": "precheck_source_size_then_store",
    }
    if not artifact_dir or not include:
        return metadata
    collection_id = uuid4().hex
    metadata["collection_id"] = collection_id
    stage_name = str(stage_context.get("name", "stage"))
    sample_index = stage_context.get("sample_index")
    attempt = stage_context.get("attempt")
    metadata["stage"] = {
        "name": stage_name,
        "sample_index": sample_index,
        "attempt": attempt,
    }
    target_root = artifact_dir / collection_id
    metadata["artifact_dir_name"] = artifact_dir.name
    matched, safety_skips = _matching_artifact_paths(cand_root, include, exclude)
    metadata["skipped"].extend(safety_skips)
    for path in matched:
        rel = path.relative_to(cand_root).as_posix()
        if len(metadata["files"]) >= max_files:
            metadata["skipped"].append({"path": rel, "reason": "max_files"})
            continue
        try:
            source_bytes = path.stat().st_size
        except OSError as exc:
            metadata["skipped"].append(
                {
                    "path": rel,
                    "reason": "stat_error",
                    "message": redact_sensitive_text(str(exc)),
                }
            )
            continue
        if metadata["total_bytes"] + source_bytes > max_bytes:
            metadata["skipped"].append(
                {"path": rel, "reason": "max_bytes", "source_bytes": source_bytes}
            )
            continue
        try:
            raw = path.read_bytes()
        except OSError as exc:
            metadata["skipped"].append(
                {
                    "path": rel,
                    "reason": "read_error",
                    "message": redact_sensitive_text(str(exc)),
                }
            )
            continue
        stored_raw, redacted, redaction_status = _artifact_stored_bytes(
            raw, redact_secrets
        )
        size = len(stored_raw)
        if metadata["total_bytes"] + size > max_bytes:
            metadata["skipped"].append(
                {
                    "path": rel,
                    "reason": "max_bytes_after_redaction",
                    "bytes": size,
                    "source_bytes": source_bytes,
                }
            )
            continue
        dest = target_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(stored_raw)
        metadata["total_bytes"] += size
        artifact_path = (Path(artifact_dir.name) / collection_id / rel).as_posix()
        artifact_record = {
            "path": rel,
            "artifact_path": artifact_path,
            "artifact_path_root": "artifact_dir_parent",
            "artifact_relative_path": (Path(collection_id) / rel).as_posix(),
            "bytes": size,
            "source_bytes": source_bytes,
            "sha256": hashlib.sha256(stored_raw).hexdigest(),
            "redacted": redacted,
            "redaction_status": redaction_status,
            "stage_name": stage_name,
            "sample_index": sample_index,
            "attempt": attempt,
        }
        artifact_record.update(_artifact_content_excerpt_metadata(stored_raw))
        metadata["files"].append(artifact_record)
    return metadata


def _artifact_content_excerpt_metadata(stored_raw: bytes) -> dict:
    try:
        text = stored_raw.decode("utf-8")
    except UnicodeDecodeError:
        return {
            "content_excerpt_policy": "stored_utf8_artifact_excerpt_v1",
            "content_excerpt_status": "binary_or_non_utf8",
            "content_excerpt_chars": 0,
            "content_excerpt_truncated": False,
            "content_excerpt_max_chars": MAX_ARTIFACT_CONTENT_EXCERPT_CHARS,
        }
    excerpt = _truncate_diagnostic_text(text, MAX_ARTIFACT_CONTENT_EXCERPT_CHARS)
    return {
        "content_excerpt_policy": "stored_utf8_artifact_excerpt_v1",
        "content_excerpt_status": "included",
        "content_excerpt": excerpt,
        "content_excerpt_chars": len(excerpt),
        "content_excerpt_truncated": len(excerpt) < len(text),
        "content_excerpt_max_chars": MAX_ARTIFACT_CONTENT_EXCERPT_CHARS,
        "content_sha256_scope": "stored_artifact_bytes",
    }


def _artifact_stored_bytes(raw: bytes, redact_secrets: bool) -> tuple[bytes, bool, str]:
    if not redact_secrets:
        return raw, False, "disabled"
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw, False, "binary_or_non_utf8"
    redacted_text = _redact_secrets(text)
    redacted = redacted_text != text
    return redacted_text.encode("utf-8"), redacted, "redacted" if redacted else "unchanged"


def _matching_artifact_paths(cand_root: Path, include: list[str], exclude: list[str]) -> tuple[list[Path], list[dict]]:
    paths = []
    skipped = []
    for path in sorted(cand_root.rglob("*"), key=lambda p: p.as_posix()):
        rel = path.relative_to(cand_root).as_posix()
        if not any(_artifact_glob_matches(rel, pattern) for pattern in include):
            continue
        if any(_artifact_glob_matches(rel, pattern) for pattern in exclude):
            continue
        if path.is_symlink():
            skipped.append({"path": rel, "reason": "link_not_followed"})
            continue
        if not path.is_file():
            skipped.append({"path": rel, "reason": "not_file"})
            continue
        try:
            resolved = path.resolve(strict=True)
            resolved_root = cand_root.resolve(strict=True)
        except OSError as exc:
            skipped.append(
                {
                    "path": rel,
                    "reason": "resolve_error",
                    "message": redact_sensitive_text(str(exc)),
                }
            )
            continue
        if resolved != resolved_root and resolved_root not in resolved.parents:
            skipped.append({"path": rel, "reason": "path_escape"})
            continue
        paths.append(path)
    return paths, skipped


def _artifact_glob_matches(rel_path: str, pattern: str) -> bool:
    rel_parts = rel_path.split("/")
    pattern_parts = pattern.replace("\\", "/").split("/")
    return _artifact_glob_match_segments(pattern_parts, rel_parts)


def _artifact_glob_match_segments(pattern_parts: list[str], rel_parts: list[str]) -> bool:
    if not pattern_parts:
        return not rel_parts
    head = pattern_parts[0]
    tail = pattern_parts[1:]
    if head == "**":
        return _artifact_glob_match_segments(tail, rel_parts) or (
            bool(rel_parts) and _artifact_glob_match_segments(pattern_parts, rel_parts[1:])
        )
    if not rel_parts:
        return False
    return fnmatch.fnmatchcase(rel_parts[0], head) and _artifact_glob_match_segments(
        tail,
        rel_parts[1:],
    )


def _validator_env(allowlist: list[str]) -> dict[str, str]:
    env = {"PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    for name in [*_DEFAULT_VALIDATOR_ENV_NAMES, *allowlist]:
        found = _find_env(name)
        if found is not None:
            key, value = found
            env[key] = value
    return env


def _stage_context_with_rng_seed(stage_context: dict) -> dict:
    seed = stage_context.get("seed")
    if seed is None:
        return stage_context
    rng_seed = _stage_rng_seed(seed)
    if stage_context.get("rng_seed") == rng_seed:
        return stage_context
    enriched = dict(stage_context)
    enriched["rng_seed"] = rng_seed
    return enriched


def _stage_rng_seed(seed: object) -> int:
    if isinstance(seed, bool):
        raise ValueError("stage seed must not be boolean")
    if isinstance(seed, int) and 0 <= seed <= 4_294_967_295:
        return seed
    payload = json.dumps(seed, sort_keys=True, separators=(",", ":"), allow_nan=False)
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big")


def _validator_env_metadata(env: dict[str, str], allowlist: list[str]) -> dict:
    return {
        "policy": "minimal_allowlist",
        "default_keys": sorted(
            key for key in env if key.upper() in set(_DEFAULT_VALIDATOR_ENV_NAMES)
        ),
        "allowlist": sorted(allowlist),
        "provided_keys": sorted(env),
        "values_redacted": True,
    }


def _find_env(name: str) -> tuple[str, str] | None:
    if name in os.environ:
        return name, os.environ[name]
    upper = name.upper()
    for key, value in os.environ.items():
        if key.upper() == upper:
            return key, value
    return None


def _redact_secrets(text: str) -> str:
    if not text:
        return text
    return redact_sensitive_text(text)


_EVALUATOR_SOURCE_HASH_CHUNK_BYTES = 64 * 1024
_EVALUATOR_COMPANION_MAX_FILES = 128
_EVALUATOR_COMPANION_MAX_FILE_BYTES = 5 * 1024 * 1024
_EVALUATOR_COMPANION_INCLUDE_SUFFIXES = frozenset(
    {".py", ".json", ".jsonl", ".yaml", ".yml", ".txt", ".csv", ".tsv", ".md"}
)
_EVALUATOR_COMPANION_EXCLUDED_DIRS = frozenset(
    {".git", ".mypy_cache", ".pytest_cache", "__pycache__", "runs"}
)
_EVALUATOR_DECLARED_DATA_MAX_FILES = 128
_EVALUATOR_DECLARED_DATA_MAX_FILE_BYTES = 5 * 1024 * 1024
_EVALUATOR_DEPENDENCY_POLICY = "declared_problem_local_evaluator_dependencies_v1"


def _evaluator_entrypoint_specs(
    problem: Problem,
    stages: list[dict] | None = None,
    *,
    evaluator_data_include: list[str] | None = None,
    evaluator_data_exclude: list[str] | None = None,
) -> list[tuple[Path, dict]]:
    stage_configs = stages or []
    data_include = [] if evaluator_data_include is None else evaluator_data_include
    data_exclude = [] if evaluator_data_exclude is None else evaluator_data_exclude
    _validate_artifact_glob_list("evaluator_data_include", data_include)
    _validate_artifact_glob_list("evaluator_data_exclude", data_exclude)
    if not stage_configs:
        path = _validate_problem_local_evaluator_path(
            problem.validate_path, problem.problem_dir
        )
        return [
            (
                path,
                {
                    "role": "default",
                    "data_include": list(data_include),
                    "data_exclude": list(data_exclude),
                },
            )
        ]

    specs: list[tuple[Path, dict]] = []
    for index, stage in enumerate(stage_configs):
        if stage.get("mode") == "embedded_evaluate":
            continue
        raw_path = stage.get("validate_path")
        if raw_path is None:
            path = problem.validate_path
        else:
            path = Path(str(raw_path))
            if not path.is_absolute():
                path = problem.problem_dir / path
        resolved = _validate_problem_local_evaluator_path(path, problem.problem_dir)
        specs.append(
            (
                resolved,
                {
                    "role": "stage",
                    "stage_name": str(stage.get("name", f"stage_{index}")),
                    "stage_index": index,
                    "configured_validate_path": None
                    if raw_path is None
                    else str(raw_path),
                    "data_include": list(stage.get("data_include", data_include)),
                    "data_exclude": list(stage.get("data_exclude", data_exclude)),
                },
            )
        )
    return specs


def preflight_evaluator_contracts(
    problem: Problem,
    stages: list[dict] | None = None,
    validator_env_allowlist: list[str] | None = None,
    validator_network_policy: str = "host",
    evaluator_data_include: list[str] | None = None,
    evaluator_data_exclude: list[str] | None = None,
) -> list[dict]:
    """Validate evaluator entrypoints before run artifacts are created or replaced."""
    allowlist = canonicalize_env_var_allowlist(
        "validator_env_allowlist",
        validator_env_allowlist or [],
    )
    network_policy = _validate_validator_network_policy(validator_network_policy)
    records: list[dict] = []
    for path, record_kwargs in _evaluator_entrypoint_specs(
        problem,
        stages,
        evaluator_data_include=evaluator_data_include,
        evaluator_data_exclude=evaluator_data_exclude,
    ):
        path_context = _evaluator_path_error_context(path, problem.problem_dir)
        allowed_dependency_paths = _evaluator_allowed_dependency_paths(
            path,
            problem.problem_dir,
            {
                "evaluator_data": _evaluator_data_context(
                    _evaluator_declared_data_sources(
                        path,
                        problem.problem_dir,
                        include=list(record_kwargs.get("data_include", [])),
                        exclude=list(record_kwargs.get("data_exclude", [])),
                    )
                )
            },
        )
        _preflight_evaluator_module(
            path,
            problem.problem_dir,
            allowlist,
            network_policy,
            path_context,
            allowed_dependency_paths,
        )
        records.append(
            _evaluator_source_record(
                path,
                problem.problem_dir,
                **record_kwargs,
            )
        )
    return records


def _evaluator_source_record(
    path: Path,
    problem_dir: Path,
    *,
    role: str,
    stage_name: str | None = None,
    stage_index: int | None = None,
    configured_validate_path: str | None = None,
    data_include: list[str] | None = None,
    data_exclude: list[str] | None = None,
) -> dict:
    record = {
        "role": role,
        "source_type": "python",
    }
    record.update(_evaluator_source_path_metadata(path, problem_dir))
    record.update(_evaluator_source_hash_record(path))
    record["companion_sources"] = _evaluator_companion_sources(path, problem_dir)
    record["declared_data_sources"] = _evaluator_declared_data_sources(
        path,
        problem_dir,
        include=[] if data_include is None else data_include,
        exclude=[] if data_exclude is None else data_exclude,
    )
    record["dependency_policy"] = {
        "policy": _EVALUATOR_DEPENDENCY_POLICY,
        "problem_local_files": (
            "entrypoint plus captured companion_sources plus captured "
            "declared_data_sources"
        ),
        "runtime_enforced": True,
        "outside_problem_policy": "not_constrained_by_this_policy",
    }
    if stage_name is not None:
        record["stage_name"] = stage_name
    if stage_index is not None:
        record["stage_index"] = stage_index
    if configured_validate_path is not None:
        record.update(
            _configured_evaluator_source_path_metadata(
                configured_validate_path, problem_dir
            )
        )
    return record


def _evaluator_source_hash_record(path: Path) -> dict:
    digest = hashlib.sha256()
    total = 0
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(_EVALUATOR_SOURCE_HASH_CHUNK_BYTES), b""):
                total += len(chunk)
                digest.update(chunk)
    except OSError as exc:
        return {
            "status": "read_error",
            "reason": "read_error",
            "error_type": exc.__class__.__name__,
            "error": _redact_secrets(str(exc)),
            "source_hash_policy": "streamed_full_file",
            "hash_chunk_bytes": _EVALUATOR_SOURCE_HASH_CHUNK_BYTES,
        }
    return {
        "status": "ok",
        "sha256": digest.hexdigest(),
        "bytes": total,
        "source_hash_policy": "streamed_full_file",
        "hash_chunk_bytes": _EVALUATOR_SOURCE_HASH_CHUNK_BYTES,
    }


def _evaluator_companion_sources(path: Path, problem_dir: Path) -> dict:
    root = path.parent
    resolved_root = root.resolve()
    resolved_problem = problem_dir.resolve()
    root_rel = resolved_root.relative_to(resolved_problem).as_posix()
    files: list[dict] = []
    skipped: list[dict] = []
    total_bytes = 0
    for candidate in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        rel_to_root = candidate.relative_to(root)
        if any(
            part in _EVALUATOR_COMPANION_EXCLUDED_DIRS for part in rel_to_root.parts
        ):
            continue
        rel = candidate.relative_to(resolved_problem).as_posix()
        display_rel = redact_sensitive_text(_escape_diagnostic_controls(rel))
        if candidate == path:
            continue
        if candidate.is_symlink():
            skipped.append({"path": display_rel, "reason": "link_not_followed"})
            continue
        if not candidate.is_file():
            continue
        if candidate.suffix.lower() not in _EVALUATOR_COMPANION_INCLUDE_SUFFIXES:
            continue
        try:
            resolved = candidate.resolve(strict=True)
        except OSError as exc:
            skipped.append(
                {
                    "path": display_rel,
                    "reason": "resolve_error",
                    "error": _redact_secrets(str(exc)),
                }
            )
            continue
        if resolved != resolved_problem and resolved_problem not in resolved.parents:
            skipped.append({"path": display_rel, "reason": "path_escape"})
            continue
        if len(files) >= _EVALUATOR_COMPANION_MAX_FILES:
            skipped.append({"path": display_rel, "reason": "max_files"})
            continue
        try:
            source_bytes = resolved.stat().st_size
        except OSError as exc:
            skipped.append(
                {
                    "path": display_rel,
                    "reason": "stat_error",
                    "error": _redact_secrets(str(exc)),
                }
            )
            continue
        if source_bytes > _EVALUATOR_COMPANION_MAX_FILE_BYTES:
            skipped.append(
                {
                    "path": display_rel,
                    "reason": "max_file_bytes",
                    "bytes": source_bytes,
                }
            )
            continue
        record = _evaluator_companion_source_record(resolved, problem_dir)
        if record.get("status") == "ok":
            total_bytes += int(record.get("bytes", 0))
        files.append(record)
    return {
        "policy": "bounded_validator_directory_companion_sources_v1",
        "root": redact_sensitive_text(_escape_diagnostic_controls(root_rel)),
        "root_scope": "problem_relative",
        "include_suffixes": sorted(_EVALUATOR_COMPANION_INCLUDE_SUFFIXES),
        "excluded_dirs": sorted(_EVALUATOR_COMPANION_EXCLUDED_DIRS),
        "max_files": _EVALUATOR_COMPANION_MAX_FILES,
        "max_file_bytes": _EVALUATOR_COMPANION_MAX_FILE_BYTES,
        "hash_chunk_bytes": _EVALUATOR_SOURCE_HASH_CHUNK_BYTES,
        "files": files,
        "skipped": skipped,
        "file_count": len(files),
        "skipped_count": len(skipped),
        "total_bytes": total_bytes,
        "aggregate_sha256": _evaluator_companion_aggregate_hash(files),
    }


def _evaluator_companion_source_record(path: Path, problem_dir: Path) -> dict:
    record = _evaluator_companion_path_metadata(path, problem_dir)
    record.update(_evaluator_source_hash_record(path))
    record["source_type"] = "python" if path.suffix.lower() == ".py" else "data"
    return record


def _evaluator_companion_path_metadata(path: Path, problem_dir: Path) -> dict:
    raw_path = str(path)
    relative_path = path.relative_to(problem_dir.resolve()).as_posix()
    display_path = redact_sensitive_text(_escape_diagnostic_controls(relative_path))
    return {
        "path": display_path,
        "path_scope": "problem_relative",
        "path_hash": hashlib.sha256(raw_path.encode("utf-8")).hexdigest(),
        "path_redacted": display_path != raw_path,
        "relative_path": display_path,
        "relative_path_hash": hashlib.sha256(
            relative_path.encode("utf-8")
        ).hexdigest(),
        "relative_path_redacted": display_path != relative_path,
    }


def _evaluator_companion_aggregate_hash(records: list[dict]) -> str:
    payload = strict_json_dumps(records)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _evaluator_declared_data_sources(
    path: Path,
    problem_dir: Path,
    *,
    include: list[str],
    exclude: list[str],
) -> dict:
    root = path.parent
    resolved_root = root.resolve()
    resolved_problem = problem_dir.resolve()
    root_rel = resolved_root.relative_to(resolved_problem).as_posix()
    files: list[dict] = []
    skipped: list[dict] = []
    total_bytes = 0
    if not include:
        return {
            "enabled": False,
            "policy": "declared_evaluator_data_files_v1",
            "root": redact_sensitive_text(_escape_diagnostic_controls(root_rel)),
            "root_scope": "problem_relative",
            "include": [],
            "exclude": list(exclude),
            "max_files": _EVALUATOR_DECLARED_DATA_MAX_FILES,
            "max_file_bytes": _EVALUATOR_DECLARED_DATA_MAX_FILE_BYTES,
            "hash_chunk_bytes": _EVALUATOR_SOURCE_HASH_CHUNK_BYTES,
            "files": [],
            "skipped": [],
            "file_count": 0,
            "skipped_count": 0,
            "total_bytes": 0,
            "aggregate_sha256": _hash_manifest_records([]),
        }
    for candidate in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        rel_to_root = candidate.relative_to(root).as_posix()
        rel_problem = candidate.relative_to(resolved_problem).as_posix()
        display_rel = redact_sensitive_text(_escape_diagnostic_controls(rel_problem))
        if not any(_artifact_glob_matches(rel_to_root, pattern) for pattern in include):
            continue
        if any(_artifact_glob_matches(rel_to_root, pattern) for pattern in exclude):
            skipped.append({"path": display_rel, "reason": "excluded"})
            continue
        if candidate == path:
            skipped.append({"path": display_rel, "reason": "entrypoint"})
            continue
        if candidate.is_symlink():
            skipped.append({"path": display_rel, "reason": "link_not_followed"})
            continue
        if not candidate.is_file():
            continue
        try:
            resolved = candidate.resolve(strict=True)
        except OSError as exc:
            skipped.append(
                {
                    "path": display_rel,
                    "reason": "resolve_error",
                    "error": _redact_secrets(str(exc)),
                }
            )
            continue
        if resolved != resolved_problem and resolved_problem not in resolved.parents:
            skipped.append({"path": display_rel, "reason": "path_escape"})
            continue
        if len(files) >= _EVALUATOR_DECLARED_DATA_MAX_FILES:
            skipped.append({"path": display_rel, "reason": "max_files"})
            continue
        try:
            source_bytes = resolved.stat().st_size
        except OSError as exc:
            skipped.append(
                {
                    "path": display_rel,
                    "reason": "stat_error",
                    "error": _redact_secrets(str(exc)),
                }
            )
            continue
        if source_bytes > _EVALUATOR_DECLARED_DATA_MAX_FILE_BYTES:
            skipped.append(
                {
                    "path": display_rel,
                    "reason": "max_file_bytes",
                    "bytes": source_bytes,
                }
            )
            continue
        record = _evaluator_companion_source_record(resolved, problem_dir)
        safe_data_path = redact_sensitive_text(_escape_diagnostic_controls(rel_to_root))
        record["data_path"] = safe_data_path
        record["data_path_hash"] = hashlib.sha256(
            rel_to_root.encode("utf-8")
        ).hexdigest()
        record["data_path_redacted"] = safe_data_path != rel_to_root
        if record.get("status") == "ok":
            total_bytes += int(record.get("bytes", 0))
        files.append(record)
    return {
        "enabled": True,
        "policy": "declared_evaluator_data_files_v1",
        "root": redact_sensitive_text(_escape_diagnostic_controls(root_rel)),
        "root_scope": "problem_relative",
        "include": list(include),
        "exclude": list(exclude),
        "max_files": _EVALUATOR_DECLARED_DATA_MAX_FILES,
        "max_file_bytes": _EVALUATOR_DECLARED_DATA_MAX_FILE_BYTES,
        "hash_chunk_bytes": _EVALUATOR_SOURCE_HASH_CHUNK_BYTES,
        "files": files,
        "skipped": skipped,
        "file_count": len(files),
        "skipped_count": len(skipped),
        "total_bytes": total_bytes,
        "aggregate_sha256": _hash_manifest_records(files),
    }


def _evaluator_data_context(declared: dict) -> dict:
    return {
        "enabled": bool(declared.get("enabled")),
        "policy": declared.get("policy"),
        "root": declared.get("root"),
        "root_scope": declared.get("root_scope"),
        "include": list(declared.get("include", [])),
        "exclude": list(declared.get("exclude", [])),
        "files": [
            {
                "path": record["data_path"],
                "problem_relative_path": record["relative_path"],
            }
            for record in declared.get("files", [])
            if isinstance(record.get("data_path"), str)
            and isinstance(record.get("relative_path"), str)
        ],
        "file_count": int(declared.get("file_count", 0)),
        "skipped_count": int(declared.get("skipped_count", 0)),
    }


def _evaluator_allowed_dependency_paths(
    path: Path,
    problem_dir: Path,
    stage_context: dict,
) -> list[Path]:
    evaluator_data = stage_context.get("evaluator_data")
    include: list[str] = []
    exclude: list[str] = []
    if isinstance(evaluator_data, dict):
        include = [
            item for item in evaluator_data.get("include", []) if isinstance(item, str)
        ]
        exclude = [
            item for item in evaluator_data.get("exclude", []) if isinstance(item, str)
        ]
    allowed = {
        path.resolve(),
        *_evaluator_companion_allowed_paths(path, problem_dir),
        *_evaluator_declared_data_allowed_paths(
            path,
            problem_dir,
            include=include,
            exclude=exclude,
        ),
    }
    return sorted(allowed, key=lambda item: str(item))


def _evaluator_dependency_metadata(
    path: Path,
    problem_dir: Path,
    stage_context: dict,
) -> dict:
    allowed = _evaluator_allowed_dependency_paths(path, problem_dir, stage_context)
    resolved_problem = problem_dir.resolve()
    files = []
    for item in allowed:
        rel = item.relative_to(resolved_problem).as_posix()
        display = redact_sensitive_text(_escape_diagnostic_controls(rel))
        files.append(
            {
                "path": display,
                "path_hash": hashlib.sha256(str(item).encode("utf-8")).hexdigest(),
                "path_redacted": display != rel,
            }
        )
    return {
        "policy": _EVALUATOR_DEPENDENCY_POLICY,
        "allowed_scope": "problem_local_files_in_manifest_evaluator_provenance",
        "outside_problem_policy": "not_constrained_by_this_policy",
        "files": files,
        "file_count": len(files),
    }


def _evaluator_companion_allowed_paths(path: Path, problem_dir: Path) -> list[Path]:
    root = path.parent
    resolved_problem = problem_dir.resolve()
    paths: list[Path] = []
    for candidate in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        rel_to_root = candidate.relative_to(root)
        if any(
            part in _EVALUATOR_COMPANION_EXCLUDED_DIRS for part in rel_to_root.parts
        ):
            continue
        if candidate == path or candidate.is_symlink() or not candidate.is_file():
            continue
        if candidate.suffix.lower() not in _EVALUATOR_COMPANION_INCLUDE_SUFFIXES:
            continue
        try:
            resolved = candidate.resolve(strict=True)
        except OSError:
            continue
        if resolved != resolved_problem and resolved_problem not in resolved.parents:
            continue
        if len(paths) >= _EVALUATOR_COMPANION_MAX_FILES:
            continue
        try:
            source_bytes = resolved.stat().st_size
        except OSError:
            continue
        if source_bytes > _EVALUATOR_COMPANION_MAX_FILE_BYTES:
            continue
        paths.append(resolved)
    return paths


def _evaluator_declared_data_allowed_paths(
    path: Path,
    problem_dir: Path,
    *,
    include: list[str],
    exclude: list[str],
) -> list[Path]:
    if not include:
        return []
    root = path.parent
    resolved_problem = problem_dir.resolve()
    paths: list[Path] = []
    for candidate in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        rel_to_root = candidate.relative_to(root).as_posix()
        if not any(_artifact_glob_matches(rel_to_root, pattern) for pattern in include):
            continue
        if any(_artifact_glob_matches(rel_to_root, pattern) for pattern in exclude):
            continue
        if candidate == path or candidate.is_symlink() or not candidate.is_file():
            continue
        try:
            resolved = candidate.resolve(strict=True)
        except OSError:
            continue
        if resolved != resolved_problem and resolved_problem not in resolved.parents:
            continue
        if len(paths) >= _EVALUATOR_DECLARED_DATA_MAX_FILES:
            continue
        try:
            source_bytes = resolved.stat().st_size
        except OSError:
            continue
        if source_bytes > _EVALUATOR_DECLARED_DATA_MAX_FILE_BYTES:
            continue
        paths.append(resolved)
    return paths


def _hash_manifest_records(records: list[dict]) -> str:
    payload = strict_json_dumps(records)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _evaluator_source_path_metadata(path: Path, problem_dir: Path) -> dict:
    raw_path = str(path)
    relative_path = path.relative_to(problem_dir.resolve()).as_posix()
    display_path = redact_sensitive_text(_escape_diagnostic_controls(relative_path))
    record = {
        "path": display_path,
        "path_scope": "problem_relative",
        "path_hash": hashlib.sha256(raw_path.encode("utf-8")).hexdigest(),
        "path_redacted": display_path != raw_path,
        "relative_path": display_path,
        "relative_path_hash": hashlib.sha256(
            relative_path.encode("utf-8")
        ).hexdigest(),
        "relative_path_redacted": display_path != relative_path,
    }
    return record


def _configured_evaluator_source_path_metadata(
    configured_validate_path: str, problem_dir: Path
) -> dict:
    display = _configured_validate_path_display(configured_validate_path, problem_dir)
    safe_display = redact_sensitive_text(display)
    record = {
        "configured_validate_path": safe_display,
        "configured_validate_path_hash": hashlib.sha256(
            configured_validate_path.encode("utf-8")
        ).hexdigest(),
        "configured_validate_path_redacted": safe_display
        != configured_validate_path,
    }
    return record


def _preflight_evaluator_module(
    path: Path,
    problem_dir: Path,
    validator_env_allowlist: list[str],
    validator_network_policy: str,
    path_context: str,
    allowed_dependency_paths: list[Path],
) -> None:
    env = _validator_env(validator_env_allowlist)
    with tempfile.TemporaryDirectory(prefix="libreevolve-preflight-") as tmp:
        result = _run_validator_process(
            [
                sys.executable,
                "-c",
                _PREFLIGHT_RUNNER,
                str(path),
                str(problem_dir),
                json.dumps([str(item) for item in allowed_dependency_paths]),
            ],
            cwd=Path(tmp),
            timeout_sec=_PREFLIGHT_TIMEOUT_SEC,
            env=env,
            validator_network_policy=validator_network_policy,
        )
    if result.timed_out:
        raise ValueError(f"Evaluator preflight failed for {path_context}: timeout")
    message = _preflight_process_message(result)
    if result.returncode != 0:
        raise ValueError(f"Evaluator preflight failed for {path_context}: {message}")
    if message is None:
        return
    raise ValueError(
        f"Evaluator preflight failed for {path_context}: malformed preflight result"
    )


def _preflight_process_message(result: _ValidatorProcessResult) -> str | None:
    for line in reversed((result.stdout or "").splitlines()):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            break
        if isinstance(payload, dict) and payload.get("ok") is True:
            return None
        if isinstance(payload, dict) and isinstance(payload.get("message"), str):
            return payload["message"] or "failed"
        break
    stderr = _redact_secrets(result.stderr.strip())
    stdout = _redact_secrets(result.stdout.strip())
    if stderr:
        return f"returncode_{result.returncode}: {stderr}"
    if stdout:
        return f"returncode_{result.returncode}: {stdout}"
    return f"returncode_{result.returncode}"


def _read_evaluator_result(path: Path) -> object:
    if not path.exists():
        raise ValueError("evaluator result file was not written")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("evaluator result envelope must be an object")
    if payload.get("ok") is not True:
        message = payload.get("message")
        if isinstance(message, str) and message:
            raise ValueError(message)
        error = payload.get("error")
        if isinstance(error, str) and error:
            raise ValueError(error)
        raise ValueError("evaluator result transport failed")
    if "result" not in payload:
        raise ValueError("evaluator result envelope is missing result")
    return payload["result"]


def _retry_attempt_record(
    result: EvaluationResult,
    attempt: int,
    context: dict,
    problem_dir: Path,
    *,
    threshold: float | None = None,
    threshold_passed: bool = True,
    threshold_result: dict | None = None,
) -> dict:
    record = {
        "attempt": attempt,
        "passed": result.is_valid and threshold_passed,
        "local_valid": result.is_valid,
        "threshold": threshold,
        "threshold_passed": threshold_passed,
        "fitness": result.fitness,
        "metrics": dict(result.metrics),
        "stdout": result.stdout,
        "stderr": result.stderr,
        "error": result.error,
        "elapsed_sec": result.elapsed_sec,
        "stage": _stage_context_metadata(context, problem_dir),
        "stages": [stage.to_dict() for stage in result.stages],
    }
    if threshold_result is not None:
        record["threshold_result"] = threshold_result
        record["metric_thresholds"] = threshold_result["metric_thresholds"]
        record["artifact_output_checks"] = threshold_result["artifact_output_checks"]
    return record


def _configured_stage_result_record(
    *,
    name: str,
    stage_index: int,
    result: EvaluationResult,
    min_score: object,
    threshold_passed: bool,
    threshold_result: dict,
    hypothesis_test_result: dict,
    passed: bool,
) -> dict:
    return {
        "name": name,
        "stage_index": stage_index,
        "passed": passed,
        "local_valid": result.is_valid,
        "threshold": None if min_score is None else float(min_score),
        "threshold_passed": threshold_passed,
        "threshold_result": threshold_result,
        "metric_thresholds": threshold_result["metric_thresholds"],
        "artifact_output_checks": threshold_result["artifact_output_checks"],
        "hypothesis_test_result": hypothesis_test_result,
        "fitness": result.fitness,
        "metrics": dict(result.metrics),
        "stdout": result.stdout,
        "stderr": result.stderr,
        "error": result.error,
        "elapsed_sec": result.elapsed_sec,
        "stages": [stage.to_dict() for stage in result.stages],
        "metadata": copy.deepcopy(result.metadata),
    }


def _stage_threshold_result(
    result: "EvaluationResult",
    min_score: object,
    metric_thresholds: object,
    stage_policy: object = None,
) -> dict:
    score_threshold = None
    checks: list[dict] = []
    if min_score is not None:
        threshold = float(min_score)
        passed = result.fitness >= threshold
        score_threshold = {
            "metric": "fitness",
            "value": result.fitness,
            "min": threshold,
            "passed": passed,
        }
        checks.append(score_threshold)
    for metric, spec in sorted(_normalized_metric_thresholds(metric_thresholds).items()):
        value = result.metrics.get(metric)
        check = {
            "metric": metric,
            "value": value,
            "min": spec.get("min"),
            "max": spec.get("max"),
            "passed": False,
        }
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            check["reason"] = "missing_or_non_numeric_metric"
        else:
            numeric = float(value)
            check["value"] = numeric
            min_ok = "min" not in spec or numeric >= float(spec["min"])
            max_ok = "max" not in spec or numeric <= float(spec["max"])
            check["passed"] = bool(min_ok and max_ok)
            if not min_ok:
                check["reason"] = "below_min"
            elif not max_ok:
                check["reason"] = "above_max"
        checks.append(check)
    artifact_checks = _artifact_output_threshold_checks(result, stage_policy)
    checks.extend(artifact_checks)
    return {
        "passed": all(check["passed"] for check in checks),
        "score_threshold": score_threshold,
        "metric_thresholds": checks[1 : 1 + len(_normalized_metric_thresholds(metric_thresholds))]
        if score_threshold is not None
        else checks[: len(_normalized_metric_thresholds(metric_thresholds))],
        "artifact_output_checks": artifact_checks,
    }


def _stage_hypothesis_test_result(
    result: "EvaluationResult",
    hypothesis_test: object,
) -> dict:
    if not isinstance(hypothesis_test, dict):
        return {
            "configured": False,
            "passed": True,
            "test_name": None,
        }
    test_name = str(hypothesis_test.get("type", "one_sided_lower_confidence_bound"))
    if test_name == "binomial_success_rate":
        return _stage_binomial_success_rate_result(result, hypothesis_test)
    return _stage_lower_confidence_bound_result(result, hypothesis_test)


def _stage_lower_confidence_bound_result(
    result: "EvaluationResult",
    hypothesis_test: dict,
) -> dict:
    metric = str(hypothesis_test.get("metric", "fitness"))
    threshold = float(hypothesis_test["min"])
    confidence = float(hypothesis_test.get("confidence", 0.95))
    min_samples = int(hypothesis_test.get("min_samples", 2))
    sequential_stopping = hypothesis_test.get("sequential_stopping") is True
    observations = _hypothesis_test_observations(result, metric)
    values = [item["value"] for item in observations]
    sequential_decision = result.metadata.get("hypothesis_test_sequential_stopping")
    if not isinstance(sequential_decision, dict):
        sequential_decision = None
    record: dict = {
        "configured": True,
        "test_name": "one_sided_lower_confidence_bound",
        "metric": metric,
        "min": threshold,
        "confidence": confidence,
        "min_samples": min_samples,
        "sample_count": len(values),
        "observations": observations,
        "sequential_stopping": sequential_stopping,
        "sequential_stop": (
            {
                "enabled": True,
                "stopped_early": sequential_decision.get("stopped_early") is True,
                "stop_reason": sequential_decision.get("stop_reason"),
                "evaluated_samples": sequential_decision.get("evaluated_samples"),
                "planned_samples": sequential_decision.get("planned_samples"),
            }
            if sequential_decision is not None
            else {
                "enabled": sequential_stopping,
                "stopped_early": False,
                "stop_reason": None,
                "evaluated_samples": len(values),
                "planned_samples": result.metadata.get("planned_sample_count"),
            }
        ),
        "passed": False,
    }
    if len(values) < min_samples:
        record["reason"] = "insufficient_samples"
        return record
    mean = sum(values) / len(values)
    if len(values) > 1:
        variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
        sample_stddev = math.sqrt(max(0.0, variance))
    else:
        sample_stddev = 0.0
    standard_error = sample_stddev / math.sqrt(len(values))
    z = NormalDist().inv_cdf(confidence)
    lower_bound = mean - z * standard_error
    if standard_error == 0.0:
        z_score = None
        p_value = 0.0 if mean >= threshold else 1.0
    else:
        z_score = (mean - threshold) / standard_error
        p_value = 1.0 - NormalDist().cdf(z_score)
    record.update(
        {
            "mean": mean,
            "sample_stddev": sample_stddev,
            "standard_error": standard_error,
            "z_critical": z,
            "lower_bound": lower_bound,
            "confidence_interval": {
                "kind": "one_sided_lower",
                "lower": lower_bound,
                "upper": None,
            },
            "z_score": z_score,
            "p_value": p_value,
            "passed": lower_bound >= threshold,
        }
    )
    error_budget_result = _stage_hypothesis_error_budget_result(
        hypothesis_test,
        confidence=confidence,
        z_critical=z,
        standard_error=standard_error,
    )
    record["error_budget"] = error_budget_result
    if record["passed"] and not error_budget_result["passed"]:
        record["passed"] = False
        record["reason"] = error_budget_result["reason"]
    if not record["passed"]:
        record.setdefault("reason", "lower_confidence_bound_below_min")
    return record


def _stage_binomial_success_rate_result(
    result: "EvaluationResult",
    hypothesis_test: dict,
) -> dict:
    metric = str(hypothesis_test.get("metric", "is_valid"))
    min_success_rate = float(hypothesis_test["min_success_rate"])
    success_threshold = hypothesis_test.get("success_threshold")
    confidence = float(hypothesis_test.get("confidence", 0.95))
    min_samples = int(hypothesis_test.get("min_samples", 2))
    sequential_stopping = hypothesis_test.get("sequential_stopping") is True
    observations = _hypothesis_test_success_observations(
        result,
        metric,
        success_threshold=float(success_threshold)
        if isinstance(success_threshold, (int, float))
        and not isinstance(success_threshold, bool)
        else None,
    )
    sequential_decision = result.metadata.get("hypothesis_test_sequential_stopping")
    if not isinstance(sequential_decision, dict):
        sequential_decision = None
    success_count = sum(1 for item in observations if item["success"])
    sample_count = len(observations)
    record: dict = {
        "configured": True,
        "test_name": "binomial_success_rate",
        "metric": metric,
        "success_threshold": (
            float(success_threshold)
            if isinstance(success_threshold, (int, float))
            and not isinstance(success_threshold, bool)
            else None
        ),
        "min_success_rate": min_success_rate,
        "confidence": confidence,
        "min_samples": min_samples,
        "sample_count": sample_count,
        "success_count": success_count,
        "failure_count": sample_count - success_count,
        "observations": observations,
        "sequential_stopping": sequential_stopping,
        "sequential_stop": (
            {
                "enabled": True,
                "stopped_early": sequential_decision.get("stopped_early") is True,
                "stop_reason": sequential_decision.get("stop_reason"),
                "evaluated_samples": sequential_decision.get("evaluated_samples"),
                "planned_samples": sequential_decision.get("planned_samples"),
            }
            if sequential_decision is not None
            else {
                "enabled": sequential_stopping,
                "stopped_early": False,
                "stop_reason": None,
                "evaluated_samples": sample_count,
                "planned_samples": result.metadata.get("planned_sample_count"),
            }
        ),
        "passed": False,
    }
    if sample_count < min_samples:
        record["reason"] = "insufficient_samples"
        return record

    success_rate = success_count / sample_count
    z = NormalDist().inv_cdf(confidence)
    lower_bound = _wilson_lower_bound(success_count, sample_count, z)
    p_value = _binomial_tail_at_least(
        successes=success_count,
        trials=sample_count,
        probability=min_success_rate,
    )
    record.update(
        {
            "success_rate": success_rate,
            "z_critical": z,
            "lower_bound": lower_bound,
            "confidence_interval": {
                "kind": "one_sided_wilson_lower",
                "lower": lower_bound,
                "upper": None,
            },
            "p_value": p_value,
            "passed": lower_bound >= min_success_rate,
        }
    )
    error_budget_result = _stage_binomial_error_budget_result(
        hypothesis_test,
        confidence=confidence,
        min_success_rate=min_success_rate,
        sample_count=sample_count,
        z_critical=z,
    )
    record["error_budget"] = error_budget_result
    if record["passed"] and not error_budget_result["passed"]:
        record["passed"] = False
        record["reason"] = error_budget_result["reason"]
    if not record["passed"]:
        record.setdefault("reason", "success_rate_lower_bound_below_min")
    return record


def _stage_hypothesis_error_budget_result(
    hypothesis_test: dict,
    *,
    confidence: float,
    z_critical: float,
    standard_error: float,
) -> dict:
    error_budget = hypothesis_test.get("error_budget")
    if not isinstance(error_budget, dict):
        return {
            "configured": False,
            "passed": True,
            "calibration_method": None,
            "false_promotion": None,
            "false_rejection": None,
        }
    max_false_promotion_rate = error_budget.get("max_false_promotion_rate")
    false_promotion: dict | None = None
    passed = True
    reason: str | None = None
    if isinstance(max_false_promotion_rate, (int, float)) and not isinstance(
        max_false_promotion_rate, bool
    ):
        approximate_rate = max(0.0, 1.0 - confidence)
        false_promotion = {
            "configured": True,
            "max_rate": float(max_false_promotion_rate),
            "estimated_rate": approximate_rate,
            "passed": approximate_rate <= float(max_false_promotion_rate) + 1e-12,
            "basis": "one_sided_confidence_level",
        }
        if false_promotion["passed"] is False:
            passed = False
            reason = "false_promotion_budget_not_met"
    else:
        false_promotion = {
            "configured": False,
            "max_rate": None,
            "estimated_rate": None,
            "passed": True,
            "basis": None,
        }

    max_false_rejection_rate = error_budget.get("max_false_rejection_rate")
    min_effect_size = error_budget.get("min_effect_size")
    false_rejection: dict | None = None
    if (
        isinstance(max_false_rejection_rate, (int, float))
        and not isinstance(max_false_rejection_rate, bool)
        and isinstance(min_effect_size, (int, float))
        and not isinstance(min_effect_size, bool)
    ):
        if standard_error == 0.0:
            approximate_rate = 0.0
        else:
            approximate_rate = NormalDist().cdf(
                z_critical - (float(min_effect_size) / standard_error)
            )
        false_rejection = {
            "configured": True,
            "max_rate": float(max_false_rejection_rate),
            "estimated_rate": approximate_rate,
            "passed": approximate_rate
            <= float(max_false_rejection_rate) + 1e-12,
            "basis": "normal_approximation_min_effect_size",
            "min_effect_size": float(min_effect_size),
        }
        if false_rejection["passed"] is False:
            passed = False
            reason = reason or "false_rejection_budget_not_met"
    else:
        false_rejection = {
            "configured": False,
            "max_rate": None,
            "estimated_rate": None,
            "passed": True,
            "basis": None,
            "min_effect_size": None,
        }

    return {
        "configured": True,
        "passed": passed,
        "reason": reason,
        "calibration_method": "normal_approximation_one_sided_lcb",
        "false_promotion": false_promotion,
        "false_rejection": false_rejection,
    }


def _stage_binomial_error_budget_result(
    hypothesis_test: dict,
    *,
    confidence: float,
    min_success_rate: float,
    sample_count: int,
    z_critical: float,
) -> dict:
    error_budget = hypothesis_test.get("error_budget")
    if not isinstance(error_budget, dict):
        return {
            "configured": False,
            "passed": True,
            "calibration_method": None,
            "false_promotion": None,
            "false_rejection": None,
        }
    max_false_promotion_rate = error_budget.get("max_false_promotion_rate")
    passed = True
    reason: str | None = None
    if isinstance(max_false_promotion_rate, (int, float)) and not isinstance(
        max_false_promotion_rate, bool
    ):
        approximate_rate = max(0.0, 1.0 - confidence)
        false_promotion = {
            "configured": True,
            "max_rate": float(max_false_promotion_rate),
            "estimated_rate": approximate_rate,
            "passed": approximate_rate <= float(max_false_promotion_rate) + 1e-12,
            "basis": "one_sided_wilson_confidence_level",
        }
        if false_promotion["passed"] is False:
            passed = False
            reason = "false_promotion_budget_not_met"
    else:
        false_promotion = {
            "configured": False,
            "max_rate": None,
            "estimated_rate": None,
            "passed": True,
            "basis": None,
        }

    max_false_rejection_rate = error_budget.get("max_false_rejection_rate")
    min_effect_size = error_budget.get("min_effect_size")
    if (
        isinstance(max_false_rejection_rate, (int, float))
        and not isinstance(max_false_rejection_rate, bool)
        and isinstance(min_effect_size, (int, float))
        and not isinstance(min_effect_size, bool)
    ):
        alternative_rate = min(1.0, min_success_rate + float(min_effect_size))
        required_successes = _minimum_wilson_successes_for_rate(
            trials=sample_count,
            min_success_rate=min_success_rate,
            z_critical=z_critical,
        )
        estimated_rate = _binomial_cdf_at_most(
            successes=required_successes - 1,
            trials=sample_count,
            probability=alternative_rate,
        )
        false_rejection = {
            "configured": True,
            "max_rate": float(max_false_rejection_rate),
            "estimated_rate": estimated_rate,
            "passed": estimated_rate <= float(max_false_rejection_rate) + 1e-12,
            "basis": "exact_binomial_min_effect_size",
            "min_effect_size": float(min_effect_size),
        }
        if false_rejection["passed"] is False:
            passed = False
            reason = reason or "false_rejection_budget_not_met"
    else:
        false_rejection = {
            "configured": False,
            "max_rate": None,
            "estimated_rate": None,
            "passed": True,
            "basis": None,
            "min_effect_size": None,
        }

    return {
        "configured": True,
        "passed": passed,
        "reason": reason,
        "calibration_method": "binomial_wilson_success_rate",
        "false_promotion": false_promotion,
        "false_rejection": false_rejection,
    }


def _hypothesis_test_observations(
    result: "EvaluationResult",
    metric: str,
) -> list[dict]:
    samples = result.metadata.get("samples")
    raw_samples = samples if isinstance(samples, list) else [result.to_dict()]
    observations: list[dict] = []
    for index, sample in enumerate(raw_samples):
        if not isinstance(sample, dict):
            continue
        if metric == "fitness":
            value = sample.get("fitness")
        else:
            metrics = sample.get("metrics")
            value = metrics.get(metric) if isinstance(metrics, dict) else None
        if (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(float(value))
        ):
            observations.append({"sample_index": index, "value": float(value)})
    return observations


def _hypothesis_test_success_observations(
    result: "EvaluationResult",
    metric: str,
    *,
    success_threshold: float | None,
) -> list[dict]:
    samples = result.metadata.get("samples")
    raw_samples = samples if isinstance(samples, list) else [result.to_dict()]
    observations: list[dict] = []
    for index, sample in enumerate(raw_samples):
        if not isinstance(sample, dict):
            continue
        if metric == "fitness":
            value = sample.get("fitness")
        elif metric == "is_valid":
            value = sample.get("is_valid")
        else:
            metrics = sample.get("metrics")
            value = metrics.get(metric) if isinstance(metrics, dict) else None
        if isinstance(value, bool):
            success = value
            comparable_value: bool | float = value
        elif (
            success_threshold is not None
            and isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(float(value))
        ):
            comparable_value = float(value)
            success = comparable_value >= success_threshold
        else:
            continue
        observations.append(
            {
                "sample_index": index,
                "value": comparable_value,
                "success": success,
            }
        )
    return observations


def _wilson_lower_bound(successes: int, trials: int, z_critical: float) -> float:
    if trials <= 0:
        return 0.0
    phat = successes / trials
    z2 = z_critical * z_critical
    denominator = 1.0 + (z2 / trials)
    center = (phat + (z2 / (2.0 * trials))) / denominator
    margin = (
        z_critical
        * math.sqrt((phat * (1.0 - phat) / trials) + (z2 / (4.0 * trials * trials)))
        / denominator
    )
    return max(0.0, center - margin)


def _minimum_wilson_successes_for_rate(
    *,
    trials: int,
    min_success_rate: float,
    z_critical: float,
) -> int:
    for successes in range(trials + 1):
        if _wilson_lower_bound(successes, trials, z_critical) >= min_success_rate:
            return successes
    return trials + 1


def _binomial_tail_at_least(
    *,
    successes: int,
    trials: int,
    probability: float,
) -> float:
    if successes <= 0:
        return 1.0
    if successes > trials:
        return 0.0
    return min(
        1.0,
        sum(
            math.comb(trials, index)
            * (probability**index)
            * ((1.0 - probability) ** (trials - index))
            for index in range(successes, trials + 1)
        ),
    )


def _binomial_cdf_at_most(
    *,
    successes: int,
    trials: int,
    probability: float,
) -> float:
    if successes < 0:
        return 0.0
    if successes >= trials:
        return 1.0
    return min(
        1.0,
        sum(
            math.comb(trials, index)
            * (probability**index)
            * ((1.0 - probability) ** (trials - index))
            for index in range(0, successes + 1)
        ),
    )


def _normalized_metric_thresholds(metric_thresholds: object) -> dict[str, dict]:
    if metric_thresholds is None:
        return {}
    if not isinstance(metric_thresholds, dict):
        return {}
    normalized: dict[str, dict] = {}
    for metric, spec in metric_thresholds.items():
        if not isinstance(metric, str) or not isinstance(spec, dict):
            continue
        record: dict = {}
        if "min" in spec:
            record["min"] = float(spec["min"])
        if "max" in spec:
            record["max"] = float(spec["max"])
        if record:
            normalized[metric] = record
    return normalized


def _artifact_output_threshold_checks(result: "EvaluationResult", stage_policy: object) -> list[dict]:
    if not isinstance(stage_policy, dict):
        return []
    checks: list[dict] = []
    if stage_policy.get("require_program_output") is True:
        present = _program_output_present(result.metadata)
        check = {
            "type": "program_output",
            "required": True,
            "present": present,
            "passed": present,
        }
        if not present:
            check["reason"] = "missing_or_omitted_program_output"
        checks.append(check)
    if "min_artifacts" in stage_policy:
        minimum = int(stage_policy["min_artifacts"])
        count = _artifact_file_count(result.metadata)
        check = {
            "type": "artifacts",
            "count": count,
            "min": minimum,
            "passed": count >= minimum,
        }
        if count < minimum:
            check["reason"] = "below_min_artifacts"
        checks.append(check)
    for pattern in stage_policy.get("required_artifacts", []):
        matched = _artifact_pattern_present(result.metadata, str(pattern))
        check = {
            "type": "required_artifact",
            "pattern": str(pattern),
            "matched": matched,
            "passed": matched,
        }
        if not matched:
            check["reason"] = "missing_required_artifact"
        checks.append(check)
    for output_check in stage_policy.get("program_output_checks", []):
        if not isinstance(output_check, dict):
            continue
        path = str(output_check.get("path", ""))
        expected = output_check.get("equals")
        passed, actual, reason = _program_output_equals(result.metadata, path, expected)
        check = {
            "type": "program_output_equals",
            "path": path,
            "expected": expected,
            "actual": actual,
            "passed": passed,
        }
        if not passed:
            check["reason"] = reason
        checks.append(check)
    return checks


def _program_output_present(metadata: dict) -> bool:
    samples = metadata.get("samples")
    if isinstance(samples, list):
        if not samples:
            return False
        return all(
            isinstance(sample, dict)
            and isinstance(sample.get("metadata"), dict)
            and _program_output_present(sample["metadata"])
            for sample in samples
        )
    outputs = metadata.get("program_outputs")
    return isinstance(outputs, dict) and outputs.get("omitted") is False


def _artifact_file_count(metadata: dict) -> int:
    samples = metadata.get("samples")
    if isinstance(samples, list):
        return sum(
            _artifact_file_count(sample.get("metadata", {}))
            for sample in samples
            if isinstance(sample, dict)
        )
    artifacts = metadata.get("artifacts")
    if not isinstance(artifacts, dict):
        return 0
    files = artifacts.get("files")
    return len(files) if isinstance(files, list) else 0


def _artifact_pattern_present(metadata: dict, pattern: str) -> bool:
    return any(_artifact_glob_matches(path, pattern) for path in _artifact_paths(metadata))


def _artifact_paths(metadata: dict) -> list[str]:
    samples = metadata.get("samples")
    if isinstance(samples, list):
        paths: list[str] = []
        for sample in samples:
            if isinstance(sample, dict):
                paths.extend(_artifact_paths(sample.get("metadata", {})))
        return paths
    artifacts = metadata.get("artifacts")
    if not isinstance(artifacts, dict):
        return []
    files = artifacts.get("files")
    if not isinstance(files, list):
        return []
    return [
        str(record["path"])
        for record in files
        if isinstance(record, dict) and isinstance(record.get("path"), str)
    ]


def _program_output_equals(metadata: dict, path: str, expected: object) -> tuple[bool, object, str | None]:
    samples = metadata.get("samples")
    if isinstance(samples, list):
        actual_values = []
        reasons = []
        for sample in samples:
            if not isinstance(sample, dict) or not isinstance(sample.get("metadata"), dict):
                return False, None, "missing_sample_metadata"
            passed, actual, reason = _program_output_equals(sample["metadata"], path, expected)
            actual_values.append(actual)
            if not passed:
                reasons.append(reason or "value_mismatch")
        return not reasons, actual_values, reasons[0] if reasons else None
    outputs = metadata.get("program_outputs")
    if not isinstance(outputs, dict) or outputs.get("omitted") is not False:
        return False, None, "missing_or_omitted_program_output"
    present, actual = _lookup_dotted_output_path(outputs.get("value"), path)
    if not present:
        return False, None, "missing_program_output_path"
    if actual != expected:
        return False, actual, "value_mismatch"
    return True, actual, None


def _lookup_dotted_output_path(value: object, path: str) -> tuple[bool, object]:
    current = value
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def _validate_metrics(raw: object, problem: Problem) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("evaluator output must be a metrics dictionary")
    metrics = dict(raw)
    declared = {
        str(metric["name"])
        for metric in problem.metrics
        if str(metric.get("source", "evaluator")) == "evaluator"
    }
    declared.add("is_valid")
    missing = sorted(declared - set(metrics))
    if missing:
        raise ValueError(f"evaluator output missing declared metrics: {missing}")
    undeclared = sorted(set(metrics) - declared)
    if undeclared:
        raise ValueError(f"evaluator output included undeclared metrics: {undeclared}")
    if not isinstance(metrics.get("is_valid"), bool):
        raise ValueError("evaluator output metric 'is_valid' must be boolean")
    for name in sorted(declared - {"is_valid"}):
        value = metrics[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"evaluator output metric {name!r} must be numeric")
        if not math.isfinite(float(value)):
            raise ValueError(f"evaluator output metric {name!r} must be finite")
        metrics[name] = float(value)
    return metrics


def _split_evaluator_result(raw: object) -> tuple[object, dict | None]:
    if not isinstance(raw, dict):
        return raw, None
    has_outputs = "outputs" in raw
    has_program_output = "program_output" in raw
    if has_outputs and has_program_output:
        raise ValueError("evaluator output must use either 'outputs' or 'program_output', not both")
    if not has_outputs and not has_program_output:
        return raw, None
    key = "outputs" if has_outputs else "program_output"
    metrics = dict(raw)
    value = metrics.pop(key)
    return metrics, _program_outputs_metadata(value, key)


def _program_outputs_metadata(value: object, source_key: str) -> dict:
    redaction = {"redacted": False, "truncated_strings": 0}
    safe_value = _redact_program_output_value(value, redaction)
    try:
        json_text = strict_json_dumps(safe_value, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"evaluator outputs must be strict JSON: {exc}") from exc
    digest = hashlib.sha256(json_text.encode("utf-8")).hexdigest()
    metadata = {
        "source_key": source_key,
        "policy": "strict_json_redact_bound",
        "max_json_chars": _EVALUATOR_PROGRAM_OUTPUT_MAX_JSON_CHARS,
        "json_chars": len(json_text),
        "sha256": digest,
        "redacted": redaction["redacted"],
        "truncated_strings": redaction["truncated_strings"],
    }
    if len(json_text) <= _EVALUATOR_PROGRAM_OUTPUT_MAX_JSON_CHARS:
        metadata["value"] = safe_value
        metadata["omitted"] = False
    else:
        metadata["value"] = None
        metadata["omitted"] = True
        metadata["preview"] = _truncate_diagnostic_text(
            json_text, _EVALUATOR_PROGRAM_OUTPUT_MAX_JSON_CHARS
        )
    return metadata


def _redact_program_output_value(value: object, redaction: dict) -> object:
    if isinstance(value, str):
        redacted = _redact_secrets(value)
        if redacted != value:
            redaction["redacted"] = True
        return redacted
    if isinstance(value, list):
        return [_redact_program_output_value(item, redaction) for item in value]
    if isinstance(value, dict):
        return {
            key: _redact_program_output_value(item, redaction)
            for key, item in value.items()
        }
    return value


def _add_metric_bound_diagnostics(metadata: dict, problem: Problem, metrics: dict) -> None:
    diagnostics: list[dict] = []
    for metric in problem.metrics:
        name = str(metric["name"])
        if name == "is_valid" or name not in metrics:
            continue
        value = metrics[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        raw_value = float(value)
        lo, hi = problem.metric_bounds(name)
        if lo <= raw_value <= hi:
            continue
        diagnostics.append(
            {
                "metric": name,
                "value": raw_value,
                "bounds": [lo, hi],
                "direction": problem.metric_direction(name),
                "normalized": problem.normalize_metric(name, raw_value),
                "clamped": True,
            }
        )
    if diagnostics:
        metadata["metric_bound_diagnostics"] = diagnostics


def _aggregate_metrics(metrics_list: list[dict], aggregation_policy: dict | None = None) -> dict:
    if not metrics_list:
        return {}
    aggregation_policy = aggregation_policy or {}
    keys = sorted({key for metrics in metrics_list for key in metrics})
    result: dict = {}
    for key in keys:
        values = [metrics[key] for metrics in metrics_list if key in metrics]
        policy = aggregation_policy.get(key)
        if values and all(isinstance(v, bool) for v in values):
            bool_values = [bool(v) for v in values]
            result[key] = all(bool_values) if policy != "any" else any(bool_values)
        elif values and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values):
            numeric_values = [float(v) for v in values]
            if policy == "min":
                result[key] = min(numeric_values)
            elif policy == "max":
                result[key] = max(numeric_values)
            elif policy == "last":
                result[key] = numeric_values[-1]
            elif isinstance(policy, dict) and policy.get("policy") == "quantile":
                result[key] = _quantile(numeric_values, float(policy["q"]))
            else:
                result[key] = sum(numeric_values) / len(numeric_values)
        elif values:
            result[key] = values[-1]
    if "is_valid" in result:
        result["is_valid"] = bool(result["is_valid"])
    return result


def _normalized_metric_aggregation(metric_aggregation: object) -> dict:
    if not isinstance(metric_aggregation, dict):
        return {}
    normalized: dict = {}
    for metric, policy in metric_aggregation.items():
        if isinstance(metric, str) and isinstance(policy, str):
            normalized[metric] = policy
        elif (
            isinstance(metric, str)
            and isinstance(policy, dict)
            and policy.get("policy") == "quantile"
            and isinstance(policy.get("q"), (int, float))
            and not isinstance(policy.get("q"), bool)
        ):
            normalized[metric] = {"policy": "quantile", "q": float(policy["q"])}
    return normalized


def _quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = q * (len(ordered) - 1)
    lower_index = int(math.floor(position))
    upper_index = int(math.ceil(position))
    if lower_index == upper_index:
        return ordered[lower_index]
    fraction = position - lower_index
    return ordered[lower_index] + (ordered[upper_index] - ordered[lower_index]) * fraction
