import subprocess
from pathlib import Path

from .agent import generate_documentation
from .validator import validate

from .git import (
    commit_documentation,
    create_documentation_branch,
    get_current_commit,
    has_documentation_changes,
)

ROOT = Path(__file__).resolve().parents[2]


def run(command: list[str]) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    return result.stdout.strip()


def get_git_diff() -> str:
    return run([
        "git",
        "diff",
        "HEAD^",
        "HEAD",
    ])


def get_changed_files() -> list[str]:
    output = run([
        "git",
        "diff",
        "--name-only",
        "HEAD^",
        "HEAD",
    ])

    return [
        line.strip()
        for line in output.splitlines()
        if line.strip()
    ]


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
    # 1. Get changed files
    # --------------------------------------------------

    changed_files = get_changed_files()

    print("\nChanged files:")

    for path in changed_files:
        print(f"  {path}")

    # --------------------------------------------------
    # 2. Get Git diff
    # --------------------------------------------------

    git_diff = get_git_diff()

    # --------------------------------------------------
    # 3. Read relevant source code
    # --------------------------------------------------

    source_files = read_source_files(
        changed_files
    )

    print(
        f"\nSending {len(source_files)} "
        "source files to Gemini..."
    )

    # --------------------------------------------------
    # 4. Ask Gemini
    # --------------------------------------------------

    result = generate_documentation(
        git_diff=git_diff,
        source_files=source_files,
    )

    # --------------------------------------------------
    # 5. Validate Gemini response
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
    # 6. No documentation required
    # --------------------------------------------------

    if not result["documentation_required"]:

        print(
            "\nNo documentation changes required."
        )

        return

    # --------------------------------------------------
    # 7. Prepare documentation files
    # --------------------------------------------------

    documentation_files = {
        "docs/SD.md": result["sd"],
        "docs/DD.md": result["dd"],
    }

    print("\nFiles proposed:")

    for path in documentation_files:
        print(f"  {path}")

    # --------------------------------------------------
    # 8. Create documentation branch BEFORE
    #    modifying documentation
    # --------------------------------------------------

    commit_sha = get_current_commit()

    branch_name = create_documentation_branch(
        commit_sha
    )

    print(
        f"\nCreated documentation branch: "
        f"{branch_name}"
    )

    # --------------------------------------------------
    # 9. Write documentation
    # --------------------------------------------------

    write_documentation(
        documentation_files
    )

    # --------------------------------------------------
    # 10. Check whether actual changes exist
    # --------------------------------------------------

    if not has_documentation_changes():

        print(
            "\nGemini requested documentation "
            "but produced no actual changes."
        )

        return

    # --------------------------------------------------
    # 11. Commit only SD.md / DD.md
    # --------------------------------------------------

    commit_documentation(
        commit_sha
    )

    print(
        "\nDocumentation commit created."
    )


if __name__ == "__main__":
    main()