import pandas as pd


def build_result_summary(
    df: pd.DataFrame,
    operation: str
) -> dict:

    summary = {
        "operation": operation,
        "row_count": len(df),
        "columns": list(df.columns)
    }

    if df.empty:
        return summary

    numeric_cols = (
        df.select_dtypes(
            include="number"
        ).columns
    )

    if len(numeric_cols) > 0:

        metric_col = numeric_cols[-1]

        summary["metric_column"] = (
            metric_col
        )

        summary["metric_min"] = float(
            df[metric_col].min()
        )

        summary["metric_max"] = float(
            df[metric_col].max()
        )

    if "Crop_Year" in df.columns:

        summary["min_year"] = int(
            df["Crop_Year"].min()
        )

        summary["max_year"] = int(
            df["Crop_Year"].max()
        )

    if operation == "top_n":

        first_row = df.iloc[0]

        summary["top_entity"] = str(
            first_row.iloc[0]
        )

        summary["top_value"] = float(
            first_row.iloc[1]
        )

    if operation == "trend":

        if (
            len(numeric_cols) > 0
            and len(df) >= 2
        ):

            metric_col = numeric_cols[-1]

            first_val = (
                df[metric_col]
                .iloc[0]
            )

            last_val = (
                df[metric_col]
                .iloc[-1]
            )

            if last_val > first_val:

                summary[
                    "trend_direction"
                ] = "increasing"

            elif last_val < first_val:

                summary[
                    "trend_direction"
                ] = "decreasing"

            else:

                summary[
                    "trend_direction"
                ] = "stable"

    return summary
