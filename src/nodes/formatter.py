from ..graph import GraphState
from ..llm import get_llm
from ..loader import FORMATTER_PROMPT
import time
from ..usg import print_token_usage
from ..summary import build_result_summary

def format_answer(
    state: GraphState
) -> GraphState:

    start_time = time.time()

    classification = state.get(
        "classification",
        {}
    )

    if (
        classification.get(
            "classification"
        ) == "ambiguous"
    ):

        state["answer_text"] = state.get(
            "clarifying_question",
            "Could you clarify your question?"
        )

        return state

    if (
        classification.get(
            "classification"
        ) == "out_of_scope"
    ):

        state["answer_text"] = (
            f"Out of scope: "
            f"{classification.get('out_of_scope_reason', 'N/A')}"
        )

        return state

    if state.get("error"):

        state["answer_text"] = (
            f"Execution failed: "
            f"{state['error']}"
        )

        return state

    results = state.get(
        "query_results",
        []
    )

    if not results:

        state["answer_text"] = (
            "No matching data was found."
        )

        return state

    first_result = results[0]

    df = first_result["dataframe"]

    if df.empty:

        state["answer_text"] = (
            "No matching data was found."
        )

        return state

    operation = first_result.get(
        "operation",
        ""
    )

    if operation == "aggregate":

        row = df.iloc[0]

        metric = df.columns[-1]

        value = row[metric]

        if isinstance(
            value,
            (int, float)
        ):

            value = f"{value:,.2f}"

        state["answer_text"] = (
            f"{metric.replace('_', ' ').title()}: "
            f"{value}"
        )

        return state

    if operation == "top_n":

        row = df.iloc[0]

        entity_col = df.columns[0]

        metric_col = df.columns[1]

        entity = row[entity_col]

        value = row[metric_col]

        if isinstance(
            value,
            (int, float)
        ):

            value = f"{value:,.2f}"

        state["answer_text"] = (
            f"Top result: {entity} "
            f"with {value}."
        )

        return state

    llm = get_llm()

    result_tables = []

    for idx, result in enumerate(results):

        result_df = result[
            "dataframe"
        ]

        table_md = (
            result_df
            .head(20)
            .to_markdown(index=False)
        )

        result_tables.append(
            f"RESULT {idx + 1}:\n"
            f"{table_md}"
        )

    result_summaries = []

    for idx, result in enumerate(results):

        result_df = result[
            "dataframe"
        ]

        operation = result.get(
            "operation",
            ""
        )

        summary = build_result_summary(
            result_df,
            operation
        )

        formatted_df = (
            result_df.copy()
        )

        numeric_cols = (
            formatted_df
            .select_dtypes(
                include="number"
            )
            .columns
        )

        for col in numeric_cols:

            formatted_df[col] = (
                formatted_df[col]
                .apply(
                    lambda x:
                    f"{x:,.2f}"
                    if isinstance(
                        x,
                        (int, float)
                    )
                    else x
                )
            )

        table_md = (
            formatted_df
            .head(10)
            .to_markdown(index=False)
        )

        result_summaries.append(
            {
                "summary": summary,
                "preview_table": table_md
            }
        )


    warning_context = ""

    warnings = state.get(
        "warnings",
        []
    )

    if warnings:

        warning_context = (
            "VALIDATOR WARNINGS:\n"
            + "\n".join(warnings)
        )

    prompt = FORMATTER_PROMPT.format(
        question=(
            state.get(
                "rewritten_question"
            )
            or state["question"]
        ),
        result_table=result_summaries,
        provenance_description="",
        warning_context=warning_context
    )

    response = llm.invoke(prompt)

    print_token_usage(response)

    content = response.content

    if isinstance(content, list):

        content = "\n".join(
            str(item)
            for item in content
        )

    content = str(content)

    state["answer_text"] = (
        content.strip()
    )

    end_time = time.time()

    print(
        f"Formatting Time: "
        f"{end_time - start_time:.2f} seconds"
    )

    return state
