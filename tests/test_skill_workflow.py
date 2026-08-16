import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace


SCRIPT = Path(__file__).parents[1].joinpath(
    "skills", "jycm-business-diff", "scripts", "jycm_workflow.py"
)
INSTALLER = SCRIPT.with_name("install_skill.py")


def dump(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


def test_skill_workflow_validates_compares_and_writes_patch(tmp_path):
    policy_path = tmp_path / "policy.json"
    before_path = tmp_path / "before.json"
    after_path = tmp_path / "after.json"
    normalized_path = tmp_path / "normalized.json"
    explanation_path = tmp_path / "explanation.json"
    patch_path = tmp_path / "patch.json"

    dump(policy_path, {
        "version": 1,
        "name": "skill-test",
        "rules": [{
            "name": "rounding",
            "path": "^amount$",
            "operation": "numeric_tolerance",
            "options": {"absolute": 0.1},
        }],
    })
    dump(before_path, {"amount": 10, "status": "draft"})
    dump(after_path, {"amount": 10.05, "status": "approved"})

    subprocess.check_call([
        sys.executable, str(SCRIPT), "validate", str(policy_path),
        "--output", str(normalized_path),
    ])
    subprocess.check_call([
        sys.executable, str(SCRIPT), "compare", str(before_path),
        str(after_path), str(policy_path), "--include-tests",
        "--explain-out", str(explanation_path),
        "--patch-out", str(patch_path),
    ])

    normalized = json.loads(normalized_path.read_text(encoding="utf-8"))
    explanation = json.loads(explanation_path.read_text(encoding="utf-8"))
    patch = json.loads(patch_path.read_text(encoding="utf-8"))
    assert normalized["name"] == "skill-test"
    assert explanation["summary"]["patch_semantically_valid"] is True
    assert explanation["summary"]["patch_operation_count"] == 2
    assert patch == [
        {"op": "test", "path": "/status", "value": "draft"},
        {"op": "replace", "path": "/status", "value": "approved"},
    ]


def test_skill_installer_supports_project_agent_layout(tmp_path):
    spec = importlib.util.spec_from_file_location("jycm_skill_installer", INSTALLER)
    installer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(installer)

    installer.install(SimpleNamespace(
        client="agents", project=str(tmp_path), force=False
    ))

    installed = tmp_path / ".agents" / "skills" / "jycm-business-diff"
    assert (installed / "SKILL.md").is_file()
    assert (installed / "scripts" / "jycm_workflow.py").is_file()
