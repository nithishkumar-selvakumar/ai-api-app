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
        f"docs/ai-dd-update-{short_sha}"
    )

    result = subprocess.run(

        [
            "git",
            "rev-parse",
            "--verify",
            branch_name,
        ],

        cwd=ROOT,

        capture_output=True,

        text=True,
    )

    if result.returncode == 0:

        run_git([
            "checkout",
            branch_name,
        ])

        return branch_name

    run_git([
        "checkout",
        "-b",
        branch_name,
        commit_sha,
    ])

    return branch_name


def has_documentation_changes() -> bool:

    tracked_result = subprocess.run(

        [
            "git",
            "diff",
            "--quiet",
            "--",
            "docs/DD.md",
        ],

        cwd=ROOT,
    )

    if tracked_result.returncode != 0:

        return True

    untracked_result = subprocess.run(

        [
            "git",
            "ls-files",
            "--others",
            "--exclude-standard",
            "--",
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
        "docs/DD.md",
    ])

    staged_result = subprocess.run(

        [
            "git",
            "diff",
            "--cached",
            "--quiet",
            "--",
            "docs/DD.md",
        ],

        cwd=ROOT,
    )

    if staged_result.returncode == 0:

        raise RuntimeError(
            "No DD documentation changes "
            "were staged."
        )

    run_git([
        "commit",
        "-m",
        f"docs: update DD for {commit_sha[:8]}",
    ])


def push_documentation_branch(
    branch_name: str,
) -> None:

    run_git([
        "push",
        "--set-upstream",
        "origin",
        branch_name,
    ])


def get_parent_commit(
    commit_sha: str,
) -> str:

    return run_git([
        "rev-parse",
        f"{commit_sha}^",
    ])


def get_git_diff(
    commit_sha: str | None = None,
) -> str:

    if commit_sha:

        parent_sha = get_parent_commit(
            commit_sha
        )

        return run_git([
            "diff",
            parent_sha,
            commit_sha,
        ])

    return run_git([
        "diff",
        "HEAD^",
        "HEAD",
    ])


def get_changed_files(
    commit_sha: str | None = None,
) -> list[str]:

    if commit_sha:

        parent_sha = get_parent_commit(
            commit_sha
        )

        output = run_git([
            "diff",
            "--name-only",
            parent_sha,
            commit_sha,
        ])

    else:

        output = run_git([
            "diff",
            "--name-only",
            "HEAD^",
            "HEAD",
        ])

    return [
        file.strip()
        for file in output.splitlines()
        if file.strip()
    ]