import duckdb
import re
import pandas as pd
from ..graph import GraphState
import time

FORBIDDEN_SQL = [
    "DROP",
    "INSERT",
    "UPDATE",
    "DELETE",
    "ALTER",
    "EXEC",
    "CREATE"
]


def validate_sql(sql: str):
    normalized = sql.strip().upper()

    if not normalized.startswith("SELECT"):
        raise ValueError(
            "Only SELECT statements are allowed."
        )

    for keyword in FORBIDDEN_SQL:
        if re.search(rf"\b{keyword}\b", normalized):
            raise ValueError(
                f"Forbidden SQL keyword detected: "
                f"{keyword}"
            )

    if " dataset " not in f" {sql.lower()} ":
        raise ValueError(
            "Queries must target the dataset table only."
        )


def build_provenance(sql: str) -> str:
    return (
        f"Executed analytical SQL query "
        f"against dataset: {sql}"
    )


def execute_query(
    state: GraphState,
    db_connection
) -> GraphState:

    start_time = time.time()

    query_plans = state.get(
        "query_plans",
        []
    )

    if not query_plans:
        state["error"] = (
            "No SQL query plans found."
        )

        return state

    all_results = []

    try:

        db_connection.execute(
            "SET threads TO 2"
        )

        for idx, plan in enumerate(query_plans):

            sql_query = plan.get("sql")

            print(
                f"\n--- EXECUTING QUERY {idx + 1} ---"
            )

            print(f"SQL:\n{sql_query}")

            validate_sql(sql_query)

            result_df = (
                db_connection
                .execute(sql_query)
                .fetchdf()
            )

            if len(result_df) > 1000:
                result_df = result_df.head(1000)

                state["warning"] = (
                    "Result truncated to first "
                    "1000 rows."
                )

            numeric_cols = (
                result_df
                .select_dtypes(include="number")
                .columns
            )

            for col in numeric_cols:

                if pd.api.types.is_float_dtype(
                    result_df[col]
                ):
                    result_df[col] = (
                        result_df[col]
                        .round(2)
                    )

            print(
                f"Rows Returned: "
                f"{len(result_df)}"
            )

            print(
                f"Columns Returned: "
                f"{list(result_df.columns)}"
            )

            all_results.append({
                "sql": sql_query,
                "dataframe": result_df,
                "chart_type": plan.get(
                    "chart_type"
                ),
                "x_axis_column": plan.get(
                    "x_axis_column"
                ),
                "y_axis_column": plan.get(
                    "y_axis_column"
                ),
                "chart_reason": plan.get(
                    "chart_reason"
                )
            })

        state["query_results"] = all_results

        if all_results:
            state["query_result"] = (
                all_results[0]["dataframe"]
            )

            state["provenance_sql"] = (
                all_results[0]["sql"]
            )

        state["provenance_description"] = (
            "Executed analytical SQL queries "
            "against dataset."
        )

        state["chart_provenance"] = (
            "Charts generated directly "
            "from executed query results."
        )

        state["error"] = None

    except Exception as e:

        print(
            f"Execution Error: {str(e)}"
        )

        state["error"] = (
            f"SQL Execution Failed: {str(e)}"
        )

        state["query_results"] = []

    end_time = time.time()

    print(
        f"Execution Time: "
        f"{end_time - start_time:.2f} seconds"
    )

    return state
