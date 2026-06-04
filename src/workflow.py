from functools import partial
from langgraph.graph import StateGraph
from src.nodes.classifier import classify_question
from src.nodes.query_builder import build_query
from src.nodes.executor import execute_query
from src.nodes.validator import validate_and_retry
from src.nodes.formatter import format_answer
from src.nodes.chart_builder import build_chart
from src.graph import GraphState





def build_workflow(
    db_connection
):

    workflow = StateGraph(
        GraphState
    )

    workflow.add_node(
        "classifier",
        classify_question
    )

    workflow.add_node(
        "query_builder",
        build_query
    )

    workflow.add_node(
        "executor",
        partial(
            execute_query,
            db_connection=db_connection
        )
    )

    workflow.add_node(
        "validator",
        validate_and_retry
    )

    workflow.add_node(
        "formatter",
        format_answer
    )

    workflow.add_node(
        "chart_builder",
        build_chart
    )

    workflow.set_entry_point(
        "classifier"
    )

    def route_from_classifier(
        state: GraphState
    ):

        classification = state.get(
            "classification",
            {}
        )

        if (
            classification.get(
                "classification"
            ) == "answerable"
        ):

            return "query_builder"

        return "formatter"

    def route_from_validator(
        state: GraphState
    ):

        if (
            state.get("error")
            == "Malformed JSON"
            and state.get(
                "json_retry_count",
                0
            ) < 2
        ):

            return "query_builder"

        if (
            state.get("error")
            and "SQL Execution Failed"
            in state["error"]
        ):

            if (
                state.get(
                    "retry_count",
                    0
                ) < 2
            ):

                return "query_builder"

        return "formatter"

    workflow.add_conditional_edges(
        "classifier",
        route_from_classifier
    )

    workflow.add_conditional_edges(
        "validator",
        route_from_validator
    )

    workflow.add_edge(
        "query_builder",
        "executor"
    )

    workflow.add_edge(
        "executor",
        "validator"
    )

    workflow.add_edge(
        "formatter",
        "chart_builder"
    )

    workflow.add_edge(
        "chart_builder",
        "__end__"
    )

    return workflow.compile()
