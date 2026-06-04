import json
import re


def parse_llm_json(raw):

    if isinstance(raw, list):

        raw = "\n".join(
            str(item)
            for item in raw
        )

    raw = str(raw).strip()

    raw = re.sub(
        r"^```json",
        "",
        raw,
        flags=re.IGNORECASE
    ).strip()

    raw = re.sub(
        r"^```",
        "",
        raw
    ).strip()

    raw = re.sub(
        r"```$",
        "",
        raw
    ).strip()

    start = raw.find("{")
    end = raw.rfind("}")

    if start == -1 or end == -1:

        raise ValueError(
            "No JSON object found."
        )

    raw = raw[start:end + 1]

    return json.loads(raw)
