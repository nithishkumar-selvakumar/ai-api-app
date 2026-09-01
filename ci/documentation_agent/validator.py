ALLOWED_FILES = {
    "docs/SD.md",
    "docs/DD.md",
}


def validate(result: dict) -> None:

    if not isinstance(result, dict):
        raise ValueError(
            "Gemini response must be a JSON object."
        )

    required_fields = {
        "documentation_required",
        "reason",
        "files",
    }

    missing = (
        required_fields
        - result.keys()
    )

    if missing:
        raise ValueError(
            f"Missing fields: {missing}"
        )

    if not isinstance(
        result["documentation_required"],
        bool,
    ):
        raise ValueError(
            "documentation_required must be boolean."
        )

    if not isinstance(
        result["reason"],
        str,
    ):
        raise ValueError(
            "reason must be a string."
        )

    files = result["files"]

    if not isinstance(files, dict):
        raise ValueError(
            "files must be an object."
        )

    unexpected = (
        set(files.keys())
        - ALLOWED_FILES
    )

    if unexpected:
        raise ValueError(
            "Gemini attempted to modify "
            f"forbidden files: {unexpected}"
        )

    for path, content in files.items():

        if not isinstance(content, str):
            raise ValueError(
                f"{path} must contain string content."
            )

        if path not in ALLOWED_FILES:
            raise ValueError(
                f"Forbidden documentation path: {path}"
            )