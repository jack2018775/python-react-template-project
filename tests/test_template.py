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
