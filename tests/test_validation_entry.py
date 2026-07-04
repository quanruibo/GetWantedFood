from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_route_files_point_to_current_cli_and_validation_flow() -> None:
    readme = read("README.md")
    agents = read("AGENTS.md")
    current_spec = read("CURRENT_SPEC.md")
    validation = read("VALIDATION.md")
    tests_readme = read("tests/README.md")
    cli = read("design_docs/CLI.md")
    test_plan = read("design_docs/TEST_PLAN.md")

    assert "./uiuc_dining_scan.py" in readme
    assert "./VALIDATION.md" in readme
    assert "./uiuc_dining_scan.py" in agents
    assert "./design_docs/CLI.md" in agents
    assert "./uiuc_dining_scan.py" in current_spec
    assert (
        "uv run python -m pytest projects/Get_wanted_food/tests/test_validation_entry.py"
        in validation
    )
    assert "tests/test_validation_entry.py" in tests_readme
    assert "../uiuc_dining_scan.py" in cli
    assert "tests/test_validation_entry.py" in test_plan
