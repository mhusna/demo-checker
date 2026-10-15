from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


_SYMBOL_PATTERNS = (
    re.compile(r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)\s*\(", re.MULTILINE),
    re.compile(
        r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+\*?\s*"
        r"([A-Za-z_$][\w$]*)\s*\(",
        re.MULTILINE,
    ),
    re.compile(
        r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*="
        r"\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>",
        re.MULTILINE,
    ),
)
_SKIP_DIRS = {
    ".git",
    ".venv",
    "bin",
    "dist",
    "node_modules",
    "obj",
    "vendor",
    "__pycache__",
}
_MAX_FILE_BYTES = 1_000_000
_MAX_MATCHES_PER_SYMBOL = 20
_MAX_SNIPPET_LENGTH = 280


@dataclass(frozen=True)
class Evidence:
    symbol: str
    path: str
    line: int
    snippet: str


@dataclass(frozen=True)
class ChangeAnalysis:
    diff: str
    symbols: tuple[str, ...]
    evidence: tuple[Evidence, ...]


def get_diff(core_repo: Path, base: str) -> str:
    if re.fullmatch(r"0+", base):
        base = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
    elif base == "HEAD^":
        parent = subprocess.run(
            ["git", "-C", str(core_repo), "rev-parse", "--verify", "HEAD^"],
            check=False,
            capture_output=True,
            text=True,
        )
        if parent.returncode:
            base = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

    result = subprocess.run(
        ["git", "-C", str(core_repo), "diff", "--no-ext-diff", "--unified=60", base, "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(f"Could not read the core project diff: {result.stderr.strip()}")
    return result.stdout


def extract_changed_symbols(diff: str) -> tuple[str, ...]:
    changed_lines = "\n".join(
        line[1:] for line in diff.splitlines() if line.startswith(("+", " ")) and not line.startswith(("+++",))
    )
    symbols = {
        match.group(1)
        for pattern in _SYMBOL_PATTERNS
        for match in pattern.finditer(changed_lines)
    }
    return tuple(sorted(symbols))


def find_business_evidence(business_repo: Path, symbols: tuple[str, ...]) -> tuple[Evidence, ...]:
    if not business_repo.is_dir():
        raise FileNotFoundError(f"Business project directory does not exist: {business_repo}")
    if not symbols:
        return ()

    patterns = {
        symbol: re.compile(rf"\b{re.escape(symbol)}\b")
        for symbol in symbols
    }
    counts = {symbol: 0 for symbol in symbols}
    evidence: list[Evidence] = []

    for path in sorted(business_repo.rglob("*")):
        if not path.is_file() or any(part in _SKIP_DIRS for part in path.parts):
            continue
        try:
            if path.stat().st_size > _MAX_FILE_BYTES:
                continue
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as error:
            raise OSError(f"Could not read business project file {path}: {error}") from error

        relative_path = path.relative_to(business_repo).as_posix()
        for line_number, line in enumerate(lines, start=1):
            for symbol, pattern in patterns.items():
                if counts[symbol] >= _MAX_MATCHES_PER_SYMBOL:
                    continue
                if pattern.search(line):
                    snippet = line.strip()
                    if len(snippet) > _MAX_SNIPPET_LENGTH:
                        snippet = snippet[: _MAX_SNIPPET_LENGTH - 3] + "..."
                    evidence.append(Evidence(symbol, relative_path, line_number, snippet))
                    counts[symbol] += 1

    return tuple(evidence)


def analyze(core_repo: Path, business_repo: Path, base: str) -> ChangeAnalysis:
    diff = get_diff(core_repo, base)
    symbols = extract_changed_symbols(diff)
    evidence = find_business_evidence(business_repo, symbols)
    return ChangeAnalysis(diff=diff, symbols=symbols, evidence=evidence)
