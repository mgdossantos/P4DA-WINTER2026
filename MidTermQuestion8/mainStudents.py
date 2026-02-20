"""
Q8 (15 pts) — Mini dashboard with Dash (TEMPLATE FOR STUDENTS)

Goal: You are graded on how well you CONNECT DATA -> FILTERS -> KPIs + GRAPH via callbacks.
✅ Layout + styling are provided.
🧠 Your work is mainly inside the TODO blocks.

Rubric focus:
- (8 pts) Callback updates graph based on selected filters
- (3 pts) KPIs update with the filters (at least 2 KPIs)
- (4 pts) Layout has required components (already done)
"""

import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# ------------------------------------------------------------
# 0) Load data
# ------------------------------------------------------------
df = pd.read_csv("df_clean.csv")

# ------------------------------------------------------------
# 1) Column detection / mapping (provided)
# ------------------------------------------------------------
def pick_col(df: pd.DataFrame, candidates):
    cols = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols:
            return cols[cand.lower()]
    return None

BOROUGH_COL = pick_col(df, ["borough", "arrondissement", "quartier", "borough_name"])
REQUEST_COL = pick_col(df, ["request_type", "requete", "request", "type", "category"])
STATUS_COL  = pick_col(df, ["status", "etat", "state", "result", "outcome"])
CANCEL_COL  = pick_col(df, ["is_cancelled", "cancelled", "canceled", "annule", "annulée", "annulee"])
OPENED_COL  = pick_col(df, ["created_at", "date_created", "date_ouverture", "date_ouverture_dt", "opened_at"])
CLOSED_COL  = pick_col(df, ["closed_at", "date_closed", "date_fermeture", "date_fermeture_dt", "closed"])
SERVICE_H_COL = pick_col(df, ["service_time_h", "service_time_hours", "service_hours", "temps_service_h"])
SERVICE_D_COL = pick_col(df, ["service_time_d", "service_time_days", "service_days", "temps_service_j"])

missing = []
if BOROUGH_COL is None: missing.append("borough/arrondissement")
if REQUEST_COL is None: missing.append("request_type/requete")
if missing:
    raise ValueError(
        "Could not find required columns in df_clean: "
        + ", ".join(missing)
        + ". Rename columns or update candidates."
    )

# Ensure service time hours (provided)
if SERVICE_H_COL is None:
    if SERVICE_D_COL is not None:
        df["_service_time_hours"] = pd.to_numeric(df[SERVICE_D_COL], errors="coerce") * 24.0
    elif (OPENED_COL is not None) and (CLOSED_COL is not None):
        df["_opened_dt"] = pd.to_datetime(df[OPENED_COL], errors="coerce")
        df["_closed_dt"] = pd.to_datetime(df[CLOSED_COL], errors="coerce")
        df["_service_time_hours"] = (df["_closed_dt"] - df["_opened_dt"]).dt.total_seconds() / 3600.0
    else:
        df["_service_time_hours"] = np.nan
    SERVICE_H_COL = "_service_time_hours"
else:
    df[SERVICE_H_COL] = pd.to_numeric(df[SERVICE_H_COL], errors="coerce")

# Ensure cancellation boolean (provided)
if CANCEL_COL is None:
    if STATUS_COL is not None:
        s = df[STATUS_COL].astype(str).str.lower()
        df["_is_cancelled"] = s.str.contains("cancel|cancell|annul")
        CANCEL_COL = "_is_cancelled"
    else:
        df["_is_cancelled"] = False
        CANCEL_COL = "_is_cancelled"
else:
    v = df[CANCEL_COL]
    if v.dtype == bool:
        df["_is_cancelled"] = v
    else:
        df["_is_cancelled"] = v.astype(str).str.lower().isin(
            ["1", "true", "yes", "y", "cancelled", "canceled", "annule", "annulé", "annulee"]
        )
    CANCEL_COL = "_is_cancelled"


# ------------------------------------------------------------
# 2) Dropdown options (provided)
# ------------------------------------------------------------
borough_options = sorted(df[BOROUGH_COL].dropna().astype(str).unique().tolist())
request_options = sorted(df[REQUEST_COL].dropna().astype(str).unique().tolist())

default_borough = borough_options[:1] if borough_options else []
default_request = request_options[:3] if len(request_options) >= 3 else request_options


# ------------------------------------------------------------
# 3) Layout (provided — DO NOT CHANGE)
# ------------------------------------------------------------
app = Dash(__name__)

app.layout = html.Div(
    style={"fontFamily": "Arial", "maxWidth": "1100px", "margin": "0 auto", "padding": "16px"},
    children=[
        html.H2("Q8 — Mini Dashboard (Dash)"),

        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px"},
            children=[
                html.Div([
                    html.Label("Select borough(s)"),
                    dcc.Dropdown(
                        id="borough_dd",
                        options=[{"label": b, "value": b} for b in borough_options],
                        value=default_borough,
                        multi=True,
                    ),
                ]),
                html.Div([
                    html.Label("Select request type(s)"),
                    dcc.Dropdown(
                        id="request_dd",
                        options=[{"label": r, "value": r} for r in request_options],
                        value=default_request,
                        multi=True,
                    ),
                ]),
            ],
        ),

        html.Hr(),

        # KPIs (must be updated by callback)
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "repeat(3, 1fr)", "gap": "12px"},
            children=[
                html.Div(style={"border": "1px solid #ddd", "borderRadius": "10px", "padding": "12px"}, children=[
                    html.Div("Total tickets", style={"fontSize": "14px", "opacity": 0.8}),
                    html.Div(id="kpi_total", style={"fontSize": "28px", "fontWeight": "bold"}),
                ]),
                html.Div(style={"border": "1px solid #ddd", "borderRadius": "10px", "padding": "12px"}, children=[
                    html.Div("Cancellation rate", style={"fontSize": "14px", "opacity": 0.8}),
                    html.Div(id="kpi_cancel", style={"fontSize": "28px", "fontWeight": "bold"}),
                ]),
                html.Div(style={"border": "1px solid #ddd", "borderRadius": "10px", "padding": "12px"}, children=[
                    html.Div("Avg service time (hours)", style={"fontSize": "14px", "opacity": 0.8}),
                    html.Div(id="kpi_service", style={"fontSize": "28px", "fontWeight": "bold"}),
                ]),
            ],
        ),

        html.Hr(),

        dcc.Graph(id="main_graph"),
        html.Div(id="debug_note", style={"marginTop": "8px", "fontSize": "12px", "opacity": 0.75}),
    ],
)


# ------------------------------------------------------------
# 4) STUDENT WORK — Implement DATA -> FILTER -> KPIs + GRAPH
# ------------------------------------------------------------

def filter_df(df_in: pd.DataFrame, selected_boroughs, selected_requests) -> pd.DataFrame:
    """
    TODO (students):
    - If selected_boroughs is empty/None, keep ALL boroughs
    - If selected_requests is empty/None, keep ALL request types
    - Return the filtered dataframe

    Tip: use .isin([...]) on the correct columns: BOROUGH_COL and REQUEST_COL
    """
    # ✅ STARTER (students can keep and complete)
    dff = df_in.copy()

    # TODO: normalize selections to list of strings
    # TODO: apply filters using BOROUGH_COL and REQUEST_COL

    return dff


def compute_kpis(dff: pd.DataFrame) -> dict:
    """
    TODO (students):
    Compute at least TWO KPIs that update with the filters.
    Required outputs (already in layout): total tickets, cancellation rate, avg service time (hours).

    Return a dict like:
    {
        "total": int,
        "cancel_rate": float (0..1),
        "avg_service_h": float (hours, may be np.nan)
    }
    """
    # TODO: handle empty dff (avoid division by zero)
    # Hints:
    # - total = len(dff)
    # - cancel_rate = dff[CANCEL_COL].mean()  (works if boolean)
    # - avg_service_h = pd.to_numeric(dff[SERVICE_H_COL], errors="coerce").mean()

    return {
        "total": 0,
        "cancel_rate": 0.0,
        "avg_service_h": np.nan,
    }


def make_figure(dff: pd.DataFrame):
    """
    TODO (students):
    Create ONE figure that changes when filters change.

    Suggested chart (easy + clear for ops):
    - Bar chart: number of tickets by REQUEST_COL, colored by BOROUGH_COL
    - Optional: show only top N request types to keep readable
    """
    if len(dff) == 0:
        fig = px.bar(title="No data for the selected filters")
        fig.update_layout(height=520)
        return fig

    # TODO: build counts table with groupby + size + reset_index
    # TODO: make px.bar(...) using REQUEST_COL on x, tickets on y, BOROUGH_COL as color

    fig = px.bar(title="TODO: implement chart")
    fig.update_layout(height=520)
    return fig


@app.callback(
    Output("main_graph", "figure"),
    Output("kpi_total", "children"),
    Output("kpi_cancel", "children"),
    Output("kpi_service", "children"),
    Output("debug_note", "children"),
    Input("borough_dd", "value"),
    Input("request_dd", "value"),
)
def update_dashboard(selected_boroughs, selected_requests):
    """
    TODO (students):
    Connect everything:
    1) filter the dataframe using dropdown selections
    2) compute KPIs from filtered data
    3) build a figure from filtered data
    4) return (figure, KPI strings, debug text)
    """
    # 1) Filter
    dff = filter_df(df, selected_boroughs, selected_requests)

    # 2) KPIs
    kpis = compute_kpis(dff)

    # 3) Figure
    fig = make_figure(dff)

    # 4) Format outputs (students can adjust formatting)
    total_txt = f"{kpis['total']:,}"
    cancel_txt = f"{kpis['cancel_rate']*100:.1f}%"
    service_txt = "—" if np.isnan(kpis["avg_service_h"]) else f"{kpis['avg_service_h']:.1f}"

    debug = (
        f"Columns: borough='{BOROUGH_COL}', request_type='{REQUEST_COL}', "
        f"cancel='{CANCEL_COL}', service_time_hours='{SERVICE_H_COL}'. "
        f"Filtered rows: {len(dff)}"
    )

    return fig, total_txt, cancel_txt, service_txt, debug


if __name__ == "__main__":
    app.run_server(debug=True)
