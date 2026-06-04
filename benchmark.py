import time

from app import app
from app import schema_context
from app import db_connection


QUERIES = [
    # "Show the top 10 rice producing states.",
    # "List wheat production by state in 2015.",
    # "Find the total wheat production by Punjab.",
    # "Show year wise wheat production trend in Punjab.",
    # "Compare rice production across states.",
    # "Show top 20 districts by rice production.",
    # "Find average rice yield by state.",
    # "Show cotton production trends over years.",
    # "List crops grown in Maharashtra.",
    # "Which state has the highest wheat yield?",
    # "Show season wise crop and yield trend for Punjab.",
    # "Find total production of sugarcane by year."
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
        final_state = app.invoke(initial_state)

        end = time.time()

        print(
            f"\nTOTAL PIPELINE TIME: "
            f"{end - start:.2f}s"
        )

        print("\nFINAL ANSWER:")
        print(final_state.get("answer_text"))

        print("\nGENERATED SQL:")
        print(final_state.get("provenance_sql"))

        print("\nERROR:")
        print(final_state.get("error"))

    except Exception as e:
        end = time.time()

        print(f"\nPIPELINE FAILED: {str(e)}")

        print(
            f"FAILED AFTER: "
            f"{end - start:.2f}s"
        )
