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

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "OBJECT",
                "properties": {
                    "documentation_required": {
                        "type": "BOOLEAN"
                    },
                    "reason": {
                        "type": "STRING"
                    },
                    "sd": {
                        "type": "STRING"
                    },
                    "dd": {
                        "type": "STRING"
                    }
                },
                "required": [
                    "documentation_required",
                    "reason",
                    "sd",
                    "dd"
                ]
            }
        }
    )

    try:

        return json.loads(
            response.text
        )

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            "Gemini returned invalid JSON:\n\n"
            + response.text
        ) from exc