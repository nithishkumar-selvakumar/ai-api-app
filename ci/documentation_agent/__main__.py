import subprocess
from pathlib import Path

from .agent import generate_documentation
from .validator import validate

from .git import (
    commit_documentation,
    create_documentation_branch,
    get_current_branch,
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

    return result.stdout


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

    # Start with changed source files.
    candidate_files = set(changed_files)

    # Add application source files so Gemini can understand
    # the architecture and dependencies of the changed code.
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
    files: dict[str, str],
) -> None:

    allowed_files = {
        "docs/SD.md",
        "docs/DD.md",
    }

    for relative_path, content in files.items():

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

    changed_files = get_changed_files()

    print("\nChanged files:")

    for path in changed_files:
        print(f"  {path}")

    git_diff = get_git_diff()

    source_files = read_source_files(
        changed_files
    )

    print(
        f"\nSending {len(source_files)} "
        "source files to Gemini..."
    )

    result = generate_documentation(
        git_diff=git_diff,
        source_files=source_files,
    )

    validate(result)

    print("\nGemini result:")
    print(
        f"Documentation required: "
        f"{result['documentation_required']}"
    )

    print(
        f"Reason: {result['reason']}"
    )

    if result["documentation_required"]:

        print("\nFiles proposed:")

        for path in result["files"]:
            print(f"  {path}")

        if result["documentation_required"]:

            write_documentation(
                result["files"]
            )

            if not has_documentation_changes():

                print(
                    "\nGemini requested documentation "
                    "but produced no actual changes."
                )

                return

            commit_sha = get_current_commit()

            branch_name = create_documentation_branch(
                commit_sha
            )

            print(
                f"\nCreated documentation branch: "
                f"{branch_name}"
            )

            commit_documentation(
                commit_sha
            )

            print(
                "\nDocumentation commit created."
            )

        else:

            print(
                "\nNo documentation changes required."
            )

        print(
            "\nDocumentation files updated successfully."
        )

    else:

        print(
            "\nNo documentation changes required."
        )


if __name__ == "__main__":
    main()