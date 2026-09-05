"""Import recorded responses without making network calls."""

import json


def load_responses(path):
    with open(path, encoding="utf-8") as source:
        records = json.load(source)
    if not isinstance(records, list) or not records:
        raise ValueError("Response file must contain a non-empty array")
    identities = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Each response must be an object")
        query = record.get("query_item")
        if not isinstance(query, dict) or not all(
            query.get(k) for k in ("id", "query", "target_brand", "expected_entities")
        ):
            raise ValueError("query_item requires id, query, target_brand and expected_entities")
        if (
            not isinstance(record.get("response_text"), str)
            or not record["response_text"].strip()
            or not record.get("model")
        ):
            raise ValueError("Each response requires model and non-empty response_text")
        identity = (query["id"], record["model"])
        if identity in identities:
            raise ValueError("Duplicate query/model response")
        identities.add(identity)
        previous = record.get("provenance", {})
        record["provenance"] = {
            **previous,
            "source_execution_mode": previous.get("execution_mode", "unknown"),
            "execution_mode": "imported",
            "verification": "user_supplied",
        }
    return records
