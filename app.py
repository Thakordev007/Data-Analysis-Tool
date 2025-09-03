from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
import os, uuid

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route("/", methods=["GET", "POST"])
def index():
    tables, all_cols, selected_col = None, None, None
    bar_chart, line_chart, pie_chart = None, None, None
    rows, cols, missing, file_size = 0, 0, 0, 0

    if request.method == "POST":
        file = request.files["file"]
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            if file.filename.endswith(".csv"):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_table(filepath)

            
            rows, cols = df.shape
            missing = df.isnull().sum().sum()
            file_size = round(os.path.getsize(filepath) / 1024, 2)

           
            all_cols = df.columns.tolist()
            selected_col = request.form.get("column")

            
            tables = [df.head(50).to_html(classes="data", index=False)]

            if selected_col and selected_col in df.columns:
                col_data = df[selected_col].value_counts().head(10)

               
                bar_chart_filename = f"{uuid.uuid4()}.png"
                bar_chart_path = os.path.join(UPLOAD_FOLDER, bar_chart_filename)
                plt.figure(figsize=(6, 4))
                col_data.plot(kind="bar", color="skyblue", edgecolor="black")
                plt.title(f"Bar Chart of {selected_col}")
                plt.xlabel(selected_col)
                plt.ylabel("Count")
                plt.tight_layout()
                plt.savefig(bar_chart_path)
                plt.close()
                bar_chart = f"/static/uploads/{bar_chart_filename}"

              
                line_chart_filename = f"{uuid.uuid4()}.png"
                line_chart_path = os.path.join(UPLOAD_FOLDER, line_chart_filename)
                plt.figure(figsize=(6, 4))
                col_data.plot(kind="line", marker="o", color="orange")
                plt.title(f"Line Chart of {selected_col}")
                plt.xlabel("Categories")
                plt.ylabel("Count")
                plt.tight_layout()
                plt.savefig(line_chart_path)
                plt.close()
                line_chart = f"/static/uploads/{line_chart_filename}"

              
                pie_chart_filename = f"{uuid.uuid4()}.png"
                pie_chart_path = os.path.join(UPLOAD_FOLDER, pie_chart_filename)
                plt.figure(figsize=(5, 5))
                col_data.plot(kind="pie", autopct="%1.1f%%")
                plt.title(f"Pie Chart of {selected_col}")
                plt.ylabel("")
                plt.tight_layout()
                plt.savefig(pie_chart_path)
                plt.close()
                pie_chart = f"/static/uploads/{pie_chart_filename}"

    return render_template(
        "index.html",
        tables=tables,
        rows=rows,
        cols=cols,
        missing=missing,
        file_size=file_size,
        all_cols=all_cols,
        selected_col=selected_col,
        bar_chart=bar_chart,
        line_chart=line_chart,
        pie_chart=pie_chart
    )


@app.route("/reset")
def reset():
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
