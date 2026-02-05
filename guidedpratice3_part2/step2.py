from dash import Dash, html
from dash import dcc
import pandas as pd
import plotly.express as px
from dash import Input, Output

df = pd.DataFrame({
    "student": ["Ana", "Bob", "Carla", "Daniel"],
    "class": ["A", "A", "B", "B"],
    "grade": [85, 78, 90, 88]
})
app = Dash(__name__)

app.layout = html.Div([
    html.H1("My First Dash App"),
    html.P("This is a simple dashboard")
])


app.layout = html.Div([
    html.H1("Grades Dashboard"),

    dcc.Dropdown(
        id="class_dd",
        options=[{"label": c, "value": c} for c in df["class"].unique()],
        value="A"
    ),

    dcc.Graph(id="graph")
])

if __name__ == "__main__":
    app.run_server(debug=True)