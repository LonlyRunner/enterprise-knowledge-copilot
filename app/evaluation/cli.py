from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from app.evaluation.cache import CaseResultCache
from app.evaluation.dataset import EvaluationDataset
from app.evaluation.executors import HttpGatewayExecutor, ReplayExecutor
from app.evaluation.quality_gate import QualityGate
from app.evaluation.report import report_to_json, report_to_markdown
from app.evaluation.runner import UnifiedEvaluationRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="C5 unified Agent/Retrieval/Generation evaluation")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run a golden dataset")
    run.add_argument("--dataset", default="data/evaluation/c5_cases.json")
    source = run.add_mutually_exclusive_group(required=True)
    source.add_argument("--results", help="replay observations JSON (CI/offline)")
    source.add_argument("--base-url", help="live Gateway API base, e.g. http://127.0.0.1:8000/api/v1")
    run.add_argument("--gate", default="data/evaluation/quality_gate.json")
    run.add_argument("--cache-dir", default="storage/evaluation/cache")
    run.add_argument("--no-cache", action="store_true")
    run.add_argument("--clear-cache", action="store_true")
    run.add_argument("--max-concurrency", type=int, default=4)
    run.add_argument("--format", choices=("json", "markdown"), default="markdown")
    run.add_argument("--output")
    run.add_argument("--no-fail-on-gate", action="store_true")
    return parser


async def run_command(args: argparse.Namespace) -> int:
    dataset_path = Path(args.dataset)
    cases = EvaluationDataset().load(dataset_path)
    cache = CaseResultCache(args.cache_dir)
    if args.clear_cache:
        print(f"Cleared {cache.clear()} cached case results", file=sys.stderr)
    if args.results:
        executor = ReplayExecutor.from_file(args.results)
        executor_version = executor.version
    else:
        executor = HttpGatewayExecutor(args.base_url)
        executor_version = executor.version
    gate = QualityGate.from_file(args.gate) if args.gate else QualityGate()
    report = await UnifiedEvaluationRunner(
        executor, cache=cache, use_cache=not args.no_cache,
        max_concurrency=args.max_concurrency, executor_version=executor_version,
    ).run(cases, dataset=str(dataset_path), quality_gate=gate)
    content = report_to_json(report) if args.format == "json" else report_to_markdown(report)
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    else:
        print(content, end="" if content.endswith("\n") else "\n")
    if report.quality_gate and not report.quality_gate.passed and not args.no_fail_on_gate:
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        return asyncio.run(run_command(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
