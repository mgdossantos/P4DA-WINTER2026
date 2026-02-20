import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

# -------------------------
# Part A) Data (pandas)
# -------------------------
df = pd.DataFrame({
    "student": ["Ana", "Bob", "Carla", "Daniel", "Eva", "Frank", "Gabi", "Hugo"],
    "class":   ["A",   "A",   "A",     "B",      "B",   "B",     "A",    "B"],
    "exam":    ["Math","Math","Science","Math",  "Science","Science","Math","Math"],
    "grade":   [85,     78,     92,      88,      75,      81,     95,    69]
})

# Precompute dropdown options (clean and stable)
class_options = [{"label": c, "value": c} for c in sorted(df["class"].unique())]
exam_options  = [{"label": e, "value": e} for e in sorted(df["exam"].unique())]

# -------------------------
# Part B) App
# -------------------------
app = Dash(__name__)
app.title = "Grades Dashboard"

app.layout = html.Div(
    style={"maxWidth": "980px", "margin": "24px auto", "fontFamily": "Arial"},
    children=[
        html.H1("Student Grades Dashboard"),

        html.P(
            "Use the filters below to explore grades by class and exam. "
            "The KPI and charts update automatically."
        ),

        html.Div(
            style={"display": "flex", "gap": "16px", "marginBottom": "16px"},
            children=[
                html.Div(
                    style={"flex": "1"},
                    children=[
                        html.Label("Select Class"),
                        dcc.Dropdown(
                            id="class_dd",
                            options=class_options,
                            value=class_options[0]["value"],
                            clearable=False
                        ),
                    ]
                ),
                html.Div(
                    style={"flex": "1"},
                    children=[
                        html.Label("Select Exam"),
                        dcc.Dropdown(
                            id="exam_dd",
                            options=exam_options,
                            value=exam_options[0]["value"],
                            clearable=False
                        ),
                    ]
                ),
            ]
        ),

        # KPI area
        html.Div(
            id="kpi",
            style={
                "padding": "12px 16px",
                "border": "1px solid #ddd",
                "borderRadius": "10px",
                "marginBottom": "16px",
                "fontSize": "18px"
            }
        ),

        # Charts
        dcc.Graph(id="bar_chart"),
        dcc.Graph(id="hist_chart"),

    ]
)

# -------------------------
# Part C) Callback (logic)
# -------------------------
@app.callback(
    Output("kpi", "children"),
    Output("bar_chart", "figure"),
    Output("hist_chart", "figure"),

    Input("class_dd", "value"),
    Input("exam_dd", "value"),
)
def update_dashboard(selected_class, selected_exam):
    # 1) Filter data (pandas)
    filtered = df[(df["class"] == selected_class) & (df["exam"] == selected_exam)]

    # Safety: handle empty selection (in real datasets, this can happen)
    if filtered.empty:
        kpi_text = "No rows match the selected filters."
        empty_fig = px.bar(title="No data to display")
        return kpi_text, empty_fig, empty_fig

    # 2) Compute KPI(s)
    avg = filtered["grade"].mean()
    #pass_rate = (filtered["grade"] >= 70).mean() * 100
    # % >= 70
    pass_rate = len(filtered[filtered["grade"] > 70]) / len(filtered) * 100

    kpi_text = f"Average grade: {avg:.2f} | Pass rate (>=70): {pass_rate:.1f}% | Students: {len(filtered)}"

    # 3) Build charts (Plotly)
    bar_fig = px.bar(
        filtered,
        x="student",
        y="grade",
        range_y=[0, 100],
        title=f"Grades by Student — Class {selected_class}, Exam {selected_exam}"
    )

    hist_fig = px.histogram(
        filtered,
        x="grade",
        nbins=8,
        title="Grade Distribution (Filtered)"
    )


    return kpi_text, bar_fig, hist_fig


# -------------------------
# Part D) Run server
# -------------------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
