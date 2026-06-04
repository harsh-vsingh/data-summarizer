from typing import TypedDict, Dict, Any, List
import pandas as pd


class GraphState(
    TypedDict,
    total=False
):

    question: str

    rewritten_question: str

    schema_context: str

    classification: Dict[
        str,
        Any
    ]

    operation_json: Dict[
        str,
        Any
    ]

    query_plans: List[
        Dict[str, Any]
    ]

    query_results: List[
        Dict[str, Any]
    ]

    retry_count: int

    json_retry_count: int

    answer_text: str

    clarifying_question: str

    conversation_context: Dict[
        str,
        Any
    ]

    provenance_sql: str | None

    provenance_description: (
        str | None
    )

    chart_provenance: str | None

    chart_figures: List[Any]

    error: str | None

    warnings: List[str]

    raw_llm_output: str