import pandas as pd
import duckdb
from pathlib import Path

def load_prompt(filename: str) -> str:
    path = Path(__file__).parent / "prompts" / filename
    return path.read_text(encoding="utf-8")

CLASSIFIER_PROMPT = load_prompt("classifier_prompt.txt")
QUERY_BUILDER_PROMPT = load_prompt("query_builder_prompt.txt")
FORMATTER_PROMPT = load_prompt("formatter_prompt.txt")


POSSIBLE_TIME_COLUMNS = [
    "year",
    "crop_year",
    "date",
    "time"
]

POSSIBLE_NUMERIC_COLUMNS = [
    "area",
    "production",
    "yield",
    "rainfall",
    "population",
    "count",
    "value"
]


def normalize_column_name(col: str) -> str:
    return (
        col.strip()
        .lower()
        .replace(" ", "_")
    )


def infer_time_column(columns):
    normalized = [normalize_column_name(c) for c in columns]

    for candidate in POSSIBLE_TIME_COLUMNS:
        if candidate in normalized:
            idx = normalized.index(candidate)
            return columns[idx]

    return None


def infer_numeric_columns(df: pd.DataFrame):
    numeric_cols = []

    for col in df.columns:
        normalized = normalize_column_name(col)

        if any(key in normalized for key in POSSIBLE_NUMERIC_COLUMNS):
            numeric_cols.append(col)

    return numeric_cols


def infer_categorical_columns(df: pd.DataFrame):
    categorical_cols = []

    for col in df.columns:
        if df[col].dtype == "object":
            categorical_cols.append(col)

    return categorical_cols


def clean_dataframe(df: pd.DataFrame):
    df.columns = [c.strip() for c in df.columns]

    categorical_cols = infer_categorical_columns(df)

    for col in categorical_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
        )

    for col in categorical_cols:
        nunique = df[col].nunique(dropna=True)

        if nunique < 500:
            df[col] = df[col].str.title()

    numeric_cols = infer_numeric_columns(df)

    for col in numeric_cols:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    time_col = infer_time_column(df.columns)

    if time_col:
        df[time_col] = pd.to_numeric(
            df[time_col],
            errors="coerce"
        )

        df = df.dropna(subset=[time_col])

        df[time_col] = df[time_col].astype(int)

    return df


def build_schema_context(df: pd.DataFrame):
    lines = []

    lines.append("Table: dataset")
    lines.append(
        f"Columns: {', '.join(df.columns)}"
    )

    dtype_str = ", ".join(
        [f"{c} ({str(df[c].dtype)})" for c in df.columns]
    )

    lines.append(f"Data Types: {dtype_str}")

    time_col = infer_time_column(df.columns)

    if time_col:
        min_year = int(df[time_col].min())
        max_year = int(df[time_col].max())

        lines.append(
            f"Time Range: {min_year}-{max_year}"
        )

    categorical_cols = infer_categorical_columns(df)

    for col in categorical_cols[:10]:
        top_values = (
            df[col]
            .value_counts(dropna=True)
            .head(5)
            .index
            .astype(str)
            .tolist()
        )

        lines.append(
            f"Top values for {col}: {', '.join(top_values)}"
        )

    numeric_cols = infer_numeric_columns(df)

    if (
        "Area" in df.columns
        and "Production" in df.columns
    ):
        lines.append(
            "Derivable Metrics:"
        )

        lines.append(
            "- Yield = Production / Area"
        )

    return "\n".join(lines)


def load_data(
    data_path: str = "data/crop_production.csv"
):
    if data_path.endswith(".csv"):
        df = pd.read_csv(
            data_path,
            encoding="utf-8"
        )

    elif data_path.endswith(".xlsx"):
        df = pd.read_excel(data_path)

    else:
        raise ValueError(
            "Unsupported file type. Use CSV or XLSX."
        )

    df = clean_dataframe(df)

    con = duckdb.connect(
        database=":memory:",
        read_only=False
    )

    con.execute("CREATE TABLE dataset AS SELECT * FROM df")

    schema_context = build_schema_context(df)

    print("Dataset loaded successfully")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    return con, schema_context