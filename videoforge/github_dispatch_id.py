"""Extrai apenas o ID exato do novo run devolvido por 'gh workflow run'.

A busca por título é fallback: um título antigo de retry não identifica
a nova execução de forma única. Não dispara GitHub Actions nem cobra IA.
"""
from __future__ import annotations

import re
import sys


def extract_run_id(stdout: str, repository: str) -> int | None:
    if not isinstance(stdout, str) or not isinstance(repository, str):
        return None
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        return None
    pattern = re.compile(
        r"https://github\.com/" + re.escape(repository)
        + r"/actions/runs/([1-9][0-9]*)(?:\b|/)"
    )
    found = {int(item) for item in pattern.findall(stdout)}
    return next(iter(found)) if len(found) == 1 else None


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("USAGE: python -m videoforge.github_dispatch_id <url> <owner/repo>")
    value = extract_run_id(sys.argv[1], sys.argv[2])
    print(value if value is not None else "")


if __name__ == "__main__":
    main()
