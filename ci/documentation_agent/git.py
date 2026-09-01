import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run_git(args: list[str]) -> str:

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

    # Check tracked modifications.
    tracked_result = subprocess.run(
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

    if tracked_result.returncode != 0:
        return True

    # Check untracked documentation files.
    untracked_result = subprocess.run(
        [
            "git",
            "ls-files",
            "--others",
            "--exclude-standard",
            "--",
            "docs/SD.md",
            "docs/DD.md",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    return bool(
        untracked_result.stdout.strip()
    )


def commit_documentation(
    commit_sha: str,
) -> None:

    run_git([
        "add",
        "--",
        "docs/SD.md",
        "docs/DD.md",
    ])

    # Make sure something was actually staged.
    staged_result = subprocess.run(
        [
            "git",
            "diff",
            "--cached",
            "--quiet",
            "--",
            "docs/SD.md",
            "docs/DD.md",
        ],
        cwd=ROOT,
    )

    if staged_result.returncode == 0:
        raise RuntimeError(
            "No documentation changes were staged."
        )

    run_git([
        "commit",
        "-m",
        f"docs: update SD and DD for {commit_sha[:8]}",
    ])