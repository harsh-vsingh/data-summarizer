from ..graph import GraphState


def validate_and_retry(
    state: GraphState
) -> GraphState:

    warnings = []

    for result in state.get(
        "query_results",
        []
    ):

        df = result["dataframe"]

        operation = result.get(
            "operation",
            ""
        )

        if df.empty:

            warnings.append(
                "One query returned no results."
            )

            continue

        lower_cols = [
            c.lower()
            for c in df.columns
        ]

        if operation == "trend":

            if not any(
                "year" in c
                for c in lower_cols
            ):

                warnings.append(
                    "Trend query missing year axis."
                )

        if operation == "top_n":

            if len(df) > 50:

                warnings.append(
                    "Top-N query returned too many rows."
                )

        if (
            "production" in lower_cols
        ):

            prod_col = df.columns[
                lower_cols.index(
                    "production"
                )
            ]

            if (
                df[prod_col] < 0
            ).any():

                warnings.append(
                    "Negative production values detected."
                )

        if df.isnull().all().any():

            warnings.append(
                "One result contains entirely null columns."
            )

    state["warnings"] = warnings

    if (
        state.get("error")
        and "SQL Execution Failed"
        in state["error"]
    ):

        state["retry_count"] = (
            state.get(
                "retry_count",
                0
            ) + 1
        )

    return state
