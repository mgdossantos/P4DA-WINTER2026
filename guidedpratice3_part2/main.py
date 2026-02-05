from dash import Dash, html
import os
print("RUNNING FILE:", __file__)
print("CWD:", os.getcwd())
firstApp = Dash(__name__)

firstApp.layout = html.Div([
    html.H1("My First Dash App"),
    html.P("This is a simple dashboard")
])

if __name__ == "__main__":
    firstApp.run(debug=True, use_reloader=True)