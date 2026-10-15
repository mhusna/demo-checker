from __future__ import annotations

import argparse
from pathlib import Path

from deployment_impact.agents import run_agents
from deployment_impact.analysis import analyze


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze deployment impact on a dependent project.")
    parser.add_argument("--core-repo", type=Path, required=True, help="Path to the core Git repository.")
    parser.add_argument("--business-repo", type=Path, required=True, help="Path to the checked-out business repository.")
    parser.add_argument("--base", required=True, help="Base Git ref or commit used for the core diff.")
    parser.add_argument("--report", type=Path, required=True, help="Markdown report output path.")
    args = parser.parse_args()

    analysis = analyze(args.core_repo, args.business_repo, args.base)
    if not analysis.diff.strip():
        raise RuntimeError("The selected base and HEAD contain no changes to analyze.")

    report = run_agents(analysis)
    heading = (
        "# Deployment impact analysis\n\n"
        f"- Changed helper names: {', '.join(analysis.symbols) or 'Not identified'}\n"
        f"- Business references found: {len(analysis.evidence)}\n"
        f"- Diff base: `{args.base}`\n\n"
    )
    args.report.write_text(heading + report + "\n", encoding="utf-8")
    print(f"Analysis report written to {args.report}")
    return 0
