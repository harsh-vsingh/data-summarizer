from ..graph import GraphState
from ..llm import get_llm
from ..loader import QUERY_BUILDER_PROMPT
from ..utils import parse_llm_json
import time
import json
from ..usg import print_token_usage



def build_query(state: GraphState) -> GraphState:
    start_time = time.time()

    print(
        f"SQL Retries: "
        f"{state.get('retry_count', 0)}"
    )

    print(
        f"JSON Retries: "
        f"{state.get('json_retry_count', 0)}"
    )

    llm = get_llm()

    retry_context = ""

    if state.get("json_retry_count", 0) > 0:
        retry_context = f"""
PREVIOUS OUTPUT WAS MALFORMED JSON:
Raw output received:
{state.get("raw_llm_output", "")}

Your output must be valid JSON only.
"""

    elif state.get("retry_count", 0) > 0:
        retry_context = f"""
PREVIOUS ATTEMPT FAILED:
SQL attempted:
{state.get("provenance_sql", "N/A")}

Error received:
{state.get("error", "")}

Fix the SQL. Do not repeat the same mistake.
"""

    question = (
        state.get("rewritten_question")
        or state["question"]
    )

    prompt = QUERY_BUILDER_PROMPT.format(
        schema_context=state["schema_context"],
        retry_context=retry_context,
        question=question
    )

    print(f"Prompt Length: {len(prompt)} chars")

    try:
        response = llm.invoke(prompt)
        print_token_usage(response)
        content = response.content

        if isinstance(content, list):

            content = "\n".join(
                str(item)
                for item in content
            )

        content = str(content)
        print(
            f"LLM Response Length: "
            f"{len(content)} chars"
        )

        state["raw_llm_output"] = content

        result = parse_llm_json(content)

        state["query_plans"] = result.get(
            "queries",
            []
        )

        for query in state["query_plans"]:

            query["operation"] = result.get(
                "operation",
                ""
            )


        for idx, query_plan in enumerate(
            state["query_plans"]
        ):

            print(
                f"\nGenerated SQL "
                f"{idx + 1}:"
            )

            print(query_plan.get("sql"))

        state["operation_json"] = result

        state["error"] = None


    except json.JSONDecodeError:
        print("Malformed JSON detected")

        state["error"] = "Malformed JSON"

        state["json_retry_count"] = (
            state.get("json_retry_count", 0) + 1
        )

    end_time = time.time()
    print(f"Query Building Time: {end_time - start_time:.2f} seconds")

    return state