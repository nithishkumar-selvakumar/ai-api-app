import json
import os
from pathlib import Path

import time

from google import genai
from google.genai import types
from google.genai.errors import ServerError

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

    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )

    prompt = build_prompt(
        git_diff=git_diff,
        source_files=source_files,
    )

    max_retries = 5

    for attempt in range(max_retries):

        try:

            print(
                f"\nCalling Gemini "
                f"(attempt {attempt + 1}/{max_retries})..."
            )

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema={
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
                            },
                        },
                        "required": [
                            "documentation_required",
                            "reason",
                            "sd",
                            "dd",
                        ],
                    },
                ),
            )

            return json.loads(
                response.text
            )

        except ServerError as exc:

            if attempt == max_retries - 1:
                raise

            wait_seconds = 2 ** attempt

            print(
                f"Gemini temporarily unavailable "
                f"(503). Retrying in "
                f"{wait_seconds} seconds..."
            )

            time.sleep(wait_seconds)

    raise RuntimeError(
        "Gemini request failed after retries."
    )