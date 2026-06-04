import uuid
import gradio as gr
from dotenv import load_dotenv
from functools import partial
from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver
from src.graph import GraphState
from src.loader import load_data
from src.nodes.classifier import classify_question
from src.nodes.query_builder import build_query
from src.nodes.executor import execute_query
from src.nodes.validator import validate_and_retry
from src.nodes.formatter import format_answer
from src.nodes.chart_builder import build_chart

load_dotenv()

db_connection, schema_context = load_data()

memory_cm = SqliteSaver.from_conn_string(":memory:")
memory = memory_cm.__enter__()

workflow = StateGraph(GraphState)
workflow.add_node("classifier", classify_question)
workflow.add_node("query_builder", build_query)
workflow.add_node(
    "executor",
    partial(execute_query, db_connection=db_connection)
)
workflow.add_node("validator", validate_and_retry)
workflow.add_node("formatter", format_answer)
workflow.add_node("chart_builder", build_chart)

workflow.set_entry_point("classifier")


def route_from_classifier(state: GraphState):
    classification = state.get("classification", {})

    if classification.get("classification") == "answerable":
        return "query_builder"

    return "formatter"


def route_from_validator(state: GraphState):
    if state.get("error") == "Malformed JSON" and state.get("json_retry_count", 0) < 2:
        return "query_builder"

    if state.get("error") and "SQL Execution Failed" in state["error"]:
        if state.get("retry_count", 0) < 2:
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

workflow.add_edge("query_builder", "executor")
workflow.add_edge("executor", "validator")
workflow.add_edge("formatter", "chart_builder")
workflow.add_edge("chart_builder", "__end__")

# app = workflow.compile(checkpointer=memory)
app = workflow.compile()


def run_graph(question, chat_history):
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4())
        }
    }

    initial_state = {
        "question": question,
        "schema_context": schema_context,
        "retry_count": 0,
        "json_retry_count": 0,
        "conversation_context": {
            "history": chat_history or []
        }
    }

    final_state = app.invoke(initial_state, config=config)

    answer = final_state.get(
        "answer_text",
        "No answer generated."
    )

    charts = final_state.get(
        "chart_figures",
        []
    )

    chart = charts[0] if charts else None

    sql = final_state.get(
        "provenance_sql",
        ""
    )

    results = final_state.get(
        "query_results",
        []
    )

    data = (
        results[0]["dataframe"]
        if results
        else None
    )

    chat_history = chat_history or []

    chat_history.append({
        "role": "user",
        "content": question
    })

    chat_history.append({
        "role": "assistant",
        "content": answer
    })

    return "", chat_history, chart, sql, data


with gr.Blocks(
    title="Government Data Agent"
) as demo:

    gr.Markdown("# Talk to Government Data")

    with gr.Row():

        with gr.Column(scale=1):
            gr.Markdown("### Dataset Info")

            gr.Markdown(
                f"```text\n{schema_context}\n```"
            )

        with gr.Column(scale=3):

            chatbot = gr.Chatbot(
                height=500
            )

            question_box = gr.Textbox(
                label="Your Question"
            )

            chart_output = gr.Plot(label="Chart")

            with gr.Accordion(
                "Query Details",
                open=False
            ):
                sql_display = gr.Code(
                    label="Generated SQL",
                    language="sql"
                )

                df_display = gr.DataFrame(
                    label="Query Result"
                )

            question_box.submit(
                run_graph,
                [question_box, chatbot],
                [
                    question_box,
                    chatbot,
                    chart_output,
                    sql_display,
                    df_display
                ]
            )

if __name__ == "__main__":
    demo.launch(
        share=True,
        theme=gr.themes.Soft()
    )