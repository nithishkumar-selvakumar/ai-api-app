def validate(
    result: dict,
) -> None:

    required_fields = {
        "documentation_required",
        "reason",
        "dd",
    }

    if not isinstance(
        result,
        dict,
    ):

        raise ValueError(
            "Gemini response must be a JSON object."
        )

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
            "documentation_required "
            "must be boolean."
        )

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

    if not result[
        "documentation_required"
    ]:

        if result["dd"].strip():

            raise ValueError(
                "Documentation is marked as "
                "unnecessary but DD.md content "
                "was returned."
            )

        return

    # --------------------------------------------------
    # Documentation IS required
    # --------------------------------------------------

    if not result["dd"].strip():

        raise ValueError(
            "Documentation is required but "
            "DD.md content is empty."
        )

    if not result["dd"].lstrip().startswith("#"):

        raise ValueError(
            "DD.md does not appear to be "
            "valid Markdown."
        )