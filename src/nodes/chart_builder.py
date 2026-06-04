import plotly.express as px

from ..graph import GraphState


def build_chart(
    state: GraphState
) -> GraphState:

    figures = []

    for result in state.get(
        "query_results",
        []
    ):

        df = result["dataframe"]

        chart_type = result.get(
            "chart_type"
        )

        x_axis = result.get(
            "x_axis_column"
        )

        y_axis = result.get(
            "y_axis_column"
        )

        title = result.get(
            "title",
            "Chart"
        )

        fig = None

        try:

            if (
                chart_type == "line"
                and x_axis in df.columns
                and y_axis in df.columns
            ):

                fig = px.line(
                    df,
                    x=x_axis,
                    y=y_axis,
                    title=title,
                    markers=True
                )

            elif (
                chart_type == "bar"
                and x_axis in df.columns
                and y_axis in df.columns
            ):

                fig = px.bar(
                    df,
                    x=x_axis,
                    y=y_axis,
                    title=title
                )

            if fig:

                fig.update_layout(
                    title_x=0.5
                )

                figures.append(fig)

        except Exception:
            pass

    state["chart_figures"] = figures

    return state
