ALLOWED_FILES = {
    "docs/SD.md",
    "docs/DD.md",
}


def validate(result: dict) -> None:

    required_fields = {
        "documentation_required",
        "reason",
        "sd",
        "dd",
    }

    # --------------------------------------------------
    # Basic response validation
    # --------------------------------------------------

    if not isinstance(result, dict):
        raise ValueError(
            "Gemini response must be a JSON object."
        )

    missing = required_fields - result.keys()

    if missing:
        raise ValueError(
            f"Missing fields: {missing}"
        )

    # --------------------------------------------------
    # documentation_required
    # --------------------------------------------------

    if not isinstance(
        result["documentation_required"],
        bool,
    ):
        raise ValueError(
            "documentation_required must be boolean."
        )

    # --------------------------------------------------
    # reason
    # --------------------------------------------------

    if not isinstance(
        result["reason"],
        str,
    ):
        raise ValueError(
            "reason must be a string."
        )

    if not result["reason"].strip():
        raise ValueError(
            "reason cannot be empty."
        )

    # --------------------------------------------------
    # SD
    # --------------------------------------------------

    if not isinstance(
        result["sd"],
        str,
    ):
        raise ValueError(
            "sd must be a string."
        )

    # --------------------------------------------------
    # DD
    # --------------------------------------------------

    if not isinstance(
        result["dd"],
        str,
    ):
        raise ValueError(
            "dd must be a string."
        )

    # --------------------------------------------------
    # Documentation NOT required
    # --------------------------------------------------

    if not result["documentation_required"]:

        if result["sd"].strip():
            raise ValueError(
                "Documentation is marked as unnecessary "
                "but SD.md content was returned."
            )

        if result["dd"].strip():
            raise ValueError(
                "Documentation is marked as unnecessary "
                "but DD.md content was returned."
            )

        return

    # --------------------------------------------------
    # Documentation IS required
    # --------------------------------------------------

    if not result["sd"].strip():
        raise ValueError(
            "Documentation is required but SD.md "
            "content is empty."
        )

    if not result["dd"].strip():
        raise ValueError(
            "Documentation is required but DD.md "
            "content is empty."
        )

    # --------------------------------------------------
    # Basic Markdown sanity checks
    # --------------------------------------------------

    if not result["sd"].lstrip().startswith("#"):
        raise ValueError(
            "SD.md does not appear to be valid Markdown."
        )

    if not result["dd"].lstrip().startswith("#"):
        raise ValueError(
            "DD.md does not appear to be valid Markdown."
        )