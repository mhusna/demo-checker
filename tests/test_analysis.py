import subprocess
from pathlib import Path

from deployment_impact.analysis import extract_changed_symbols, find_business_evidence, get_diff


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def test_extracts_python_and_javascript_helpers_from_diff() -> None:
    diff = """\
@@ -1,2 +1,3 @@
+def calculate_total(items):
+export function format_total(value) {
+const normalize = (value) => value.trim()
"""

    assert extract_changed_symbols(diff) == (
        "calculate_total",
        "format_total",
        "normalize",
    )


def test_finds_limited_textual_evidence_in_business_project(tmp_path: Path) -> None:
    (tmp_path / "consumer.py").write_text(
        "result = calculate_total(items)\n# calculate_total is used here too\n",
        encoding="utf-8",
    )
    ignored = tmp_path / "node_modules"
    ignored.mkdir()
    (ignored / "bundle.js").write_text("calculate_total(items)\n", encoding="utf-8")

    evidence = find_business_evidence(tmp_path, ("calculate_total",))

    assert [(item.path, item.line) for item in evidence] == [
        ("consumer.py", 1),
        ("consumer.py", 2),
    ]


def test_get_diff_handles_initial_push_without_a_parent_commit(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.invalid")
    _git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "core.py").write_text("def calculate_total(items):\n    return sum(items)\n", encoding="utf-8")
    _git(tmp_path, "add", "core.py")
    _git(tmp_path, "commit", "-m", "initial")

    diff = get_diff(tmp_path, "HEAD^")

    assert "+def calculate_total(items):" in diff
