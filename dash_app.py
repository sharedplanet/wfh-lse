import json
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

with open("aggregates.json") as f:
    aggregates = json.load(f)

questions = {
    "Q11 – Policy change since pandemic": "11_Response",
    "Q12 – Likelihood of return-to-office": "12_Response",
    "Q13 – Proportion working remotely": "13_Response",
    "Q14 – Frequency of WFH": "14_Response",
    "Q15 – Roles in organization - multi-select": "15_",
    "Q16 – Benefits of WFH - multi-select": "16_",
    "Q17 – Difficulties in Management - multi-select": "17_",
    "Q18 – Impact: Productivity": "18_Productivity",
    "Q18 – Impact: Innovation": "18_Innovation",
    "Q18 – Impact: Staff recruitment and retention": "18_Staff recruitment and retention",
    "Q18 – Impact: Staff wellbeing": "18_Staff wellbeing",
    "Q18 – Impact: Training and career development": "18_Training and career development",
    "Q18 – Impact: Team collaboration": "18_Team collaboration",
    "Q18 – Impact: Overall business growth": "18_Overall business growth",
    "Q19 – Idea development and collaboration": "19_Idea development and collaboration (e.g. brainstorming, informal knowledge sharing)",
    "Q19 – Speed and implementation of innovation": "19_Speed and implementation of innovation (e.g. introduction of new products or services)",
    "Q19 – Adoption of new technologies/tools": "19_Adoption of new technologies or tools",
    "Q19 – Access to external collaborators": "19_Access to external collaborators (e.g. partners, clients)",
    "Q19 – Access to new talent/skills": "19_Access to new talent or innovation-related skills",
    "Q19 – Other (please select/specify)": "19_Other (please select and specify below)",
    "Q19 – Other (please specify)": "19_Other (please specify)",
    "Q20 – Barriers to scaling - multi-select": "20_",
    "Q21 – Technologies of enablement - multi-select": "21_",
    "Q23 – Barriers to scaling - multi-select": "23_",
    "Q24 – Adoption of AI impact on remote work - multi-select": "24_",
}

disagg_options = {
    "Years since business incorporated": "2_Response",
    "Sector": "3_Response",
    "Workforce size (Q7 buckets)": "7_Response_Bucket",
}

bucket_order = ["Micro (1–9)", "Small (10–49)", "Medium (50–249)", "Large (250+)"]

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H2("Remote/Hybrid Work Survey Dashboard"),
    html.Div([
        html.Label("Filter by Q8 Response:"),
        dcc.Dropdown(
            id="q8_filter",
            options=[
                {"label": "No, never", "value": "No, never"},
                {"label": "Yes (currently or at some point in time)", "value": "Yes (currently or at some point in time)"},
            ],
            value="No, never",
            clearable=False,
        )
    ], style={"width": "300px"}),
    html.Div([
        html.Label("Select question to analyze:"),
        dcc.Dropdown(
            id="question_select",
            options=[{"label": k, "value": v} for k, v in questions.items()],
            value="11_Response",
            clearable=False,
        )
    ], style={"width": "600px", "marginTop": "20px"}),
    html.Div([
        html.Label("Disaggregate by:"),
        dcc.Dropdown(
            id="disagg_select",
            options=[{"label": k, "value": v} for k, v in disagg_options.items()],
            value="7_Response_Bucket",
            clearable=False,
        )
    ], style={"width": "400px", "marginTop": "20px"}),
    dcc.Graph(id="bar_chart", style={"marginTop": "30px"}),
])

@app.callback(
    Output("bar_chart", "figure"),
    Input("q8_filter", "value"),
    Input("question_select", "value"),
    Input("disagg_select", "value"),
)
def update_chart(q8_value, question_col, disagg_col):
    key = f"{q8_value}|{question_col}|{disagg_col}"
    if key not in aggregates:
        return px.bar(title="No data available for this selection.")
    data = pd.DataFrame(aggregates[key])
    if question_col.endswith("_"):
        fig = px.bar(
            data,
            x="Percent",
            y=disagg_col,
            color="Choice",
            orientation="h",
            barmode="stack",
            text=data["Percent"].apply(lambda p: f"{p:.1f}%" if p >= 5 else ""),
            title=f"{question_col} by {disagg_col} (Q8={q8_value})",
            labels={"Percent": "Percentage of responses", disagg_col: disagg_col, "Choice": "Choice"},
            category_orders={disagg_col: bucket_order} if disagg_col == "7_Response_Bucket" else None,
        )
    else:
        fig = px.bar(
            data,
            x="Percent",
            y=disagg_col,
            color=question_col,
            orientation="h",
            barmode="stack",
            text=data["Percent"].apply(lambda p: f"{p:.1f}%" if p >= 5 else ""),
            title=f"{question_col} by {disagg_col} (Q8={q8_value})",
            labels={"Percent": "Percentage of responses", disagg_col: disagg_col, question_col: question_col},
            category_orders={disagg_col: bucket_order} if disagg_col == "7_Response_Bucket" else None,
        )
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            title=None,
            itemwidth=80,
            font=dict(size=10),
            traceorder="normal",
        ),
        margin=dict(t=100, b=40, l=40, r=40),
        autosize=True,
    )
    return fig

if __name__ == "__main__":
    app.run(debug=True)
