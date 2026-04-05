import json
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def _series_for_charts(df, col_name):
    """Build a value-count style series for charts (numeric bins vs categorical)."""
    s = df[col_name].dropna()
    if s.empty:
        return None
    if pd.api.types.is_numeric_dtype(s):
        nuniq = s.nunique()
        if nuniq > 15:
            bins = min(10, max(3, nuniq // 5))
            binned = pd.cut(s, bins=bins, duplicates="drop")
            out = binned.value_counts().sort_index()
            out.index = out.index.astype(str)
            return out.head(10)
        vc = s.value_counts().head(10)
        vc.index = vc.index.map(lambda x: f"{x:g}" if isinstance(x, (int, float)) else str(x))
        return vc
    vc = s.astype(str).value_counts().head(10)
    return vc


def _chart_payload_for_column(df, col_name):
    ser = _series_for_charts(df, col_name)
    if ser is None or ser.empty:
        return {"labels": [], "counts": []}
    return {
        "labels": [str(i) for i in ser.index.tolist()],
        "counts": [int(x) for x in ser.tolist()],
    }


@app.route("/", methods=["GET", "POST"])
def index():
    preview_records = []
    chart_data_full = {}
    all_cols = None
    selected_col = None
    rows, cols, missing, file_size = 0, 0, 0, 0

    if request.method == "POST":
        file = request.files["file"]
        if file and file.filename:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            if file.filename.endswith(".csv"):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_table(filepath)

            rows, cols = df.shape
            missing = int(df.isnull().sum().sum())
            file_size = round(os.path.getsize(filepath) / 1024, 2)

            all_cols = df.columns.tolist()
            posted = request.form.get("column")
            if posted and posted in df.columns:
                selected_col = posted
            elif all_cols:
                selected_col = all_cols[0]

            preview_records = json.loads(df.head(100).to_json(orient="records", date_format="iso"))
            chart_data_full = {c: _chart_payload_for_column(df, c) for c in df.columns}

    return render_template(
        "index.html",
        preview_records=preview_records,
        all_cols=all_cols,
        selected_col=selected_col,
        chart_data_full=chart_data_full,
        rows=rows,
        cols=cols,
        missing=missing,
        file_size=file_size,
    )


@app.route("/reset")
def reset():
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
