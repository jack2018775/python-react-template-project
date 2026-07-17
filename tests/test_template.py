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
    for module_name, slug in (("fiscal", "fiscal"), ("comercial", "comercial")):
        assert (package_dir / module_name / "domain" / "entities" / f"{slug}.py").exists()
        assert (package_dir / module_name / "domain" / "value_objects" / "__init__.py").exists()
        assert (package_dir / module_name / "domain" / "repositories" / f"{slug}_repository.py").exists()
        assert (package_dir / module_name / "domain" / "services" / "__init__.py").exists()
        assert (package_dir / module_name / "domain" / "events" / "__init__.py").exists()
        assert (package_dir / module_name / "domain" / "exceptions" / f"{slug}_not_found.py").exists()
        assert (package_dir / module_name / "application" / "commands" / f"create_{slug}.py").exists()
        assert (package_dir / module_name / "application" / "queries" / f"{slug}_queries.py").exists()
        assert (
            package_dir / module_name / "infrastructure" / "persistence" / f"in_memory_{slug}_repository.py"
        ).exists()
        assert (package_dir / module_name / "interfaces" / "http" / f"{slug}_routes.py").exists()

    # The main project's own answers file must survive untouched.
    assert "target: new_project" in (dst / ".copier-answers.yml").read_text(encoding="utf-8")

    _run(["just", "setup"], cwd=dst)
    _run(["just", "check-arch"], cwd=dst)
    _run(["just", "coverage"], cwd=dst)
    _run(["just", "clean"], cwd=dst)


@pytest.mark.slow
def test_fine_grained_generators_coexist_and_pass_quality_gates(tmp_path: Path) -> None:
    dst = tmp_path / "generated"
    _generate(dst)

    def _generate_into(**data: object) -> None:
        copier.run_copy(
            str(TEMPLATE_ROOT),
            str(dst),
            data={"package_name": "test_project", "module_name": "fiscal", **data},
            defaults=True,
            unsafe=True,
            answers_file=Path(".copier-answers.module.yml"),
        )

    _generate_into(target="new_module", entity_name="NotaFiscal")
    _generate_into(target="new_entity", entity_name="Pedido")
    _generate_into(target="new_value_object", value_object_name="Cpf")
    _generate_into(target="new_service", service_name="CalculadoraDeImposto")
    _generate_into(target="new_use_case", use_case_name="AprovarPagamento", use_case_kind="command")
    _generate_into(target="new_use_case", use_case_name="ConsultarSaldo", use_case_kind="query")
    _generate_into(target="new_event", event_name="NotaFiscalEmitida")
    _generate_into(target="new_exception", exception_name="SaldoInsuficiente")
    _generate_into(target="new_repository", entity_name="Pedido")

    package_dir = dst / "backend" / "src" / "test_project" / "fiscal"
    assert (package_dir / "domain" / "entities" / "nota_fiscal.py").exists()
    assert (package_dir / "domain" / "entities" / "pedido.py").exists()
    assert (package_dir / "domain" / "value_objects" / "cpf.py").exists()
    assert (package_dir / "domain" / "services" / "calculadora_de_imposto.py").exists()
    assert (package_dir / "application" / "commands" / "aprovar_pagamento.py").exists()
    assert (package_dir / "application" / "queries" / "consultar_saldo.py").exists()
    assert (package_dir / "domain" / "events" / "nota_fiscal_emitida.py").exists()
    assert (package_dir / "domain" / "exceptions" / "saldo_insuficiente.py").exists()
    assert (package_dir / "domain" / "repositories" / "pedido_repository.py").exists()
    assert (package_dir / "infrastructure" / "persistence" / "in_memory_pedido_repository.py").exists()

    _run(["just", "setup"], cwd=dst)
    _run(["just", "lint"], cwd=dst)
    _run(["just", "typecheck"], cwd=dst)
    _run(["just", "check-arch"], cwd=dst)
    _run(["just", "coverage"], cwd=dst)
    _run(["just", "clean"], cwd=dst)
