import math
from pathlib import Path

import pytest

from libreevolve.core.candidate import (
    DEFAULT_MAX_CANDIDATE_FILE_CHARS,
    DEFAULT_MAX_CANDIDATE_STATIC_FILE_BYTES,
    DEFAULT_MAX_CANDIDATE_TOTAL_CHARS,
    DEFAULT_MAX_CANDIDATE_TOTAL_STATIC_BYTES,
    DEFAULT_MAX_CANDIDATE_WORKSPACE_FILES,
)
from libreevolve.core.config import Config, ConfigError
from libreevolve.core.prompt import DEFAULT_TEMPLATE
from libreevolve.plugins.base import PluginBase


class _EntryPointPlugin(PluginBase):
    def __init__(self, mode: str = "default", limit: int = 1):
        self.mode = mode
        self.limit = limit


class _FakeDistribution:
    version = "1.2.3"
    metadata = {"Name": "libreevolve-test-plugin"}


class _FakeEntryPoint:
    name = "sample"
    group = "libreevolve.plugins"
    value = "tests.fake:EntryPointPlugin"
    dist = _FakeDistribution()

    def load(self):
        return _EntryPointPlugin


class _FakeEntryPoints(list):
    def select(self, *, group: str, name: str):
        return [
            entry_point
            for entry_point in self
            if entry_point.group == group and entry_point.name == name
        ]

def test_default_max_generations():
    assert Config().max_generations == 1000

def test_default_n_islands():
    assert Config().n_islands == 5

def test_initial_program_validity_policy_validation():
    assert Config().initial_program_validity_policy == "permissive_baseline"
    assert (
        Config(initial_program_validity_policy="alphaevolve_strict")
        .initial_program_validity_policy
        == "alphaevolve_strict"
    )
    with pytest.raises(ConfigError, match="initial_program_validity_policy"):
        Config(initial_program_validity_policy="strict")

def test_override_fields():
    c = Config(
        max_generations=50,
        max_evaluations=10,
        max_evaluator_seconds=5.0,
        max_evaluator_subprocess_attempts=12,
        max_evaluator_stage_samples=6,
        max_evaluator_retry_attempts=3,
        max_evaluator_timeouts=2,
        max_evaluator_sample_budget_exhaustions=1,
        max_evaluator_stage_budget_exhaustions=1,
        max_runtime_seconds=30.0,
        max_llm_calls=4,
        max_llm_provider_attempts=8,
        max_llm_tokens=2000,
        max_llm_cost_microusd=5000,
        max_llm_seconds=12.5,
        llm_role_call_limits={"critique": 2, "mutation": 4},
        llm_role_provider_attempt_limits={"critique": 3},
        llm_role_token_limits={"feedback:review": 1200},
        llm_role_cost_microusd_limits={"meta_prompt": 7000},
        llm_role_seconds_limits={"critique": 3.5},
        llm_role_failure_quarantine_after={"mutation": 2},
        proposals_per_generation=3,
        seed=99,
    )
    assert c.max_generations == 50 and c.seed == 99
    assert c.max_evaluations == 10
    assert c.max_evaluator_seconds == 5.0
    assert c.max_evaluator_subprocess_attempts == 12
    assert c.max_evaluator_stage_samples == 6
    assert c.max_evaluator_retry_attempts == 3
    assert c.max_evaluator_timeouts == 2
    assert c.max_evaluator_sample_budget_exhaustions == 1
    assert c.max_evaluator_stage_budget_exhaustions == 1
    assert c.max_runtime_seconds == 30.0
    assert c.max_llm_calls == 4
    assert c.max_llm_provider_attempts == 8
    assert c.max_llm_tokens == 2000
    assert c.max_llm_cost_microusd == 5000
    assert c.max_llm_seconds == 12.5
    assert c.llm_role_call_limits == {"critique": 2, "mutation": 4}
    assert c.llm_role_provider_attempt_limits == {"critique": 3}
    assert c.llm_role_token_limits == {"feedback:review": 1200}
    assert c.llm_role_cost_microusd_limits == {"meta_prompt": 7000}
    assert c.llm_role_seconds_limits == {"critique": 3.5}
    assert c.llm_role_failure_quarantine_after == {"mutation": 2}
    assert c.proposals_per_generation == 3

def test_default_backend_is_anthropic():
    assert Config().backends[0]["type"] == "anthropic"


def test_default_sampling_strategies():
    config = Config()
    assert config.parent_selection_strategy == "mixed"
    assert config.inspiration_strategy == "mixed"


def test_default_candidate_workspace_budgets_match_model_policy():
    config = Config()

    assert config.max_candidate_workspace_files == DEFAULT_MAX_CANDIDATE_WORKSPACE_FILES
    assert config.max_candidate_file_chars == DEFAULT_MAX_CANDIDATE_FILE_CHARS
    assert config.max_candidate_total_chars == DEFAULT_MAX_CANDIDATE_TOTAL_CHARS
    assert config.max_candidate_static_file_bytes == DEFAULT_MAX_CANDIDATE_STATIC_FILE_BYTES
    assert config.max_candidate_total_static_bytes == DEFAULT_MAX_CANDIDATE_TOTAL_STATIC_BYTES


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"max_generations": -1}, "max_generations"),
        ({"max_evaluations": -1}, "max_evaluations"),
        ({"max_evaluator_seconds": 0}, "max_evaluator_seconds"),
        ({"max_evaluator_subprocess_attempts": -1}, "max_evaluator_subprocess_attempts"),
        ({"max_evaluator_subprocess_attempts": True}, "max_evaluator_subprocess_attempts"),
        ({"max_evaluator_stage_samples": -1}, "max_evaluator_stage_samples"),
        ({"max_evaluator_stage_samples": True}, "max_evaluator_stage_samples"),
        ({"max_evaluator_retry_attempts": -1}, "max_evaluator_retry_attempts"),
        ({"max_evaluator_retry_attempts": True}, "max_evaluator_retry_attempts"),
        ({"max_evaluator_timeouts": -1}, "max_evaluator_timeouts"),
        ({"max_evaluator_timeouts": True}, "max_evaluator_timeouts"),
        (
            {"max_evaluator_sample_budget_exhaustions": -1},
            "max_evaluator_sample_budget_exhaustions",
        ),
        (
            {"max_evaluator_sample_budget_exhaustions": True},
            "max_evaluator_sample_budget_exhaustions",
        ),
        (
            {"max_evaluator_stage_budget_exhaustions": -1},
            "max_evaluator_stage_budget_exhaustions",
        ),
        (
            {"max_evaluator_stage_budget_exhaustions": True},
            "max_evaluator_stage_budget_exhaustions",
        ),
        ({"max_runtime_seconds": 0}, "max_runtime_seconds"),
        ({"proposals_per_generation": 0}, "proposals_per_generation"),
        ({"proposals_per_generation": True}, "proposals_per_generation"),
        ({"num_inspirations": -1}, "num_inspirations"),
        ({"eval_timeout_sec": 0}, "eval_timeout_sec"),
        ({"explore_ratio": 1.5}, "explore_ratio"),
        ({"parent_selection_strategy": "best-ish"}, "parent_selection_strategy"),
        ({"inspiration_strategy": "anything"}, "inspiration_strategy"),
        ({"mutation_mode": "rewrite"}, "mutation_mode"),
        ({"max_candidate_workspace_files": 0}, "max_candidate_workspace_files"),
        ({"max_candidate_workspace_files": True}, "max_candidate_workspace_files"),
        ({"max_candidate_file_chars": -1}, "max_candidate_file_chars"),
        ({"max_candidate_file_chars": True}, "max_candidate_file_chars"),
        ({"max_candidate_total_chars": -1}, "max_candidate_total_chars"),
        ({"max_candidate_total_chars": True}, "max_candidate_total_chars"),
        ({"max_candidate_static_file_bytes": -1}, "max_candidate_static_file_bytes"),
        ({"max_candidate_static_file_bytes": True}, "max_candidate_static_file_bytes"),
        ({"max_candidate_total_static_bytes": -1}, "max_candidate_total_static_bytes"),
        ({"max_candidate_total_static_bytes": True}, "max_candidate_total_static_bytes"),
        ({"prompt_reward_mode": "delta"}, "prompt_reward_mode"),
        ({"prompt_reward_bounds": [1.0, 1.0]}, "prompt_reward_bounds"),
        ({"prompt_reward_bounds": [1.0]}, "prompt_reward_bounds"),
        ({"prompt_explore_coeff": -1.0}, "prompt_explore_coeff"),
        ({"meta_prompt_evolution": "false"}, "meta_prompt_evolution"),
        ({"critique_enabled": "false"}, "critique_enabled"),
        ({"critique_prompt": 123}, "critique_prompt"),
        ({"critique_reviewers": "reviewer"}, "critique_reviewers"),
        ({"critique_reviewers": [{"name": "reviewer", "extra": True}]}, "unsupported fields"),
        ({"critique_reviewers": [{"name": "bad role"}]}, "critique_reviewers\\[0\\]\\.name"),
        ({"critique_reviewers": [{"name": "r", "role": "bad role"}]}, "critique_reviewers\\[0\\]\\.role"),
        ({"critique_reviewers": [{"name": "r"}, {"name": "r"}]}, "duplicate critique reviewer name"),
        ({"critique_reviewers": [{"name": "r1", "role": "critique:x"}, {"name": "r2", "role": "critique:x"}]}, "duplicate critique reviewer role"),
        ({"critique_aggregation_policy": "majority"}, "critique_aggregation_policy"),
        ({"capture_proposal_metadata": "yes"}, "capture_proposal_metadata"),
        ({"validator_env_allowlist": "PATH"}, "validator_env_allowlist"),
        ({"validator_env_allowlist": ["GOOD", "BAD=VALUE"]}, "validator_env_allowlist"),
        ({"validator_env_allowlist": ["BAD\nNAME"]}, "manifest-safe environment variable"),
        ({"validator_env_allowlist": ["1BAD"]}, "manifest-safe environment variable"),
        ({"validator_env_allowlist": ["BAD-NAME"]}, "manifest-safe environment variable"),
        ({"validator_env_allowlist": ["bad\u202ename"]}, "manifest-safe environment variable"),
        ({"validator_network_policy": "block"}, "validator_network_policy"),
        ({"validator_network_policy": 7}, "validator_network_policy"),
        ({"evaluator_artifact_include": "*.json"}, "evaluator_artifact_include"),
        ({"evaluator_artifact_exclude": [""]}, "evaluator_artifact_exclude"),
        ({"evaluator_artifact_include": ["reports\u202e/*.json"]}, "display-safe"),
        ({"evaluator_artifact_exclude": ["reports\u200d/*.json"]}, "display-safe"),
        (
            {"evaluator_artifact_include": ["api_key=sk-proj_ARTIFACT_INCLUDE_SECRET_1234567890/*.txt"]},  # pragma: allowlist secret
            "manifest-safe glob patterns",
        ),
        (
            {"evaluator_artifact_exclude": ["api_key=sk-proj_ARTIFACT_EXCLUDE_SECRET_1234567890/*.txt"]},  # pragma: allowlist secret
            "manifest-safe glob patterns",
        ),
        ({"evaluator_artifact_include": ["../secret/*.txt"]}, "path-safe glob patterns"),
        ({"evaluator_artifact_exclude": ["/absolute/*.txt"]}, "path-safe glob patterns"),
        ({"evaluator_artifact_include": ["C:/secret/*.txt"]}, "path-safe glob patterns"),
        ({"evaluator_artifact_exclude": ["..\\secret\\*.txt"]}, "path-safe glob patterns"),
        ({"evaluator_artifact_include": ["nested//file.txt"]}, "path-safe glob patterns"),
        ({"evaluator_artifact_include": [" ./file.txt"]}, "path-safe glob patterns"),
        ({"evaluator_artifact_max_files": -1}, "evaluator_artifact_max_files"),
        ({"evaluator_artifact_max_bytes": -1}, "evaluator_artifact_max_bytes"),
        ({"evaluator_artifact_redact_secrets": "yes"}, "evaluator_artifact_redact_secrets"),  # pragma: allowlist secret
        ({"evaluator_output_max_chars": -1}, "evaluator_output_max_chars"),
        ({"evaluator_output_max_chars": True}, "evaluator_output_max_chars"),
        ({"prompt_max_chars": 0}, "prompt_max_chars"),
        ({"prompt_max_chars": -1}, "prompt_max_chars"),
        ({"prompt_max_chars": True}, "prompt_max_chars"),
        ({"prompt_max_chars": "1000"}, "prompt_max_chars"),
        ({"prompt_max_estimated_tokens": 0}, "prompt_max_estimated_tokens"),
        ({"prompt_max_estimated_tokens": -1}, "prompt_max_estimated_tokens"),
        ({"prompt_max_estimated_tokens": True}, "prompt_max_estimated_tokens"),
        ({"prompt_max_estimated_tokens": "1000"}, "prompt_max_estimated_tokens"),
        ({"prompt_artifact_content_mode": "full"}, "prompt_artifact_content_mode"),
        ({"prompt_artifact_content_max_bytes": 0}, "prompt_artifact_content_max_bytes"),
        ({"prompt_artifact_content_max_bytes": True}, "prompt_artifact_content_max_bytes"),
        ({"prompt_artifact_content_max_chars": 0}, "prompt_artifact_content_max_chars"),
        ({"prompt_artifact_content_max_chars": "100"}, "prompt_artifact_content_max_chars"),
        ({"mutation_prompt_retention_mode": "private"}, "mutation_prompt_retention_mode"),
        ({"explicit_context_retention_mode": "private"}, "explicit_context_retention_mode"),
        ({"meta_prompt_evidence_retention_mode": "private"}, "meta_prompt_evidence_retention_mode"),
        ({"quarantine_snapshot_retention_mode": "private"}, "quarantine_snapshot_retention_mode"),
        ({"critique_retention_mode": "private"}, "critique_retention_mode"),
        ({"feedback_retention_mode": "private"}, "feedback_retention_mode"),
        ({"plugin_context_retention_mode": "private"}, "plugin_context_retention_mode"),
        ({"provider_response_retention_mode": "private"}, "provider_response_retention_mode"),
        ({"provider_error_retention_mode": "private"}, "provider_error_retention_mode"),
        ({"log_dir": 7}, "log_dir"),
        ({"log_dir": ""}, "log_dir"),
        ({"log_dir": " runs"}, "path-safe log directory"),
        ({"log_dir": "runs/trailing "}, "path-safe log directory"),
        ({"log_dir": "runs/line\nbreak"}, "path-safe log directory"),
        ({"log_dir": "runs/bad\x7fname"}, "path-safe log directory"),
        ({"log_dir": "runs/bad:name"}, "path-safe log directory"),
        ({"log_dir": "runs/../escape"}, "path-safe log directory"),
        ({"log_dir": "runs/NUL"}, "path-safe log directory"),
        ({"log_dir": "runs/COM1.txt"}, "path-safe log directory"),
        ({"log_dir": "runs/bad\u202egnp"}, "display-safe log directory"),
        ({"log_dir": "runs/zero\u200dwidth"}, "display-safe log directory"),
        ({"log_dir": "runs/cafe\u0301"}, "path-safe log directory"),
        ({"problem_name": ""}, "problem_name"),
        ({"problem_name": "../escape"}, "problem_name"),
        ({"problem_name": "/absolute"}, "problem_name"),
        ({"problem_name": "C:\\escape"}, "problem_name"),
        ({"problem_name": "bad:name"}, "problem_name"),
        ({"problem_name": "CON"}, "problem_name"),
        ({"problem_name": "nul.txt"}, "problem_name"),
        ({"problem_name": "COM1"}, "problem_name"),
        ({"problem_name": "LPT9.log"}, "problem_name"),
        ({"problem_name": " run"}, "problem_name"),
        ({"problem_name": "run "}, "problem_name"),
        ({"problem_name": "run."}, "problem_name"),
        ({"problem_name": "bad\x7fname"}, "problem_name"),
        ({"problem_name": "rtl\u202egnp"}, "problem_name"),
        ({"problem_name": "zero\u200dwidth"}, "problem_name"),
        ({"problem_name": "cafe\u0301"}, "problem_name"),
        (
            {"problem_name": "api_key=sk-proj_runname_secret_1234567890"},  # pragma: allowlist secret
            "secret-safe run-name component",
        ),
        (
            {"problem_name": "sk-proj_runname_secret_1234567890"},  # pragma: allowlist secret
            "secret-safe run-name component",
        ),
        ({"seed": "42"}, "seed"),
        ({"seed": True}, "seed"),
        ({"run_id": ""}, "run_id"),
        ({"run_id": "mutated\nrun"}, "run_id"),
        ({"run_id": "api_key=sk-proj_secret_1234567890"}, "run_id"),
        ({"run_id": "sk-proj_runidsecret_1234567890abcdef"}, "run_id"),
        ({"run_id": "_leading-underscore"}, "run_id"),
        ({"run_id": "x" * 129}, "run_id"),
        ({"run_collision_policy": "append"}, "run_collision_policy"),
        ({"n_islands": 0}, "n_islands"),
        ({"migration_interval": -1}, "migration_interval"),
        ({"migration_ratio": -0.1}, "migration_ratio"),
        ({"map_elites_bins": 0}, "map_elites_bins"),
        ({"map_elites_complexity_max_chars": 0}, "map_elites_complexity_max_chars"),
        ({"map_elites_complexity_max_chars": True}, "map_elites_complexity_max_chars"),
        ({"map_elites_complexity_max_chars": "100"}, "map_elites_complexity_max_chars"),
        ({"map_elites_descriptor_axes": []}, "map_elites_descriptor_axes"),
        (
            {"map_elites_descriptor_axes": ["performance", "complexity", "bad"]},
            "map_elites_descriptor_axes",
        ),
        (
            {"map_elites_descriptor_axes": ["performance", "performance", "diversity"]},
            "map_elites_descriptor_axes",
        ),
        ({"elite_archive_size": 0}, "elite_archive_size"),
        ({"ensemble_explore_coeff": -1.0}, "ensemble_explore_coeff"),
        ({"ensemble_strategy": "random"}, "ensemble_strategy"),
        ({"llm_max_retries": -1}, "llm_max_retries"),
        ({"llm_max_retries": 11}, "llm_max_retries"),
        ({"llm_max_call_attempts": 0}, "llm_max_call_attempts"),
        ({"llm_max_call_attempts": -1}, "llm_max_call_attempts"),
        ({"llm_max_call_attempts": True}, "llm_max_call_attempts"),
        ({"llm_max_call_attempts": "32"}, "llm_max_call_attempts"),
        ({"llm_max_call_attempts": 33}, "llm_max_call_attempts"),
        ({"llm_fallback": "yes"}, "llm_fallback"),
        ({"llm_max_response_chars": 0}, "llm_max_response_chars"),
        ({"llm_max_response_chars": -1}, "llm_max_response_chars"),
        ({"llm_max_response_chars": True}, "llm_max_response_chars"),
        ({"llm_max_response_chars": "100"}, "llm_max_response_chars"),
        ({"llm_call_history_max": 0}, "llm_call_history_max"),
        ({"llm_call_history_max": -1}, "llm_call_history_max"),
        ({"llm_call_history_max": True}, "llm_call_history_max"),
        ({"llm_call_history_max": "100"}, "llm_call_history_max"),
        ({"llm_call_timeout_sec": 0}, "llm_call_timeout_sec"),
        ({"llm_call_timeout_sec": -1.0}, "llm_call_timeout_sec"),
        ({"llm_call_timeout_sec": True}, "llm_call_timeout_sec"),
        ({"llm_call_timeout_sec": "1"}, "llm_call_timeout_sec"),
        ({"max_llm_calls": -1}, "max_llm_calls"),
        ({"max_llm_calls": True}, "max_llm_calls"),
        ({"max_llm_calls": "1"}, "max_llm_calls"),
        ({"max_llm_provider_attempts": -1}, "max_llm_provider_attempts"),
        ({"max_llm_provider_attempts": True}, "max_llm_provider_attempts"),
        ({"max_llm_provider_attempts": "1"}, "max_llm_provider_attempts"),
        ({"max_llm_tokens": -1}, "max_llm_tokens"),
        ({"max_llm_tokens": True}, "max_llm_tokens"),
        ({"max_llm_tokens": "1"}, "max_llm_tokens"),
        ({"max_llm_cost_microusd": -1}, "max_llm_cost_microusd"),
        ({"max_llm_cost_microusd": True}, "max_llm_cost_microusd"),
        ({"max_llm_cost_microusd": "1"}, "max_llm_cost_microusd"),
        ({"max_llm_seconds": -1.0}, "max_llm_seconds"),
        ({"max_llm_seconds": True}, "max_llm_seconds"),
        ({"max_llm_seconds": "1"}, "max_llm_seconds"),
        ({"llm_role_provider_attempt_limits": []}, "llm_role_provider_attempt_limits"),
        (
            {"llm_role_provider_attempt_limits": {"critique": -1}},
            "llm_role_provider_attempt_limits",
        ),
        (
            {"llm_role_token_limits": {"feedback:review": True}},
            "llm_role_token_limits",
        ),
        (
            {"llm_role_cost_microusd_limits": {"bad role": 1}},
            "llm_role_cost_microusd_limits key",
        ),
        (
            {"llm_role_seconds_limits": {"mutation": True}},
            "llm_role_seconds_limits",
        ),
        (
            {"llm_role_seconds_limits": {"bad role": 1.0}},
            "llm_role_seconds_limits key",
        ),
        ({"plugins": "causal"}, "plugins"),
        ({"plugins": [""]}, "plugins\\[0\\]"),
        ({"plugins": ["  "]}, "plugins\\[0\\]"),
        ({"plugins": [7]}, "plugins\\[0\\]"),
        ({"plugins": [" causal "]}, "manifest-safe plugin label"),
        ({"plugins": ["causal\n"]}, "manifest-safe plugin label"),
        ({"plugins": ["api_key=sk-proj_secret_1234567890"]}, "manifest-safe plugin label"),  # pragma: allowlist secret
        ({"plugins": ["sk-proj_secret_1234567890"]}, "manifest-safe plugin label"),  # pragma: allowlist secret
        ({"plugins": ["_causal"]}, "manifest-safe plugin label"),
        ({"plugins": ["x" * 129]}, "manifest-safe plugin label"),
        ({"plugins": ["causal\u202e"]}, "safe plugin label"),
        ({"plugins": ["causal\u200d"]}, "safe plugin label"),
        ({"plugins": ["plugin.name-1"]}, "Unknown plugin"),
        ({"plugins": [{"options": {}}]}, "plugins\\[0\\].name is required"),
        ({"plugins": [{"name": "causal", "extra": True}]}, "unknown key"),
        ({"plugins": [{"name": "causal", "options": []}]}, "plugins\\[0\\].options"),
        ({"plugins": [{"name": "causal", "options": {"bad-key": 1}}]}, "plugin option names"),
        (
            {"plugins": [{"name": "causal", "options": {"missing": 1}}]},
            "Plugin 'causal' has unknown option",
        ),
        (
            {"plugins": [{"name": "deep_research", "options": {"search_every": 0}}]},
            "Plugin 'deep_research' option 'search_every' must be a positive integer",
        ),
        (
            {"plugins": [{"name": "deep_research", "options": {"cache_mode": "remote"}}]},
            "Plugin 'deep_research' option 'cache_mode' must be one of",
        ),
        (
            {
                "plugins": [
                    {
                        "name": "deep_research",
                        "options": {"retrieval_body_retention_mode": "private"},
                    }
                ]
            },
            "Plugin 'deep_research' option 'retrieval_body_retention_mode' must be one of",
        ),
        (
            {
                "plugins": [
                    {
                        "name": "deep_research",
                        "options": {"source_ranking_policy": "semantic_model_v9"},
                    }
                ]
            },
            "Plugin 'deep_research' option 'source_ranking_policy' must be one of",
        ),
        (
            {
                "plugins": [
                    {
                        "name": "causal",
                        "options": {"label": "api_key=sk-proj_secret_1234567890"},
                    }
                ]
            },
            "must not contain secret-like text",
        ),  # pragma: allowlist secret
    ],
)
def test_rejects_invalid_top_level_config(kwargs, message):
    with pytest.raises(ConfigError, match=message):
        Config(**kwargs)


def test_accepts_manifest_safe_plugin_labels():
    config = Config(plugins=["causal", "deep_research", "ttt_rl"])

    assert config.plugins == ["causal", "deep_research", "ttt_rl"]


def test_accepts_manifest_safe_plugin_spec_mappings():
    config = Config(
        plugins=[
            "modular",
            {"name": "causal", "options": {"history_limit": 25}},
        ]
    )

    assert config.plugins == [
        "modular",
        {"name": "causal", "options": {"history_limit": 25}},
    ]


def test_accepts_manifest_safe_entry_point_plugin_specs(monkeypatch):
    monkeypatch.setattr(
        "libreevolve.plugins.registry.metadata.entry_points",
        lambda: _FakeEntryPoints([_FakeEntryPoint()]),
    )

    config = Config(
        plugins=[
            {
                "name": "entry_point",
                "options": {
                    "group": "libreevolve.plugins",
                    "name": "sample",
                    "paper_inspiration": "AlphaEvolveExtension",
                },
            }
        ]
    )

    assert config.plugins == [
        {
            "name": "entry_point",
            "options": {
                "group": "libreevolve.plugins",
                "name": "sample",
                "paper_inspiration": "AlphaEvolveExtension",
            },
        }
    ]


def test_accepts_entry_point_plugin_constructor_options(monkeypatch):
    monkeypatch.setattr(
        "libreevolve.plugins.registry.metadata.entry_points",
        lambda: _FakeEntryPoints([_FakeEntryPoint()]),
    )

    config = Config(
        plugins=[
            {
                "name": "entry_point",
                "options": {
                    "group": "libreevolve.plugins",
                    "name": "sample",
                    "constructor_options": {
                        "mode": "audit",
                        "limit": 3,
                    },
                },
            }
        ]
    )

    assert config.plugins[0]["options"]["constructor_options"] == {
        "mode": "audit",
        "limit": 3,
    }


def test_rejects_unsafe_entry_point_paper_inspiration(monkeypatch):
    monkeypatch.setattr(
        "libreevolve.plugins.registry.metadata.entry_points",
        lambda: _FakeEntryPoints([_FakeEntryPoint()]),
    )

    with pytest.raises(ConfigError, match="paper_inspiration.*manifest-safe"):
        Config(
            plugins=[
                {
                    "name": "entry_point",
                    "options": {
                        "group": "libreevolve.plugins",
                        "name": "sample",
                        "paper_inspiration": "AlphaEvolve Extension",
                    },
                }
            ]
        )


def test_rejects_missing_entry_point_plugin_before_run_setup(monkeypatch):
    monkeypatch.setattr(
        "libreevolve.plugins.registry.metadata.entry_points",
        lambda: _FakeEntryPoints([]),
    )

    with pytest.raises(ConfigError, match="entry point .* was not found"):
        Config(
            plugins=[
                {
                    "name": "entry_point",
                    "options": {
                        "group": "libreevolve.plugins",
                        "name": "missing",
                    },
                }
            ]
        )


def test_rejects_malformed_entry_point_constructor_options(monkeypatch):
    monkeypatch.setattr(
        "libreevolve.plugins.registry.metadata.entry_points",
        lambda: _FakeEntryPoints([_FakeEntryPoint()]),
    )

    with pytest.raises(ConfigError, match="constructor_options.*must be a mapping"):
        Config(
            plugins=[
                {
                    "name": "entry_point",
                    "options": {
                        "group": "libreevolve.plugins",
                        "name": "sample",
                        "constructor_options": ["mode", "audit"],
                    },
                }
            ]
        )


def test_accepts_maximum_llm_retry_cap():
    assert Config(llm_max_retries=10).llm_max_retries == 10


def test_accepts_maximum_llm_call_attempt_cap():
    assert Config(llm_max_call_attempts=32).llm_max_call_attempts == 32


@pytest.mark.parametrize(
    ("stage", "message"),
    [
        ({}, "name is required"),
        ({"samples": 0}, "samples"),
        ({"retries": -1}, "retries"),
        ({"retries": 11}, "retries"),
        ({"timeout_sec": 0}, "timeout_sec"),
        ({"max_sample_seconds": 0}, "max_sample_seconds"),
        ({"max_sample_seconds": "fast"}, "max_sample_seconds"),
        ({"max_stage_seconds": 0}, "max_stage_seconds"),
        ({"max_stage_seconds": "fast"}, "max_stage_seconds"),
        ({"min_score": "high"}, "min_score"),
        ({"metric_aggregation": []}, "metric_aggregation"),
        ({"metric_aggregation": {1: "min"}}, "keys must be strings"),
        ({"metric_aggregation": {"bad metric": "min"}}, "manifest-safe metric name"),
        ({"metric_aggregation": {"score": "median"}}, "must be one of"),
        ({"metric_aggregation": {"score": 1}}, "must be one of"),
        ({"metric_aggregation": {"score": {"policy": "mean", "q": 0.5}}}, "policy must be 'quantile'"),
        ({"metric_aggregation": {"score": {"policy": "quantile"}}}, "q is required"),
        ({"metric_aggregation": {"score": {"policy": "quantile", "q": 1.5}}}, "between 0 and 1"),
        ({"metric_aggregation": {"score": {"policy": "quantile", "q": "p90"}}}, "score.q"),
        (
            {"metric_aggregation": {"score": {"policy": "quantile", "q": 0.5, "method": "nearest"}}},
            "unsupported",
        ),
        ({"metric_thresholds": []}, "metric_thresholds"),
        ({"metric_thresholds": {1: {"min": 0.1}}}, "keys must be strings"),
        ({"metric_thresholds": {"bad metric": {"min": 0.1}}}, "manifest-safe metric name"),
        ({"metric_thresholds": {"score": 0.1}}, "must be a mapping"),
        ({"metric_thresholds": {"score": {}}}, "must define min and/or max"),
        ({"metric_thresholds": {"score": {"median": 0.5}}}, "unsupported"),
        ({"metric_thresholds": {"score": {"min": "high"}}}, "score.min"),
        ({"metric_thresholds": {"score": {"min": 2.0, "max": 1.0}}}, "min must be <= max"),
        ({"name": "gate", "hypothesis_test": []}, "hypothesis_test"),
        (
            {
                "name": "gate",
                "samples": 2,
                "hypothesis_test": {"type": "welch_t_test", "min": 0.5},
            },
            "type",
        ),
        (
            {
                "name": "gate",
                "samples": 2,
                "hypothesis_test": {
                    "type": "one_sided_lower_confidence_bound",
                },
            },
            "min is required",
        ),
        (
            {
                "name": "gate",
                "samples": 2,
                "hypothesis_test": {
                    "type": "one_sided_lower_confidence_bound",
                    "min": 0.5,
                    "confidence": 1.0,
                },
            },
            "confidence",
        ),
        (
            {
                "name": "gate",
                "samples": 2,
                "hypothesis_test": {
                    "type": "one_sided_lower_confidence_bound",
                    "min": 0.5,
                    "min_samples": 1,
                },
            },
            "min_samples",
        ),
        (
            {
                "name": "gate",
                "samples": 2,
                "hypothesis_test": {
                    "type": "one_sided_lower_confidence_bound",
                    "min": 0.5,
                    "min_samples": 3,
                },
            },
            "samples must be >= min_samples",
        ),
        (
            {
                "name": "gate",
                "samples": 2,
                "hypothesis_test": {
                    "type": "one_sided_lower_confidence_bound",
                    "min": 0.5,
                    "sequential_stopping": "yes",
                },
            },
            "sequential_stopping",
        ),
        (
            {
                "name": "gate",
                "samples": 2,
                "hypothesis_test": {
                    "type": "one_sided_lower_confidence_bound",
                    "min": 0.5,
                    "error_budget": [],
                },
            },
            "error_budget",
        ),
        (
            {
                "name": "gate",
                "samples": 2,
                "hypothesis_test": {
                    "type": "one_sided_lower_confidence_bound",
                    "min": 0.5,
                    "confidence": 0.8,
                    "error_budget": {"max_false_promotion_rate": 0.1},
                },
            },
            "max_false_promotion_rate",
        ),
        (
            {
                "name": "gate",
                "samples": 2,
                "hypothesis_test": {
                    "type": "one_sided_lower_confidence_bound",
                    "min": 0.5,
                    "error_budget": {"max_false_rejection_rate": 0.2},
                },
            },
            "min_effect_size",
        ),
        (
            {
                "name": "gate",
                "samples": 2,
                "hypothesis_test": {
                    "type": "one_sided_lower_confidence_bound",
                    "min": 0.5,
                    "error_budget": {
                        "max_false_rejection_rate": 0.2,
                        "min_effect_size": 0.0,
                    },
                },
            },
            "min_effect_size",
        ),
        (
            {
                "name": "gate",
                "hypothesis_test": {
                    "type": "one_sided_lower_confidence_bound",
                    "min": 0.5,
                },
            },
            "samples must be configured",
        ),
        ({"min_artifacts": -1}, "min_artifacts"),
        ({"min_artifacts": True}, "min_artifacts"),
        ({"require_program_output": "yes"}, "require_program_output"),
        ({"required_artifacts": "*.json"}, "required_artifacts"),
        ({"required_artifacts": [""]}, "required_artifacts"),
        ({"program_output_checks": {}}, "program_output_checks"),
        ({"program_output_checks": ["status"]}, "must be a mapping"),
        ({"program_output_checks": [{"path": "status"}]}, "equals is required"),
        ({"program_output_checks": [{"path": "bad path", "equals": "ok"}]}, "dotted manifest-safe path"),
        ({"program_output_checks": [{"path": "status", "equals": ["ok"]}]}, "JSON-safe scalar"),
        ({"name": ""}, "name"),
        ({"name": 7}, "name"),
        ({"name": "syntax"}, "reserved"),
        ({"name": "validate"}, "reserved"),
        ({"name": " gate"}, "manifest-safe stage label"),
        ({"name": "gate\n"}, "manifest-safe stage label"),
        ({"name": "gate\napi_key=sk-proj_secret_1234567890"}, "manifest-safe stage label"),  # pragma: allowlist secret
        ({"name": "gate\u202e"}, "safe stage label"),
        ({"name": "gate\u200d"}, "safe stage label"),
        ({"name": "gate", "role": "filter"}, "role"),
        ({"name": "gate", "role": "small scale"}, "role"),
        ({"validate_path": Path("validate.py")}, "validate_path"),
        ({"validate_path": ""}, "validate_path"),
        ({"mode": "unsupported"}, "mode"),
        ({"eval_inputs": {"case": 1}}, "eval_inputs requires"),
        ({"mode": "embedded_evaluate", "validate_path": "validate.py"}, "validate_path"),
        ({"mode": "embedded_evaluate", "stdin_text": "x"}, "stdin"),
        ({"mode": "embedded_evaluate", "data_include": ["data/*.json"]}, "data_include/data_exclude"),
        (
            {"mode": "embedded_evaluate", "eval_inputs": {"api_key": "sk-proj_secret_1234567890"}},  # pragma: allowlist secret
            "JSON-safe config",
        ),
        ({"artifact_include": "*.json"}, "artifact_include"),
        ({"artifact_exclude": [""]}, "artifact_exclude"),
        ({"artifact_include": ["reports\u202e/*.json"]}, "display-safe"),
        ({"artifact_exclude": ["reports\u200d/*.json"]}, "display-safe"),
        (
            {"artifact_include": ["api_key=sk-proj_STAGE_ARTIFACT_INCLUDE_SECRET_1234567890/*.txt"]},  # pragma: allowlist secret
            "manifest-safe glob patterns",
        ),
        (
            {"artifact_exclude": ["api_key=sk-proj_STAGE_ARTIFACT_EXCLUDE_SECRET_1234567890/*.txt"]},  # pragma: allowlist secret
            "manifest-safe glob patterns",
        ),
        ({"artifact_include": ["../secret/*.txt"]}, "path-safe glob patterns"),
        ({"artifact_exclude": ["/absolute/*.txt"]}, "path-safe glob patterns"),
        ({"artifact_include": ["C:/secret/*.txt"]}, "path-safe glob patterns"),
        ({"artifact_exclude": ["..\\secret\\*.txt"]}, "path-safe glob patterns"),
        ({"data_include": "*.json"}, "data_include"),
        ({"data_exclude": [""]}, "data_exclude"),
        ({"data_include": ["../secret/*.json"]}, "path-safe glob patterns"),
        ({"stdin_text": 7}, "stdin_text"),
        ({"stdin_text": "x" * 100_001}, "stdin_text"),
        ({"stdin_file": 7}, "stdin_file"),
        ({"stdin_text": "x", "stdin_file": "input.txt"}, "must not set both"),
        ({"workload": "inner_search"}, "workload"),
        ({"workload": {"type": "search"}}, "workload.type"),
        ({"workload": {"type": "inner_search", "datasets": {}}}, "datasets"),
        ({"workload": {"type": "inner_search", "datasets": [{}]}}, "datasets\\[0\\].id"),
        ({"workload": {"type": "inner_search", "datasets": [{"id": "train", "sha256": "bad"}]}}, "sha256"),
        ({"workload": {"type": "inner_search", "budget": {"max_steps": -1}}}, "max_steps"),
        ({"workload": {"type": "inner_search", "score_fields": ["score", "score"]}}, "duplicate"),
        ({"artifact_max_files": -1}, "artifact_max_files"),
        ({"artifact_max_bytes": -1}, "artifact_max_bytes"),
        ({"artifact_redact_secrets": "yes"}, "artifact_redact_secrets"),  # pragma: allowlist secret
        ({"samples": 1, "seeds": [1, 2]}, "samples"),
        ({"seeds": [Path("seed.txt")]}, "seeds"),
        ({"seeds": [True]}, "seeds"),
        ({"seeds": [float("inf")]}, "seeds"),
        (
            {"seeds": ["sk-proj_stageseedsecret1234567890"]},  # pragma: allowlist secret
            "share-safe scalar seed",
        ),
        (
            {"seeds": ["SK-PROJ-STAGESEEDSECRET1234567890"]},  # pragma: allowlist secret
            "share-safe scalar seed",
        ),
        (
            {"seeds": ["api_key=stage seed secret"]},  # pragma: allowlist secret
            "share-safe scalar seed",
        ),
        (
            {"seeds": ["Authorization: Bearer hf_abcdefghijklmnopqrstuvwxyz1234567890"]},  # pragma: allowlist secret
            "share-safe scalar seed",
        ),
        ({"unknown": True}, "unsupported"),
    ],
)
def test_rejects_invalid_eval_stage_config(stage, message):
    with pytest.raises(ConfigError, match=message):
        Config(eval_stages=[stage])


def test_accepts_maximum_eval_stage_retry_cap():
    config = Config(eval_stages=[{"name": "retry_cap", "retries": 10}])

    assert config.eval_stages[0]["retries"] == 10


def test_accepts_eval_stage_hypothesis_test_config():
    config = Config(
        eval_stages=[
            {
                "name": "stat_gate",
                "role": "small_scale_filter",
                "samples": 3,
                "hypothesis_test": {
                    "type": "one_sided_lower_confidence_bound",
                    "metric": "score",
                    "min": 0.6,
                    "confidence": 0.9,
                    "min_samples": 3,
                    "sequential_stopping": True,
                    "error_budget": {
                        "max_false_promotion_rate": 0.1,
                        "max_false_rejection_rate": 0.2,
                        "min_effect_size": 0.05,
                    },
                },
            }
        ]
    )

    assert config.eval_stages[0]["hypothesis_test"]["metric"] == "score"
    assert config.eval_stages[0]["hypothesis_test"]["confidence"] == 0.9
    assert config.eval_stages[0]["hypothesis_test"]["sequential_stopping"] is True
    assert config.eval_stages[0]["hypothesis_test"]["error_budget"] == {
        "max_false_promotion_rate": 0.1,
        "max_false_rejection_rate": 0.2,
        "min_effect_size": 0.05,
    }
    assert config.eval_stages[0]["role"] == "small_scale_filter"


def test_accepts_configured_evaluator_stdin_text():
    config = Config(
        evaluator_stdin_text="default\n",
        eval_stages=[{"name": "gate", "stdin_text": "stage\n"}],
    )

    assert config.evaluator_stdin_text == "default\n"
    assert config.eval_stages[0]["stdin_text"] == "stage\n"


def test_accepts_configured_evaluator_stdin_file():
    config = Config(
        evaluator_stdin_file="input.txt",
        eval_stages=[{"name": "gate", "stdin_file": "stage-input.txt"}],
    )

    assert config.evaluator_stdin_file == "input.txt"
    assert config.eval_stages[0]["stdin_file"] == "stage-input.txt"


def test_accepts_embedded_evaluate_stage_eval_inputs():
    config = Config(
        eval_stages=[
            {
                "name": "candidate_eval",
                "mode": "embedded_evaluate",
                "eval_inputs": {"cases": [1, 2, 3], "scale": 0.5},
            }
        ]
    )

    assert config.eval_stages[0]["mode"] == "embedded_evaluate"
    assert config.eval_stages[0]["eval_inputs"]["cases"] == [1, 2, 3]


def test_accepts_configured_evaluator_workload_metadata():
    digest = "a" * 64
    config = Config(
        eval_stages=[
            {
                "name": "search_stage",
                "workload": {
                    "type": "inner_search",
                    "datasets": [
                        {
                            "id": "packing_train",
                            "split": "train",
                            "sha256": digest,
                            "rows": 12,
                        }
                    ],
                    "budget": {"max_trials": 50, "max_seconds": 3.5},
                    "checkpoint_policy": "retained_artifacts",
                    "score_fields": ["score", "valid_count"],
                    "artifact_policy": "candidate_writes_construct_json",
                },
            }
        ]
    )

    workload = config.eval_stages[0]["workload"]
    assert workload["type"] == "inner_search"
    assert workload["datasets"][0]["sha256"] == digest
    assert workload["budget"]["max_trials"] == 50
    assert workload["score_fields"] == ["score", "valid_count"]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"evaluator_stdin_text": 7}, "evaluator_stdin_text"),
        ({"evaluator_stdin_text": "x" * 100_001}, "evaluator_stdin_text"),
        ({"evaluator_stdin_file": 7}, "evaluator_stdin_file"),
        (
            {"evaluator_stdin_text": "x", "evaluator_stdin_file": "input.txt"},
            "must not set both",
        ),
    ],
)
def test_rejects_invalid_evaluator_stdin_text(kwargs, message):
    with pytest.raises(ConfigError, match=message):
        Config(**kwargs)


def test_accepts_configured_stage_wall_clock_budget():
    config = Config(eval_stages=[{
        "name": "budgeted",
        "max_sample_seconds": 0.5,
        "max_stage_seconds": 1.5,
    }])

    assert config.eval_stages[0]["max_sample_seconds"] == 0.5
    assert config.eval_stages[0]["max_stage_seconds"] == 1.5


def test_accepts_eval_stage_metric_thresholds():
    config = Config(
        eval_stages=[
            {
                "name": "quality",
                "metric_thresholds": {
                    "score": {"min": 0.8},
                    "runtime": {"max": 5.0},
                },
            }
        ]
    )

    assert config.eval_stages[0]["metric_thresholds"]["score"]["min"] == 0.8


def test_accepts_eval_stage_metric_aggregation():
    config = Config(
        eval_stages=[
            {
                "name": "sampled",
                "metric_aggregation": {
                    "score": "min",
                    "runtime": {"policy": "quantile", "q": 0.9},
                    "is_valid": "all",
                },
            }
        ]
    )

    assert config.eval_stages[0]["metric_aggregation"]["score"] == "min"
    assert config.eval_stages[0]["metric_aggregation"]["runtime"]["q"] == 0.9


def test_rejects_duplicate_eval_stage_names():
    with pytest.raises(ConfigError, match="duplicates"):
        Config(eval_stages=[{"name": "gate"}, {"name": "gate"}])


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        (
            {"eval_stages": [{1: "bad", "unknown": "bad"}]},
            r"eval_stages\[0\] keys must be strings",
        ),
        (
            {"backends": [{"type": "openai", "model": "m", 1: "bad", "unknown": "bad"}]},
            r"backends\[0\] keys must be strings",
        ),
        (
            {"llm_feedback": [{1: "bad", "unknown": "bad"}]},
            r"llm_feedback\[0\] keys must be strings",
        ),
    ],
)
def test_rejects_non_string_nested_config_keys_before_unsupported_sort(kwargs, message):
    with pytest.raises(ConfigError, match=message):
        Config(**kwargs)


@pytest.mark.parametrize(
    ("backend", "message"),
    [
        ({"type": "openai"}, "model"),
        ({"type": "bad", "model": "m"}, "type"),
        ({"type": "openai", "model": ""}, "model"),
        ({"type": "openai", "model": " gpt-4o-mini"}, "manifest-safe model identifier"),
        ({"type": "openai", "model": "gpt-4o-mini\n"}, "manifest-safe model identifier"),
        (
            {"type": "openai", "model": "gpt-4o-mini\napi_key=sk-proj_secret_1234567890"},  # pragma: allowlist secret
            "manifest-safe model identifier",
        ),
        (
            {"type": "openai", "model": "sk-proj_secret_1234567890"},  # pragma: allowlist secret
            "manifest-safe model identifier",
        ),
        ({"type": "anthropic", "model": "m", "reasoning_effort": "high"}, "unsupported"),
        ({"type": "anthropic", "model": "m", "api_mode": "responses"}, "unsupported"),
        ({"type": "openai", "model": "m", "reasoning_effort": "extreme"}, "reasoning_effort"),
        ({"type": "openai", "model": "m", "api_mode": "bad"}, "api_mode"),
        (
            {
                "type": "openai",
                "model": "gpt-5.1",
                "reasoning_effort": "high",
                "api_mode": "chat_completions",
            },
            "chat_completions",
        ),
        (
            {"type": "openai", "model": "gpt-4o", "reasoning_effort": "none"},
            "gpt-5.1 or newer",
        ),
        (
            {"type": "openai", "model": "gpt-5.1", "reasoning_effort": "minimal"},
            "gpt-5.1 models",
        ),
        (
            {"type": "openai", "model": "gpt-5-pro", "reasoning_effort": "medium"},
            "gpt-5-pro",
        ),
        (
            {"type": "openai", "model": "gpt-5.1", "reasoning_effort": "xhigh"},
            "gpt-5.1 models",
        ),
        (
            {"type": "openai", "model": "o3-mini", "reasoning_effort": "xhigh"},
            "eligible OpenAI models",
        ),
        ({"type": "openai", "model": "m", "cost": 0}, "cost"),
        (
            {"type": "openai", "model": "m", "cost_usd_per_million_tokens": 0},
            "cost_usd_per_million_tokens",
        ),
        (
            {"type": "openai", "model": "m", "prompt_max_estimated_tokens": 0},
            "prompt_max_estimated_tokens",
        ),
        (
            {"type": "openai", "model": "m", "context_window_tokens": 0},
            "context_window_tokens",
        ),
        (
            {"type": "openai", "model": "m", "reserved_output_tokens": -1},
            "reserved_output_tokens",
        ),
        (
            {"type": "openai", "model": "m", "reserved_output_tokens": 1},
            "context_window_tokens",
        ),
        (
            {
                "type": "openai",
                "model": "m",
                "context_window_tokens": 1024,
                "reserved_output_tokens": 1024,
            },
            "reserved_output_tokens",
        ),
        ({"type": "openai", "model": "m", "timeout_sec": 0}, "timeout_sec"),
        ({"type": "anthropic", "model": "m", "timeout_sec": True}, "timeout_sec"),
        ({"type": "ollama", "model": "m", "timeout_sec": float("inf")}, "timeout_sec"),
        ({"type": "openai", "model": "m", "provider_max_retries": -1}, "provider_max_retries"),
        ({"type": "anthropic", "model": "m", "provider_max_retries": True}, "provider_max_retries"),
        ({"type": "ollama", "model": "m", "provider_max_retries": 11}, "provider_max_retries"),
        (
            {
                "type": "custom",
                "model": "m",
                "class_path": "tests.llm.test_ensemble:ConfiguredEchoBackend",
                "timeout_sec": 10,
            },
            "unsupported",
        ),
        (
            {
                "type": "custom",
                "model": "m",
                "class_path": "tests.llm.test_ensemble:ConfiguredEchoBackend",
                "provider_max_retries": 1,
            },
            "unsupported",
        ),
        ({"type": "openai", "model": "m", "temperature": -0.1}, "temperature"),
        ({"type": "openai", "model": "m", "temperature": 2.1}, "temperature"),
        ({"type": "openai", "model": "m", "top_p": 0}, "top_p"),
        ({"type": "openai", "model": "m", "stop": ""}, "stop"),
        ({"type": "openai", "model": "m", "seed": -1}, "seed"),
        (
            {"type": "openai", "model": "m", "api_mode": "responses", "seed": 1},
            "Chat Completions",
        ),
        (
            {"type": "openai", "model": "m", "api_mode": "responses", "stop": "END"},
            "Chat Completions",
        ),
        (
            {"type": "openai", "model": "gpt-5.1", "reasoning_effort": "high", "seed": 1},
            "Chat Completions",
        ),
        ({"type": "anthropic", "model": "m", "temperature": 1.1}, "temperature"),
        ({"type": "anthropic", "model": "m", "seed": 1}, "anthropic"),
        ({"type": "ollama", "model": "m", "seed": 2_147_483_648}, "seed"),
        ({"type": "openai", "model": "m", "base_url": "ftp://example.test"}, "http"),
        ({"type": "openai", "model": "m", "base_url": "https://user@example.test"}, "credentials"),
        ({"type": "openai", "model": "m", "base_url": "https://example.test?x=1"}, "query"),
        ({"type": "openai", "model": "m", "organization": "bad org"}, "organization"),
        ({"type": "openai", "model": "m", "project": "sk-proj_contextsecret1234567890"}, "project"),
        ({"type": "anthropic", "model": "m", "organization": "org-example"}, "unsupported"),
        ({"type": "anthropic", "model": "m", "host": "http://localhost:11434"}, "unsupported"),
        ({"type": "ollama", "model": "m", "base_url": "https://example.test"}, "unsupported"),
        ({"type": "ollama", "model": "m", "organization": "org-example"}, "unsupported"),
        ({"type": "openai", "model": "m", "role": ""}, "manifest-safe role label"),
        ({"type": "openai", "model": "m", "role": "feedback:"}, "manifest-safe role label"),
        ({"type": "openai", "model": "m", "role": "bad role"}, "manifest-safe role label"),
        ({"type": "openai", "model": "m", "role": "bad\nrole"}, "manifest-safe role label"),
        (
            {"type": "openai", "model": "m", "role": "api_key=sk-proj_role_secret_1234567890"},  # pragma: allowlist secret
            "manifest-safe role label",
        ),
        ({"type": "openai", "model": "m", "extra": True}, "unsupported"),
    ],
)
def test_rejects_invalid_backend_config(backend, message):
    with pytest.raises(ConfigError, match=message):
        Config(backends=[backend])


def test_accepts_manifest_safe_backend_model_identifiers():
    config = Config(
        backends=[
            {"type": "openai", "model": "gpt-5.2"},
            {"type": "anthropic", "model": "claude-sonnet-4-6"},
            {"type": "ollama", "model": "library/qwen2.5-coder:7b-instruct"},
            {
                "type": "custom",
                "model": "fixture-model",
                "class_path": "tests.llm.test_ensemble:ConfiguredEchoBackend",
                "kwargs": {"prefix": "ok", "nested": {"enabled": True}},
            },
        ]
    )

    assert [backend["model"] for backend in config.backends] == [
        "gpt-5.2",
        "claude-sonnet-4-6",
        "library/qwen2.5-coder:7b-instruct",
        "fixture-model",
    ]


def test_accepts_backend_request_parameters():
    config = Config(
        backends=[
            {
                "type": "openai",
                "model": "gpt-4o-mini",
                "temperature": 0.2,
                "top_p": 0.9,
                "stop": ["END"],
                "seed": 123,
                "provider_max_retries": 1,
            },
            {
                "type": "anthropic",
                "model": "claude-sonnet-4-6",
                "temperature": 0.3,
                "top_p": 0.8,
                "stop": "DONE",
            },
            {
                "type": "ollama",
                "model": "llama3",
                "temperature": 0.4,
                "top_p": 0.7,
                "stop": ["HALT"],
                "seed": 456,
            },
        ]
    )

    assert config.backends[0]["temperature"] == 0.2
    assert config.backends[0]["provider_max_retries"] == 1
    assert config.backends[1]["stop"] == "DONE"
    assert config.backends[2]["seed"] == 456


def test_accepts_backend_client_context_fields():
    config = Config(
        backends=[
            {
                "type": "openai",
                "model": "gpt-4o-mini",
                "base_url": "https://gateway.example/v1",
                "organization": "org-example",
                "project": "proj_example",
            },
            {
                "type": "anthropic",
                "model": "claude-sonnet-4-6",
                "base_url": "https://anthropic.example/v1",
            },
            {
                "type": "ollama",
                "model": "llama3",
                "host": "http://localhost:11434",
            },
        ]
    )

    assert config.backends[0]["base_url"] == "https://gateway.example/v1"
    assert config.backends[1]["base_url"] == "https://anthropic.example/v1"
    assert config.backends[2]["host"] == "http://localhost:11434"


def test_accepts_llm_reward_accounted_roles():
    config = Config(llm_reward_accounted_roles=["mutation", "critique", "mutation"])

    assert config.llm_reward_accounted_roles == ["mutation", "critique"]


def test_accepts_llm_role_call_limits():
    config = Config(
        llm_role_call_limits={
            "mutation": 3,
            "critique": 1,
            "feedback:*": 2,
            "feedback:grader": 0,
        }
    )

    assert config.llm_role_call_limits == {
        "critique": 1,
        "feedback:*": 2,
        "feedback:grader": 0,
        "mutation": 3,
    }


def test_accepts_wildcard_llm_role_usage_limits():
    config = Config(
        llm_role_provider_attempt_limits={"feedback:*": 3},
        llm_role_token_limits={"feedback:*": 1200},
        llm_role_cost_microusd_limits={"feedback:*": 7000},
        llm_role_seconds_limits={"feedback:*": 3.5},
    )

    assert config.llm_role_provider_attempt_limits == {"feedback:*": 3}
    assert config.llm_role_token_limits == {"feedback:*": 1200}
    assert config.llm_role_cost_microusd_limits == {"feedback:*": 7000}
    assert config.llm_role_seconds_limits == {"feedback:*": 3.5}


def test_accepts_llm_role_backend_indices():
    config = Config(
        backends=[
            {"type": "ollama", "model": "llama3"},
            {"type": "ollama", "model": "qwen2.5"},
            {"type": "ollama", "model": "codellama"},
        ],
        llm_role_backend_indices={
            "critique": [2, 1, 1],
            "feedback:grader": [0],
        },
    )

    assert config.llm_role_backend_indices == {
        "critique": [2, 1],
        "feedback:grader": [0],
    }


def test_accepts_llm_role_failure_quarantine_after():
    config = Config(
        llm_role_failure_quarantine_after={
            "mutation": 2,
            "feedback:grader": 1,
        },
    )

    assert config.llm_role_failure_quarantine_after == {
        "feedback:grader": 1,
        "mutation": 2,
    }


@pytest.mark.parametrize(
    ("limits", "message"),
    [
        ([], "llm_role_call_limits must be a mapping"),
        ({"bad role": 1}, "llm_role_call_limits key must be a manifest-safe role label"),
        ({"feedback*": 1}, "llm_role_call_limits key must be a manifest-safe role label"),
        ({"mutation": -1}, "llm_role_call_limits\\['mutation'\\] must be a non-negative integer"),
        ({"mutation": True}, "llm_role_call_limits\\['mutation'\\] must be a non-negative integer"),
        ({"mutation": "1"}, "llm_role_call_limits\\['mutation'\\] must be a non-negative integer"),
    ],
)
def test_rejects_invalid_llm_role_call_limits(limits, message):
    with pytest.raises(ConfigError, match=message):
        Config(llm_role_call_limits=limits)


@pytest.mark.parametrize(
    ("routing", "message"),
    [
        ([], "llm_role_backend_indices must be a mapping"),
        ({"bad role": [0]}, "llm_role_backend_indices key must be a manifest-safe role label"),
        ({"critique": []}, "llm_role_backend_indices\\['critique'\\] must be a non-empty list"),
        ({"critique": [True]}, "llm_role_backend_indices\\['critique'\\]\\[0\\] must be a backend index"),
        ({"critique": ["1"]}, "llm_role_backend_indices\\['critique'\\]\\[0\\] must be a backend index"),
        ({"critique": [-1]}, "llm_role_backend_indices\\['critique'\\]\\[0\\] must be a backend index"),
        ({"critique": [2]}, "llm_role_backend_indices\\['critique'\\]\\[0\\] must be a backend index"),
    ],
)
def test_rejects_invalid_llm_role_backend_indices(routing, message):
    with pytest.raises(ConfigError, match=message):
        Config(
            backends=[
                {"type": "ollama", "model": "llama3"},
                {"type": "ollama", "model": "qwen2.5"},
            ],
            llm_role_backend_indices=routing,
        )


@pytest.mark.parametrize(
    ("policy", "message"),
    [
        ([], "llm_role_failure_quarantine_after must be a mapping"),
        (
            {"bad role": 1},
            "llm_role_failure_quarantine_after key must be a manifest-safe role label",
        ),
        (
            {"mutation": 0},
            "llm_role_failure_quarantine_after\\['mutation'\\] must be a positive integer",
        ),
        (
            {"mutation": -1},
            "llm_role_failure_quarantine_after\\['mutation'\\] must be a positive integer",
        ),
        (
            {"mutation": True},
            "llm_role_failure_quarantine_after\\['mutation'\\] must be a positive integer",
        ),
        (
            {"mutation": "1"},
            "llm_role_failure_quarantine_after\\['mutation'\\] must be a positive integer",
        ),
    ],
)
def test_rejects_invalid_llm_role_failure_quarantine_after(policy, message):
    with pytest.raises(ConfigError, match=message):
        Config(llm_role_failure_quarantine_after=policy)


@pytest.mark.parametrize(
    ("roles", "message"),
    [
        ([], "llm_reward_accounted_roles must include at least one role"),
        ("mutation", "llm_reward_accounted_roles must be a list"),
        ([123], "llm_reward_accounted_roles\\[0\\] must be a string"),
        (
            ["bad role"],
            "llm_reward_accounted_roles\\[0\\] must be a manifest-safe role label",
        ),
        (
            ["api_key=sk-proj_rewardrole_secret_1234567890"],  # pragma: allowlist secret
            "llm_reward_accounted_roles\\[0\\] must be a manifest-safe role label",
        ),
    ],
)
def test_rejects_invalid_llm_reward_accounted_roles(roles, message):
    with pytest.raises(ConfigError, match=message):
        Config(llm_reward_accounted_roles=roles)


def test_accepts_llm_prompt_role_policy():
    config = Config(
        llm_prompt_roles={
            "mutation": {
                "system": "Act as a code evolution proposer.",
                "developer": "Return only the requested patch format.",
            },
            "feedback:grader": {
                "system": "Act as a bounded reviewer.",
            },
        }
    )

    assert config.llm_prompt_roles == {
        "mutation": {
            "system": "Act as a code evolution proposer.",
            "developer": "Return only the requested patch format.",
        },
        "feedback:grader": {
            "system": "Act as a bounded reviewer.",
        },
    }


@pytest.mark.parametrize(
    ("llm_prompt_roles", "message"),
    [
        ([], "llm_prompt_roles must be a mapping"),
        ({"bad role": {"system": "x"}}, "manifest-safe role label"),
        ({"mutation": {"assistant": "x"}}, "unsupported fields"),
        ({"mutation": {}}, "system and/or developer"),
        ({"mutation": {"system": ""}}, "non-empty text"),
        ({"mutation": {"developer": 7}}, "must be a string"),
        ({"mutation": {"system": "x" * 4001}}, "at most 4000 characters"),
    ],
)
def test_rejects_invalid_llm_prompt_role_policy(llm_prompt_roles, message):
    with pytest.raises(ConfigError, match=message):
        Config(llm_prompt_roles=llm_prompt_roles)


@pytest.mark.parametrize(
    ("backend", "message"),
    [
        (
            {"type": "custom", "model": "m"},
            "class_path",
        ),
        (
            {"type": "custom", "model": "m", "class_path": "bad"},
            "module.path:ClassName",
        ),
        (
            {
                "type": "custom",
                "model": "m",
                "class_path": "pkg.mod:Backend",
                "kwargs": "bad",
            },
            "kwargs",
        ),
        (
            {
                "type": "custom",
                "model": "m",
                "class_path": "pkg.mod:Backend",
                "kwargs": {"bad key": "value"},
            },
            "keyword labels",
        ),
        (
            {
                "type": "custom",
                "model": "m",
                "class_path": "pkg.mod:Backend",
                "kwargs": {"model": "other"},
            },
            "top-level backend field",
        ),
        (
            {
                "type": "custom",
                "model": "m",
                "class_path": "pkg.mod:Backend",
                "kwargs": {"api_key": "sk-proj_custombackendsecret1234567890"},  # pragma: allowlist secret
            },
            "JSON-safe config",
        ),
    ],
)
def test_rejects_invalid_custom_backend_config(backend, message):
    with pytest.raises(ConfigError, match=message):
        Config(backends=[backend])


def test_rejects_request_parameters_on_custom_backend_config():
    with pytest.raises(ConfigError, match="custom backends"):
        Config(
            backends=[
                {
                    "type": "custom",
                    "model": "m",
                    "class_path": "pkg.mod:Backend",
                    "temperature": 0.2,
                }
            ]
        )


@pytest.mark.parametrize(
    ("model", "reasoning_effort"),
    [
        ("gpt-5.1", "none"),
        ("gpt-5.1", "high"),
        ("gpt-5.2", "minimal"),
        ("gpt-5.5", "xhigh"),
        ("gpt-5-pro", "high"),
        ("o3-mini", "minimal"),
    ],
)
def test_accepts_model_specific_openai_reasoning_effort(model, reasoning_effort):
    config = Config(
        backends=[
            {
                "type": "openai",
                "model": model,
                "reasoning_effort": reasoning_effort,
            }
        ]
    )

    assert config.backends[0]["reasoning_effort"] == reasoning_effort


@pytest.mark.parametrize("api_mode", ["auto", "chat_completions", "responses"])
def test_accepts_openai_api_mode_policy(api_mode):
    config = Config(
        backends=[
            {
                "type": "openai",
                "model": "gpt-5.1",
                "api_mode": api_mode,
            }
        ]
    )

    assert config.backends[0]["api_mode"] == api_mode


@pytest.mark.parametrize(
    ("grader", "message"),
    [
        ("simplicity", "llm_feedback"),
        ({"name": 7}, "name"),
        ({"metric": 7}, "metric"),
        ({"prompt": 7}, "prompt"),
        ({"name": ""}, "manifest-safe feedback label"),
        ({"metric": ""}, "manifest-safe metric name"),
        ({"name": "_reviewer"}, "manifest-safe feedback label"),
        ({"metric": "bad metric"}, "manifest-safe metric name"),
        ({"metric": "llm-score"}, "manifest-safe metric name"),
        ({"metric": "1score"}, "manifest-safe metric name"),
        ({"name": "reviewer\n"}, "manifest-safe feedback label"),
        (
            {"name": "api_key=sk-proj_feedbacklabel_secret_1234567890"},  # pragma: allowlist secret
            "manifest-safe feedback label",
        ),
        ({"name": "reviewer\u202e"}, "safe feedback label"),
        ({"name": "reviewer\u200d"}, "safe feedback label"),
        ({"metric": "llm_score\u202e"}, "safe metric name"),
        ({"metric": "llm_score\u200d"}, "safe metric name"),
        ({"objective_metric": "yes"}, "objective_metric"),
        ({"weight": "heavy"}, "weight"),
        ({"weight": -0.1}, "weight.*between 0 and 1"),
        ({"weight": 1.1}, "weight.*between 0 and 1"),
        ({"min_score": "low"}, "min_score"),
        ({"min_score": -0.1}, "min_score.*between 0 and 1"),
        ({"min_score": 1.1}, "min_score.*between 0 and 1"),
        ({"bounds": "0,1"}, "bounds"),
        ({"bounds": [1.0, 1.0]}, "bounds.*strictly increasing"),
        ({"bounds": [0.0, math.inf]}, "bounds"),
        ({"direction": "lower"}, "direction"),
        ({"include_invalid": "yes"}, "include_invalid"),
        ({"failure_policy": "stop_run"}, "failure_policy"),
        ({"failure_retries": -1}, "failure_retries"),
        ({"failure_retries": 4}, "failure_retries"),
        ({"failure_retries": True}, "failure_retries"),
        ({"failure_penalty": "heavy"}, "failure_penalty"),
        ({"failure_penalty": -0.1}, "failure_penalty.*between 0 and 1"),
        ({"failure_penalty": 1.1}, "failure_penalty.*between 0 and 1"),
        ({"criterion": "bad space"}, "criterion"),
        ({"criterion_description": 3}, "criterion_description"),
        ({"evaluator_gap_rationale": 3}, "evaluator_gap_rationale"),
        ({"rubric": 3}, "rubric"),
        ({"feedback_intent": "maybe"}, "feedback_intent"),
        ({"calibration_report_id": "bad space"}, "calibration_report_id"),
        ({"extra": True}, "unsupported"),
    ],
)
def test_rejects_invalid_llm_feedback_config(grader, message):
    with pytest.raises(ConfigError, match=message):
        Config(llm_feedback=[grader])


def test_accepts_valid_llm_feedback_config():
    config = Config(llm_feedback=[{
        "name": "simplicity",
        "metric": "llm_simplicity",
        "objective_metric": True,
        "weight": 0.2,
        "min_score": 0.1,
        "bounds": [0.0, 100.0],
        "direction": "minimize",
        "prompt": "Return JSON",
        "criterion": "simplicity",
        "criterion_description": "Candidate should be concise.",
        "evaluator_gap_rationale": "The evaluator does not measure readability.",
        "rubric": "Prefer clear, short implementations.",
        "feedback_intent": "score_and_discard",
        "calibration_report_id": "simplicity_calibration_v1",
        "include_invalid": True,
        "failure_policy": "penalize",
        "failure_retries": 3,
        "failure_penalty": 0.25,
    }])
    assert config.llm_feedback[0]["name"] == "simplicity"
    assert config.llm_feedback[0]["objective_metric"] is True


@pytest.mark.parametrize(
    ("template", "message"),
    [
        ("Task: {missing_field}", "unknown"),
        ("No task field", "missing required"),
        ("Task: {task", "malformed"),
    ],
)
def test_rejects_invalid_prompt_variant_templates(template, message):
    with pytest.raises(ConfigError, match=message):
        Config(prompt_variants=[template])


def test_rejects_minimal_prompt_variant_template_by_default():
    with pytest.raises(ConfigError, match="missing AlphaEvolve prompt channels"):
        Config(prompt_variants=["Task: {task}"])


def test_accepts_minimal_prompt_variant_template_in_compatibility_mode():
    config = Config(
        prompt_variants=["Task: {task}"],
        prompt_variant_semantic_policy="compatibility",
    )

    assert config.prompt_variants == ["Task: {task}"]
    assert config.prompt_variant_semantic_policy == "compatibility"


def test_accepts_alphaevolve_prompt_variant_template_by_default():
    assert Config(prompt_variants=[DEFAULT_TEMPLATE]).prompt_variants == [DEFAULT_TEMPLATE]


def test_rejects_invalid_prompt_variant_semantic_policy():
    with pytest.raises(ConfigError, match="prompt_variant_semantic_policy"):
        Config(prompt_variant_semantic_policy="loose")


def test_accepts_weighted_prompt_format_options():
    config = Config(
        prompt_variants=[DEFAULT_TEMPLATE + "\n[[prompt:tone]]"],
        prompt_format_options={
            "tone": [
                "Be concise.",
                {"text": "Explain tradeoffs.", "weight": 2.5},
            ]
        },
    )

    assert config.prompt_format_options["tone"][0] == {
        "text": "Be concise.",
        "weight": 1.0,
    }
    assert config.prompt_format_options["tone"][1]["weight"] == 2.5


@pytest.mark.parametrize(
    ("prompt_format_options", "message"),
    [
        ([], "must be a mapping"),
        ({"bad name": ["x"]}, "keys must match"),
        ({"tone": []}, "non-empty list"),
        ({"tone": [{"weight": 1.0}]}, "text is required"),
        ({"tone": [{"text": "x", "weight": -1.0}]}, "positive finite"),
        ({"tone": [{"text": "x", "unknown": "field"}]}, "unsupported fields"),
        ({"tone": ["Task: {missing_field}"]}, "unknown"),
    ],
)
def test_rejects_invalid_prompt_format_options(prompt_format_options, message):
    with pytest.raises(ConfigError, match=message):
        Config(prompt_format_options=prompt_format_options)


def test_rejects_prompt_variant_with_missing_format_option():
    with pytest.raises(ConfigError, match="missing prompt_format_options"):
        Config(
            prompt_variants=["Task: {task}\n[[prompt:tone]]"],
            prompt_variant_semantic_policy="compatibility",
        )


def test_accepts_prompt_reward_policy_config():
    config = Config(
        prompt_reward_mode="improvement",
        prompt_reward_bounds=[-1.0, 1.0],
        prompt_explore_coeff=0.25,
    )
    assert config.prompt_reward_mode == "improvement"
    assert config.prompt_reward_bounds == [-1.0, 1.0]
    assert config.prompt_explore_coeff == 0.25


def test_canonicalizes_validator_env_allowlist_labels():
    config = Config(validator_env_allowlist=[" path ", "Path", "BENCHMARK_DATA_DIR"])

    assert config.validator_env_allowlist == ["PATH", "BENCHMARK_DATA_DIR"]


def test_accepts_validator_network_policy_modes():
    assert Config().validator_network_policy == "host"
    assert Config(validator_network_policy=" deny ").validator_network_policy == "deny"


def test_accepts_evaluator_output_max_chars():
    config = Config(evaluator_output_max_chars=123)

    assert Config().evaluator_output_max_chars == 20_000
    assert config.evaluator_output_max_chars == 123


def test_accepts_prompt_max_chars():
    config = Config(prompt_max_chars=2048)

    assert Config().prompt_max_chars is None
    assert config.prompt_max_chars == 2048


def test_accepts_prompt_max_estimated_tokens():
    config = Config(prompt_max_estimated_tokens=512)

    assert Config().prompt_max_estimated_tokens is None
    assert config.prompt_max_estimated_tokens == 512


def test_accepts_map_elites_descriptor_axes():
    config = Config(
        map_elites_descriptor_axes=[
            "metric:accuracy",
            "evaluation_metadata:behavior.novelty",
            "candidate_metadata:archive.score",
        ]
    )

    assert config.map_elites_descriptor_axes == [
        "metric:accuracy",
        "evaluation_metadata:behavior.novelty",
        "candidate_metadata:archive.score",
    ]


def test_accepts_prompt_artifact_content_policy():
    config = Config(
        prompt_artifact_content_mode="bounded_file",
        prompt_artifact_content_max_bytes=8192,
        prompt_artifact_content_max_chars=2048,
    )

    assert Config().prompt_artifact_content_mode == "excerpt"
    assert Config().prompt_artifact_content_max_bytes == 4096
    assert Config().prompt_artifact_content_max_chars == 1000
    assert config.prompt_artifact_content_mode == "bounded_file"
    assert config.prompt_artifact_content_max_bytes == 8192
    assert config.prompt_artifact_content_max_chars == 2048


def test_accepts_mutation_prompt_retention_modes():
    for mode in ["full", "redacted", "hash_only", "off"]:
        assert Config(mutation_prompt_retention_mode=mode).mutation_prompt_retention_mode == mode


def test_accepts_explicit_context_retention_modes():
    for mode in ["full", "redacted", "hash_only", "off"]:
        config = Config(explicit_context_retention_mode=mode)
        assert config.explicit_context_retention_mode == mode


def test_accepts_meta_prompt_evidence_retention_modes():
    for mode in ["full", "redacted", "hash_only", "off"]:
        config = Config(meta_prompt_evidence_retention_mode=mode)
        assert config.meta_prompt_evidence_retention_mode == mode


def test_accepts_quarantine_snapshot_retention_modes():
    for mode in ["full", "redacted", "hash_only", "off"]:
        config = Config(quarantine_snapshot_retention_mode=mode)
        assert config.quarantine_snapshot_retention_mode == mode


def test_accepts_critique_retention_modes():
    for mode in ["full", "redacted", "hash_only", "off"]:
        assert Config(critique_retention_mode=mode).critique_retention_mode == mode


def test_accepts_critique_reviewer_pool_config():
    config = Config(
        critique_reviewers=[
            {
                "name": "correctness",
                "prompt": "Check correctness.",
                "role": "critique:correctness",
            },
            {"name": "simplicity"},
        ],
        critique_aggregation_policy="last_valid",
    )

    assert config.critique_reviewers == [
        {
            "name": "correctness",
            "prompt": "Check correctness.",
            "role": "critique:correctness",
        },
        {
            "name": "simplicity",
            "prompt": "",
            "role": "critique:simplicity",
        },
    ]
    assert config.critique_aggregation_policy == "last_valid"


def test_accepts_feedback_retention_modes():
    for mode in ["full", "redacted", "hash_only", "off"]:
        assert Config(feedback_retention_mode=mode).feedback_retention_mode == mode


def test_accepts_plugin_context_retention_modes():
    for mode in ["full", "redacted", "hash_only", "off"]:
        assert Config(plugin_context_retention_mode=mode).plugin_context_retention_mode == mode


def test_accepts_provider_error_retention_modes():
    for mode in ["full", "redacted", "hash_only", "off"]:
        assert Config(provider_error_retention_mode=mode).provider_error_retention_mode == mode


def test_accepts_provider_response_retention_modes():
    for mode in ["full", "redacted", "hash_only", "off"]:
        assert Config(provider_response_retention_mode=mode).provider_response_retention_mode == mode


def test_artifact_globs_allow_filename_characters_that_are_not_env_names():
    config = Config(
        evaluator_artifact_include=["reports/a=b.json", "reports/cafe\u00e9.json"],
        evaluator_artifact_exclude=["reports/tmp=old/**"],
        evaluator_data_include=["fixtures/a=b.json"],
        evaluator_data_exclude=["fixtures/tmp=old/**"],
        eval_stages=[
            {
                "name": "artifact_stage",
                "artifact_include": ["stage/output=a.txt", "stage/resume\u00e9.txt"],
                "artifact_exclude": ["stage/tmp=b/**"],
                "data_include": ["data/input=a.json"],
                "data_exclude": ["data/tmp=b/**"],
            }
        ],
    )

    assert config.evaluator_artifact_include == ["reports/a=b.json", "reports/cafe\u00e9.json"]
    assert config.evaluator_data_include == ["fixtures/a=b.json"]
    assert config.eval_stages[0]["artifact_include"] == ["stage/output=a.txt", "stage/resume\u00e9.txt"]
    assert config.eval_stages[0]["data_include"] == ["data/input=a.json"]


def test_accepts_json_safe_eval_stage_metadata():
    config = Config(eval_stages=[
        {
            "name": "sampled",
            "validate_path": "validate_alt.py",
            "seeds": [1, "case-a", 3.5, None],
        }
    ])

    assert config.eval_stages[0]["validate_path"] == "validate_alt.py"


def test_accepts_pathlike_log_dir(tmp_path):
    config = Config(log_dir=tmp_path, problem_name="run")
    assert config.log_dir == str(tmp_path)


def test_accepts_portable_run_name_components():
    assert Config(problem_name="run_2026-05.alpha").problem_name == "run_2026-05.alpha"


def test_accepts_manifest_safe_run_id():
    config = Config(run_id="run-123.alpha_4")
    assert config.run_id == "run-123.alpha_4"
