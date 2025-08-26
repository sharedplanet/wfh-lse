import json
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# ---------------------------
# Load pre-aggregated data
# ---------------------------
with open("aggregates.json") as f:
    aggregates = json.load(f)

# ---------------------------
# Questions mapping
# ---------------------------
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
    "Q25 – Reasons for non-adoption - multi-select": "25_",
}

# ---------------------------
# Disaggregation options
# ---------------------------
disagg_options = {
    "Years since business incorporated": "2_Response",
    "Sector": "3_Response",
    "Workforce size (Q7 buckets)": "7_Response_Bucket",
}

bucket_order = ["Micro (1–9)", "Small (10–49)", "Medium (50–249)", "Large (250+)"]

# ---------------------------
# Styles
# ---------------------------
dropdown_style = {
    "width": "100%",
    "maxWidth": "650px",
    "margin": "5px auto",
    "backgroundColor": "#ffffff",
    "border": "1px solid #d1d3e0",
    "borderRadius": "8px",
    "padding": "10px 12px",
    "fontSize": "14px",
    "color": "#1f2c56",
    "boxShadow": "0 2px 6px rgba(0,0,0,0.05)",
}

label_style = {
    "color": "#1f2c56",
    "fontWeight": "600",
    "fontSize": "15px",
    "marginBottom": "6px",
    "textAlign": "center",
    "display": "block",
}

header_style = {
    "color": "#1f2c56",
    "textAlign": "center",
    "fontWeight": "700",
    "marginBottom": "30px",
    "fontFamily": "Inter, Helvetica, Arial, sans-serif",
}

graph_container_style = {
    "marginTop": "30px",
    "padding": "20px",
    "borderRadius": "10px",
    "backgroundColor": "#ffffff",
    "boxShadow": "0 4px 12px rgba(0,0,0,0.05)",
}

body_style = {
    "fontFamily": "Inter, Helvetica, Arial, sans-serif",
    "backgroundColor": "#f8f9fc",
    "padding": "30px",
    "textAlign": "center"
}

# ---------------------------
# Build Dash app
# ---------------------------
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H2("Remote/Hybrid Work Survey Dashboard", style=header_style),

    # Q8 Radio filter
    html.Div([
        html.Label("Filter by Q8 Response:", style=label_style),
        dcc.RadioItems(
            id="q8_filter",
            options=[
                {"label": "Yes (currently or at some point in time)", "value": "Yes (currently or at some point in time)"},
                {"label": "No, never", "value": "No, never"},
            ],
            value="Yes (currently or at some point in time)",
            inline=True,
            style={"margin": "0 auto"}
        )
    ], style={"marginBottom": "20px"}),

    # Question selector
    html.Div([
        html.Label("Select question to analyze:", style=label_style),
        dcc.Dropdown(id="question_select", options=[], clearable=False, style=dropdown_style),
    ]),

    # Multi-choice selector
    html.Div([
        html.Label("Select option within multi-select question:", style=label_style),
        dcc.Dropdown(id="multi_choice_select", options=[], value=None, clearable=False, style=dropdown_style)
    ], id="multi_choice_container", style={"display": "none"}),

    # Disaggregation
    html.Div([
        html.Label("Disaggregate by:", style=label_style),
        dcc.Dropdown(
            id="disagg_select",
            options=[{"label": k, "value": v} for k, v in disagg_options.items()],
            value="7_Response_Bucket",
            clearable=False,
            style=dropdown_style,
        )
    ], style={"marginBottom": "20px"}),

    # Graph
    dcc.Graph(id="bar_chart", style={"marginTop": "30px"}),

], style=body_style)

# ---------------------------
# Callbacks
# ---------------------------
@app.callback(
    Output("question_select", "options"),
    Output("question_select", "value"),
    Input("q8_filter", "value"),
    Input("question_select", "value"),
)
def update_question_dropdown(q8_value, current_value):
    if q8_value == "No, never":
        opts = [{"label": "Q25 – Reasons for non-adoption - multi-select", "value": "25_"}]
        return opts, "25_"
    else:
        opts = [{"label": k, "value": v} for k, v in questions.items() if not k.startswith("Q25")]
        new_value = current_value if current_value in [o["value"] for o in opts] else opts[0]["value"]
        return opts, new_value


@app.callback(
    Output("multi_choice_container", "style"),
    Output("multi_choice_select", "options"),
    Output("multi_choice_select", "value"),
    Input("question_select", "value"),
)
def update_multi_choice_selector(question_col):
    if question_col and question_col.endswith("_"):
        # Extract all keys for this question
        all_keys = [k for k in aggregates.keys() if k.split('|')[1].startswith(question_col)]
        # Get unique second parts (choice names)
        unique_choices = sorted({k.split('|')[1] for k in all_keys})
        options = [{"label": c.replace(question_col, ""), "value": c} for c in unique_choices]
        default_val = options[0]["value"] if options else None
        return {"display": "block"}, options, default_val
    else:
        return {"display": "none"}, [], None


@app.callback(
    Output("bar_chart", "figure"),
    Input("q8_filter", "value"),
    Input("question_select", "value"),
    Input("disagg_select", "value"),
    Input("multi_choice_select", "value"),
)
def update_chart(q8_value, question_col, disagg_col, multi_choice):
    # Determine aggregate key
    if question_col.endswith("_") and multi_choice:
        key = f"{q8_value}|{multi_choice}|{disagg_col}"
    else:
        key = f"{q8_value}|{question_col}|{disagg_col}"

    if key not in aggregates:
        return px.bar(title="No data available for this selection.")

    data = pd.DataFrame(aggregates[key])

    if question_col.endswith("_") and multi_choice:
        fig = px.bar(
            data,
            x="Percent",
            y=disagg_col,
            orientation="h",
            text=data.apply(lambda r: f"{r['Percent']:.1f}% ({int(r['Count'])})", axis=1),
            title=f"{multi_choice.replace(question_col,'')} by {disagg_col}",
            labels={"Percent": "Percentage of respondents", disagg_col: disagg_col},
            category_orders={disagg_col: bucket_order} if disagg_col == "7_Response_Bucket" else None
        )
        # Fix x-axis to 0–100% for multi-select
        fig.update_xaxes(range=[0, 100], title_text="Percentage of respondents")
    else:
        fig = px.bar(
            data,
            x="Percent",
            y=disagg_col,
            color=question_col,
            orientation="h",
            barmode="stack",
            text=data.apply(lambda r: f"{r['Percent']:.1f}% ({int(r['Count'])})", axis=1),
            title=f"{question_col} by {disagg_col} (Q8={q8_value})",
            labels={"Percent": "Percentage of responses", disagg_col: disagg_col, question_col: question_col},
            category_orders={disagg_col: bucket_order} if disagg_col == "7_Response_Bucket" else None
        )

    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title=None, itemwidth=80),
        margin=dict(t=140, b=40, l=40, r=40),
        autosize=True,
        plot_bgcolor="#f8f9fc",
        paper_bgcolor="#f8f9fc",
    )
    fig.update_traces(textposition="inside", insidetextanchor="middle")

    return fig

# ---------------------------
# Run app
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True, port=8051)

