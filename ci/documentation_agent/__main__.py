import os
from pathlib import Path

from .agent import generate_documentation
from .validator import validate
from .github import create_pull_request

from .git import (
    commit_documentation,
    create_documentation_branch,
    get_current_commit,
    get_changed_files,
    get_git_diff,
    has_documentation_changes,
    push_documentation_branch,
)

ROOT = Path(__file__).resolve().parents[2]


def read_source_files(
    changed_files: list[str],
) -> dict[str, str]:

    result = {}

    # Start with changed files.
    candidate_files = set(changed_files)

    # Add all application Python files so Gemini
    # can understand dependencies and architecture.
    app_dir = ROOT / "app"

    if app_dir.exists():

        for path in app_dir.rglob("*.py"):

            relative_path = path.relative_to(ROOT)

            candidate_files.add(
                str(relative_path).replace("\\", "/")
            )

    for relative_path in sorted(candidate_files):

        # Never send documentation.
        if relative_path.startswith("docs/"):
            continue

        # Never send environment files.
        if relative_path.startswith(".env"):
            continue

        path = ROOT / relative_path

        if not path.is_file():
            continue

        try:

            content = path.read_text(
                encoding="utf-8"
            )

        except UnicodeDecodeError:

            continue

        result[relative_path] = content

    return result


def write_documentation(
    documentation_files: dict[str, str],
) -> None:

    allowed_files = {
        "docs/SD.md",
        "docs/DD.md",
    }

    for relative_path, content in documentation_files.items():

        if relative_path not in allowed_files:

            raise ValueError(
                f"Forbidden documentation file: "
                f"{relative_path}"
            )

        target = ROOT / relative_path

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        target.write_text(
            content.rstrip() + "\n",
            encoding="utf-8",
        )

        print(
            f"Updated: {relative_path}"
        )


def main():

    print("================================")
    print("AI Documentation Agent")
    print("================================")

    # --------------------------------------------------
    # 1. Resolve documentation commit
    # --------------------------------------------------

    documentation_commit_sha = (
        os.getenv("DOCUMENTATION_COMMIT_SHA")
        or get_current_commit()
    )

    print(
        f"\nDocumentation commit: "
        f"{documentation_commit_sha}"
    )

    # --------------------------------------------------
    # 2. Get changed files
    # --------------------------------------------------

    changed_files = get_changed_files(
        documentation_commit_sha
    )

    print("\nChanged files:")

    for path in changed_files:
        print(f"  {path}")

    # --------------------------------------------------
    # 3. Get Git diff
    # --------------------------------------------------

    git_diff = get_git_diff(
        documentation_commit_sha
    )

    # --------------------------------------------------
    # 4. Read source files
    # --------------------------------------------------

    source_files = read_source_files(
        changed_files
    )

    print(
        f"\nSending {len(source_files)} "
        "source files to Gemini..."
    )

    # --------------------------------------------------
    # 5. Generate documentation
    # --------------------------------------------------

    result = generate_documentation(
        git_diff=git_diff,
        source_files=source_files,
    )

    # --------------------------------------------------
    # 6. Validate Gemini response
    # --------------------------------------------------

    validate(result)

    print("\nGemini result:")

    print(
        f"Documentation required: "
        f"{result['documentation_required']}"
    )

    print(
        f"Reason: {result['reason']}"
    )

    # --------------------------------------------------
    # 7. Stop if documentation is not required
    # --------------------------------------------------

    if not result["documentation_required"]:

        print(
            "\nNo documentation changes required."
        )

        return

    # --------------------------------------------------
    # 8. Prepare documentation files
    # --------------------------------------------------

    documentation_files = {
        "docs/SD.md": result["sd"],
        "docs/DD.md": result["dd"],
    }

    print("\nFiles proposed:")

    for path in documentation_files:
        print(f"  {path}")

    # --------------------------------------------------
    # 9. Create documentation branch
    # --------------------------------------------------

    branch_name = create_documentation_branch(
        documentation_commit_sha
    )

    print(
        f"\nCreated documentation branch: "
        f"{branch_name}"
    )

    # --------------------------------------------------
    # 10. Write documentation
    # --------------------------------------------------

    write_documentation(
        documentation_files
    )

    # --------------------------------------------------
    # 11. Check actual documentation changes
    # --------------------------------------------------

    if not has_documentation_changes():

        print(
            "\nGemini requested documentation "
            "but produced no actual changes."
        )

        return

    # --------------------------------------------------
    # 12. Commit documentation
    # --------------------------------------------------

    commit_documentation(
        documentation_commit_sha
    )

    print(
        "\nDocumentation commit created."
    )

    # --------------------------------------------------
    # 13. Push documentation branch
    # --------------------------------------------------

    push_documentation_branch(
        branch_name
    )

    print(
        f"\nPushed branch to GitHub: "
        f"{branch_name}"
    )

    # --------------------------------------------------
    # 14. Create Pull Request
    # --------------------------------------------------

    pull_request = create_pull_request(
        branch_name=branch_name,
        commit_sha=documentation_commit_sha,
    )

    print(
        "\nPull Request created:"
    )

    print(
        pull_request["html_url"]
    )


if __name__ == "__main__":
    main()