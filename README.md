# python-template-project

Template [Copier](https://copier.readthedocs.io/) para novos projetos Python + React, com tudo
pré-configurado:

- **Backend**: Flask, seguindo **Clean Architecture** + **DDD** (camadas `domain` / `application` /
  `infrastructure` / `interfaces`, com fronteiras validadas por `import-linter`)
- **Gerenciador de pacotes**: [uv](https://docs.astral.sh/uv/)
- **Qualidade**: [ruff](https://docs.astral.sh/ruff/) (lint + format), [pyright](https://microsoft.github.io/pyright/)
  (type checking), [pytest](https://docs.pytest.org/) + [pytest-cov](https://pytest-cov.readthedocs.io/)
  (TDD/cobertura), [pre-commit](https://pre-commit.com/)
- **Frontend**: React + TypeScript (Vite), ESLint
- **Infra**: Docker multi-stage (dev/produção) para backend e frontend, Docker Compose para
  desenvolvimento local
- **CI**: workflow de GitHub Actions rodando lint, type check, arquitetura e testes em cada push/PR

## Como usar

Instale o [copier](https://copier.readthedocs.io/en/stable/#installation) (ou use `uvx`, sem
instalar nada):

```bash
uvx copier copy gh:<seu-usuario>/python-template-project meu-novo-projeto
```

Responda as perguntas (nome do projeto, versão do Python/Node, porta dos serviços, licença, etc.)
e o projeto será gerado em `meu-novo-projeto/` já pronto para `make setup && make dev`.

### Atualizando um projeto já gerado

Como o template usa Copier, projetos gerados podem receber atualizações do template no futuro:

```bash
cd meu-novo-projeto
uvx copier update
```

## Estrutura deste repositório

```
copier.yaml         # perguntas e configuração do template
template/            # esqueleto do projeto que será gerado (renderizado com Jinja)
tests/               # testes que validam a geração do template (pytest + copier API)
```

## Desenvolvendo este template

```bash
uv sync
uv run pytest -m "not slow"   # testes rápidos (validação de exclusões condicionais, etc.)
uv run pytest -m slow         # gera um projeto de verdade e roda todo o toolchain (lento)
```
