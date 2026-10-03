"""Build the Morning Brief starter from the reference implementation: every function body becomes `raise NotImplementedError`.

    uv run --no-project python tools/make_project_starter.py

Kept as is: pyproject, profile, versions, env.example, fixtures, tests, evals/cases, docs, workflows, prompts, templates,
and the module-level structure of every Python file (imports, constants, dataclass fields, signatures, docstrings).
Replaced: the body of every function and method, except in modules listed in KEEP_WHOLE (M1 day-1 scaffolding).
"""

from __future__ import annotations

import ast
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "exercises/project-morning-brief/morning-brief"
DST = ROOT / "exercises/project-morning-brief/morning-brief-starter"
KEEP_WHOLE = {"__init__.py", "config.py", "llm/schemas.py", "llm/prompts.py", "sources/base.py", "offline.py", "cli.py"}


class Stubber(ast.NodeTransformer):
    def _stub(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        doc = ast.get_docstring(node)
        body: list[ast.stmt] = []
        if doc:
            body.append(node.body[0])
        body.append(ast.parse("raise NotImplementedError  # TODO: see the milestone brief in chapter 31").body[0])
        node.body = body
        return node

    def visit_FunctionDef(self, node):  # noqa: N802 - ast visitor API
        return self._stub(node)

    def visit_AsyncFunctionDef(self, node):  # noqa: N802
        return self._stub(node)


def stub_source(text: str) -> str:
    tree = ast.parse(text)
    tree = Stubber().visit(tree)
    ast.fix_missing_locations(tree)
    header = text.split("\n", 1)[0] if text.startswith('"""') or text.startswith("r'''") or text.startswith('r"""') else ""
    out = ast.unparse(tree)
    return (out if out.startswith('"""') or out.startswith("'") else out) + "\n"


def main() -> None:
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST, ignore=shutil.ignore_patterns(".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "data", "out", "uv.lock"))
    package = DST / "src" / "morning_brief"
    stubbed = 0
    for path in sorted(package.rglob("*.py")):
        rel = path.relative_to(package).as_posix()
        if rel in KEEP_WHOLE:
            continue
        path.write_text(stub_source(path.read_text(encoding="utf-8")), encoding="utf-8")
        stubbed += 1
    (DST / "README.md").write_text(
        "# Morning Brief: starter\n\nThis is the course starter: the full project structure, tests, fixtures, docs, workflows and prompts,\n"
        "with every function body replaced by `raise NotImplementedError`. Chapter 31 walks through the nine milestones;\n"
        "each milestone names the modules to implement and the tests that must pass. The reference implementation\n"
        "lives next to this directory (`../morning-brief`) for when you are stuck.\n\n"
        "```powershell\nuv sync\nuv run pytest -q           # red at first; green by the end of M9\nuv run morning-brief run --offline\n```\n",
        encoding="utf-8",
    )
    print(f"starter written to {DST} ({stubbed} modules stubbed)")


if __name__ == "__main__":
    main()
