import json
import os
from pathlib import Path

from google import genai


ROOT = Path(__file__).resolve().parents[2]

MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


def read_file(path: Path) -> str:
    if not path.exists():
        return ""

    return path.read_text(
        encoding="utf-8"
    )


def build_prompt(
    git_diff: str,
    source_files: dict[str, str],
    existing_sd: str,
    existing_dd: str,
) -> str:

    system_prompt = read_file(
        ROOT
        / "ci"
        / "documentation_agent"
        / "prompts"
        / "system.md"
    )

    sd_template = read_file(
        ROOT
        / "ci"
        / "documentation_agent"
        / "prompts"
        / "sd_template.md"
    )

    dd_template = read_file(
        ROOT
        / "ci"
        / "documentation_agent"
        / "prompts"
        / "dd_template.md"
    )

    source_code = "\n\n".join(
        f"""
===== SOURCE FILE: {path} =====

{content}
"""
        for path, content in source_files.items()
    )

    return f"""
{system_prompt}

========================
SD TEMPLATE
========================

{sd_template}

========================
DD TEMPLATE
========================

{dd_template}

========================
EXISTING SD.md
========================

{existing_sd}

========================
EXISTING DD.md
========================

{existing_dd}

========================
GIT DIFF
========================

{git_diff}

========================
RELEVANT SOURCE CODE
========================

{source_code}
"""


def generate_documentation(
    git_diff: str,
    source_files: dict[str, str],
) -> dict:

    existing_sd = read_file(
        ROOT / "docs" / "SD.md"
    )

    existing_dd = read_file(
        ROOT / "docs" / "DD.md"
    )

    prompt = build_prompt(
        git_diff=git_diff,
        source_files=source_files,
        existing_sd=existing_sd,
        existing_dd=existing_dd,
    )

    response_schema = {
        "type": "object",
        "properties": {
            "documentation_required": {
                "type": "boolean"
            },
            "reason": {
                "type": "string"
            },
            "files": {
                "type": "object",
                "properties": {
                    "docs/SD.md": {
                        "type": "string"
                    },
                    "docs/DD.md": {
                        "type": "string"
                    }
                },
                "additionalProperties": False
            }
        },
        "required": [
            "documentation_required",
            "reason",
            "files"
        ],
        "additionalProperties": False
    }

    interaction = client.interactions.create(
        model=MODEL,
        input=prompt,
        response_format={
            "type": "text",
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "documentation_result",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "documentation_required": {
                                "type": "boolean"
                            },
                            "reason": {
                                "type": "string"
                            },
                            "files": {
                                "type": "object",
                                "properties": {
                                    "docs/SD.md": {
                                        "type": "string"
                                    },
                                    "docs/DD.md": {
                                        "type": "string"
                                    }
                                },
                                "additionalProperties": False
                            }
                        },
                        "required": [
                            "documentation_required",
                            "reason",
                            "files"
                        ],
                        "additionalProperties": False
                    }
                }
            }
        }
    )

    text = interaction.output_text.strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            "Gemini returned invalid JSON:\n\n"
            + text
        ) from exc