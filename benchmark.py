import time

from app import app
from app import schema_context
from app import db_connection


QUERIES = [

    # Ranking + aggregation
    "Show the top 10 rice producing states.",

    # Filtering + grouping
    "List wheat production by state in 2015.",

    # Time-series trend
    "Show year wise wheat production trend in Punjab.",

    # Distinct categorical lookup
    "List crops grown in Maharashtra.",

    # Comparative aggregation
    "Compare rice production across states.",

    # Year-wise aggregation (hand-verifiable)
    "Find total production of sugarcane by year.",

    # Multi-dimensional aggregation
    "Show season wise crop and yield trend for Punjab.",

    # Top-k district ranking
    "Show top 20 districts by rice production.",

    # Out-of-scope refusal
    "Find the crop with most stars.",

    # Ambiguity handling
    "Show production trends."
]



for i, query in enumerate(QUERIES, 1):

    print("\n" + "=" * 80)
    print(f"QUERY {i}")
    print("=" * 80)

    print(f"QUESTION: {query}")

    initial_state = {
        "question": query,
        "schema_context": schema_context,
        "db_connection": db_connection,
        "conversation_context": {
            "history": []
        },
        "retry_count": 0,
        "json_retry_count": 0
    }

    start = time.time()

    try:

        final_state = app.invoke(
            initial_state
        )

        end = time.time()

        print(
            f"\nTOTAL PIPELINE TIME: "
            f"{end - start:.2f}s"
        )

        print("\nFINAL ANSWER:")
        print(
            final_state.get(
                "answer_text"
            )
        )

        print("\nGENERATED SQL:")
        print(
            final_state.get(
                "provenance_sql"
            )
        )

        print("\nERROR:")
        print(
            final_state.get(
                "error"
            )
        )

    except Exception as e:

        end = time.time()

        print(
            f"\nPIPELINE FAILED: "
            f"{str(e)}"
        )

        print(
            f"FAILED AFTER: "
            f"{end - start:.2f}s"
        )
