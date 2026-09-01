import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run_git(
    args: list[str],
) -> str:

    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    return result.stdout.strip()


def get_current_commit() -> str:
    return run_git([
        "rev-parse",
        "HEAD",
    ])


def get_current_branch() -> str:
    return run_git([
        "branch",
        "--show-current",
    ])


def create_documentation_branch(
    commit_sha: str,
) -> str:

    short_sha = commit_sha[:8]

    branch_name = (
        f"docs/ai-update-{short_sha}"
    )

    run_git([
        "checkout",
        "-b",
        branch_name,
    ])

    return branch_name


def has_documentation_changes() -> bool:

    result = subprocess.run(
        [
            "git",
            "diff",
            "--quiet",
            "--",
            "docs/SD.md",
            "docs/DD.md",
        ],
        cwd=ROOT,
    )

    return result.returncode != 0


def commit_documentation(
    commit_sha: str,
) -> None:

    run_git([
        "add",
        "--",
        "docs/SD.md",
        "docs/DD.md",
    ])

    run_git([
        "commit",
        "-m",
        f"docs: update SD and DD for {commit_sha[:8]}",
    ])