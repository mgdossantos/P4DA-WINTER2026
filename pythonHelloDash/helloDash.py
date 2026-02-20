# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
#https://dash.plotly.com/
#dcc=dash core component
from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

#create application
app2 = Dash()

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.bar(df, x="Fruit", y="Amount")

#<div>
  #<h1>Title</h1>
  #<p>Text</p>
#</div>

#create the layout
app2.layout = html.Div(children=[
    html.H1('Hello Dash Test 2'),
    html.Div('Dash: A web application framework for your data.'),
    dcc.Graph(id='example-graph',figure=fig)
])

if __name__ == '__main__':
    #run the application, local
    app2.run_server(debug=True, host="127.0.0.1", port=8050, use_reloader=False)