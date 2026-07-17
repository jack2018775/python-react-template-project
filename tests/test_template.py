import shutil
import subprocess
from pathlib import Path

import copier
import pytest

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent


def _generate(dst: Path, **extra_data: object) -> None:
    data = {
        "project_name": "Test Project",
        "author_name": "Test Author",
        "author_email": "test@example.com",
        **extra_data,
    }
    copier.run_copy(str(TEMPLATE_ROOT), str(dst), data=data, defaults=True, unsafe=True)


def _run(cmd: list[str], cwd: Path) -> None:
    resolved = shutil.which(cmd[0])
    if resolved:
        cmd = [resolved, *cmd[1:]]
    subprocess.run(cmd, cwd=cwd, check=True)


@pytest.mark.slow
def test_generated_project_passes_quality_gates_via_just(tmp_path: Path) -> None:
    dst = tmp_path / "generated"
    _generate(dst)

    _run(["just", "setup"], cwd=dst)
    _run(["just", "lint"], cwd=dst)
    _run(["just", "typecheck"], cwd=dst)
    _run(["just", "check-arch"], cwd=dst)
    _run(["just", "coverage"], cwd=dst)
    _run(["npm", "run", "build"], cwd=dst / "frontend")
    _run(["just", "clean"], cwd=dst)


def test_generation_with_no_license_and_no_ci(tmp_path: Path) -> None:
    dst = tmp_path / "generated"
    _generate(dst, license="None", use_github_actions=False)

    assert not (dst / "LICENSE").exists()
    assert not (dst / ".github").exists()
    assert (dst / "README.md").exists()


@pytest.mark.slow
def test_new_module_coexists_and_passes_quality_gates(tmp_path: Path) -> None:
    dst = tmp_path / "generated"
    _generate(dst)

    for module_name, entity_name in (("fiscal", "Fiscal"), ("comercial", "Comercial")):
        copier.run_copy(
            str(TEMPLATE_ROOT),
            str(dst),
            data={
                "target": "new_module",
                "package_name": "test_project",
                "module_name": module_name,
                "entity_name": entity_name,
            },
            defaults=True,
            unsafe=True,
            answers_file=Path(f".copier-answers.module-{module_name}.yml"),
        )

    package_dir = dst / "backend" / "src" / "test_project"
    for module_name in ("fiscal", "comercial"):
        assert (package_dir / module_name / "domain" / "entities" / "__init__.py").exists()
        assert (package_dir / module_name / "domain" / "value_objects" / "__init__.py").exists()
        assert (package_dir / module_name / "domain" / "repositories" / "__init__.py").exists()
        assert (package_dir / module_name / "domain" / "services" / "__init__.py").exists()
        assert (package_dir / module_name / "domain" / "events" / "__init__.py").exists()
        assert (package_dir / module_name / "domain" / "exceptions.py").exists()
        assert (package_dir / module_name / "application" / "commands" / "__init__.py").exists()
        assert (package_dir / module_name / "application" / "queries" / "__init__.py").exists()
        assert (package_dir / module_name / "infrastructure" / "persistence" / "__init__.py").exists()
        assert (package_dir / module_name / "interfaces" / "http" / "routes.py").exists()

    # The main project's own answers file must survive untouched.
    assert "target: new_project" in (dst / ".copier-answers.yml").read_text(encoding="utf-8")

    _run(["just", "setup"], cwd=dst)
    _run(["just", "check-arch"], cwd=dst)
    _run(["just", "coverage"], cwd=dst)
    _run(["just", "clean"], cwd=dst)
