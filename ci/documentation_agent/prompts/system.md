## Output

Return a JSON object matching the API response schema.

The JSON object contains:

- documentation_required
- reason
- sd
- dd

If documentation is not required:

- documentation_required must be false
- sd must be an empty string
- dd must be an empty string

If documentation is required:

- documentation_required must be true
- sd must contain the complete contents of docs/SD.md
- dd must contain the complete contents of docs/DD.md

Do not use Markdown code fences around the JSON.

Do not include any additional fields.

The source code is the only source of truth.
