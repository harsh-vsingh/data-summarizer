import uuid

import gradio as gr

from dotenv import load_dotenv

from src.loader import load_data
from src.workflow import build_workflow

load_dotenv()

db_connection, schema_context = load_data()

app = build_workflow(
    db_connection
)


def build_query_details(
    sql,
    dataframe,
    warnings=None
):

    warnings = warnings or []

    details = ""

    if warnings:

        details += "### Warnings\n"

        for warning in warnings:

            details += (
                f"- {warning}\n"
            )

        details += "\n"

    if sql:

        details += (
            "### Generated SQL\n"
            "```sql\n"
            f"{sql}\n"
            "```\n\n"
        )

    if dataframe is not None:

        preview_df = dataframe.head(20)

        details += (
            "### Result Preview "
            "(first 20 rows)\n\n"
        )

        details += (
            preview_df.to_markdown(
                index=False
            )
        )

    return details


def run_graph(
    question,
    chat_history
):

    if not question.strip():

        return (
            "",
            chat_history,
            None,
            None,
            None,
            None,
            ""
        )

    chat_history = (
        chat_history or []
    )

    chat_history.append(
        {
            "role": "user",
            "content": question
        }
    )

    chat_history.append(
        {
            "role": "assistant",
            "content": (
                "Running analytical pipeline..."
            )
        }
    )

    yield (
        "",
        chat_history,
        None,
        None,
        None,
        None,
        ""
    )

    config = {
        "configurable": {
            "thread_id": str(
                uuid.uuid4()
            )
        }
    }

    initial_state = {
        "question": question,
        "schema_context": (
            schema_context
        ),
        "retry_count": 0,
        "json_retry_count": 0
    }

    final_state = app.invoke(
        initial_state,
        config=config
    )

    answer = final_state.get(
        "answer_text",
        "No answer generated."
    )

    charts = final_state.get(
        "chart_figures",
        []
    )

    results = final_state.get(
        "query_results",
        []
    )

    warnings = final_state.get(
        "warnings",
        []
    )

    details_markdown = ""

    if results:

        for idx, result in enumerate(results):

            sql = result.get(
                "sql",
                ""
            )

            dataframe = result.get(
                "dataframe"
            )

            details_markdown += (
                f"\n\n## Query "
                f"{idx + 1}\n\n"
            )

            details_markdown += (
                build_query_details(
                    sql,
                    dataframe,
                    warnings
                )
            )

    chat_history[-1] = {
        "role": "assistant",
        "content": answer
    }

    yield (
        "",
        chat_history,

        charts[0]
        if len(charts) > 0
        else None,

        charts[1]
        if len(charts) > 1
        else None,

        charts[2]
        if len(charts) > 2
        else None,

        charts[3]
        if len(charts) > 3
        else None,

        details_markdown
    )


with gr.Blocks(
    title="Government Data Agent",
    fill_height=True
) as demo:

    gr.Markdown(
        """
# Talk to Government Data

Ask analytical questions about
Indian crop production data.
"""
    )

    with gr.Row():

        # LEFT SIDE
        with gr.Column(scale=3):

            chatbot = gr.Chatbot(
                height="75vh"
            )

            with gr.Accordion(
                "Query Details",
                open=False
            ):

                details_output = (
                    gr.Markdown()
                )

            with gr.Row():

                question_box = (
                    gr.Textbox(
                        placeholder=(
                            "Ask a question..."
                        ),
                        container=False,
                        scale=8
                    )
                )

                submit_btn = (
                    gr.Button(
                        "Send",
                        scale=1
                    )
                )

            with gr.Row():

                clear_btn = (
                    gr.Button(
                        "Clear Chat"
                    )
                )

        # RIGHT SIDE
        with gr.Column(scale=2):

            gr.Markdown(
                "## Charts"
            )

            chart_1 = gr.Plot(
                label="Chart 1"
            )

            chart_2 = gr.Plot(
                label="Chart 2"
            )

            chart_3 = gr.Plot(
                label="Chart 3"
            )

            chart_4 = gr.Plot(
                label="Chart 4"
            )

    gr.Examples(
        examples=[
            [
                "Show the top 10 "
                "rice producing states."
            ],
            [
                "Show year wise wheat "
                "production trend in Punjab."
            ],
            [
                "Compare rice production "
                "across states."
            ],
            [
                "Find average rice yield "
                "by state."
            ],
            [
                "List crops grown in "
                "Maharashtra."
            ]
        ],
        inputs=question_box
    )

    question_box.submit(
        run_graph,
        [
            question_box,
            chatbot
        ],
        [
            question_box,
            chatbot,
            chart_1,
            chart_2,
            chart_3,
            chart_4,
            details_output
        ]
    )

    submit_btn.click(
        run_graph,
        [
            question_box,
            chatbot
        ],
        [
            question_box,
            chatbot,
            chart_1,
            chart_2,
            chart_3,
            chart_4,
            details_output
        ]
    )

    clear_btn.click(
        lambda: (
            [],
            None,
            None,
            None,
            None,
            ""
        ),
        outputs=[
            chatbot,
            chart_1,
            chart_2,
            chart_3,
            chart_4,
            details_output
        ]
    )

if __name__ == "__main__":

    demo.launch(
        share=True,
        theme=gr.themes.Soft()
    )