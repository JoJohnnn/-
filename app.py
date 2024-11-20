from flask import Flask, request, render_template, redirect, url_for, flash, session
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "attendance_requests.xlsx")

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["ID", "Date", "Reason", "Employee", "Confirmed", "ConfirmedAt"])
    df.to_excel(DATA_FILE, index=False)

def generate_id():
    df = pd.read_excel(DATA_FILE)
    if df.empty:
        return 1
    return int(df["ID"].max() + 1)

USER_CREDENTIALS = {
    "Q": "1234",
    "ジョン": "1234", 
    "ラン": "1234",
    "サキ": "1234", 
    "氷河": "1234",
    "クリス": "1234", 
    "アグ": "1234",
    "admin": "admin"  # 管理者アカウントを追加
}

ADMIN_USERS = ["admin"]

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            session["user"] = username
            session["is_admin"] = username in ADMIN_USERS
            flash(f"ログイン成功しました。こんにちは、{username}さん！")
            return redirect(url_for("index"))
        else:
            flash("ユーザー名またはパスワードが間違っています。")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    session.pop("is_admin", None)
    flash("ログアウトしました。")
    return redirect(url_for("login"))

@app.route("/")
def index():
    if "user" not in session:
        flash("ログインしてください。")
        return redirect(url_for("login"))
    
    users = list(USER_CREDENTIALS.keys()) if session.get("is_admin", False) else []
    return render_template("index.html", user=session["user"], users=users, is_admin=session.get("is_admin", False))

@app.route("/submit", methods=["POST"])
def submit():
    if "user" not in session:
        flash("ログインしてください。")
        return redirect(url_for("login"))

    date = request.form["date"]
    reason = request.form["reason"]
    
    if session.get("is_admin", False):
        employee = request.form.get("employee", session["user"])
        employee_display = f"{employee}admin"
    else:
        employee = session["user"]
        employee_display = employee

    df = pd.read_excel(DATA_FILE)

    duplicate = df[(df["Employee"] == employee) & (df["Date"] == date)]
    if not duplicate.empty:
        flash("同じ修正日で既に申請があります。")
        return redirect(url_for("index"))

    request_id = generate_id()
    new_data = {
        "ID": request_id, 
        "Date": date, 
        "Reason": reason, 
        "Employee": employee,
        "EmployeeDisplay": employee_display,
        "Confirmed": False, 
        "ConfirmedAt": None
    }
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_excel(DATA_FILE, index=False)

    return redirect(url_for("list_requests"))

@app.route("/list")
def list_requests():
    if "user" not in session:
        flash("ログインしてください。")
        return redirect(url_for("login"))

    try:
        df = pd.read_excel(DATA_FILE)
    except Exception:
        df = pd.DataFrame(columns=["ID", "Date", "Reason", "Employee", "EmployeeDisplay", "Confirmed", "ConfirmedAt"])

    if df.empty:
        data = []
    else:
        df = df[df["ID"].notnull()]
        data = df.to_dict(orient="records")

    return render_template("list.html", 
                           data=data, 
                           user=session["user"], 
                           is_admin=session.get("is_admin", False))

@app.route("/edit/<int:request_id>")
def edit_request(request_id):
    if "user" not in session:
        flash("ログインしてください。")
        return redirect(url_for("login"))

    df = pd.read_excel(DATA_FILE)
    record = df[df["ID"] == request_id]
    
    if record.empty:
        flash("該当の申請が見つかりません。")
        return redirect(url_for("list_requests"))

    record = record.to_dict(orient="records")[0]

    if record["Employee"] != session["user"] and not session.get("is_admin", False):
        return redirect(url_for("list_requests"))

    return render_template("edit.html", 
                           record=record, 
                           user=session["user"], 
                           is_admin=session.get("is_admin", False))

@app.route("/update/<int:request_id>", methods=["POST"])
def update_request(request_id):
    if "user" not in session:
        flash("ログインしてください。")
        return redirect(url_for("login"))

    date = request.form["date"]
    reason = request.form["reason"]
    
    if session.get("is_admin", False):
        employee = request.form.get("employee", session["user"])
        employee_display = f"{employee}admin"
    else:
        employee = session["user"]
        employee_display = employee

    df = pd.read_excel(DATA_FILE)

    duplicate = df[(df["Employee"] == employee) & (df["Date"] == date) & (df["ID"] != request_id)]
    if not duplicate.empty:
        flash("同じ修正日で既に申請があります。")
        return redirect(url_for("edit_request", request_id=request_id))

    df.loc[df["ID"] == request_id, ["Date", "Reason", "Employee", "EmployeeDisplay", "Confirmed", "ConfirmedAt"]] = [date, reason, employee, employee_display, False, None]
    df.to_excel(DATA_FILE, index=False)

    flash("申請が正常に更新されました。再度確認してください。")
    return redirect(url_for("list_requests"))

@app.route("/delete/<int:request_id>", methods=["POST"])
def delete_request(request_id):
    if "user" not in session:
        flash("ログインしてください。")
        return redirect(url_for("login"))

    df = pd.read_excel(DATA_FILE)
    record = df[df["ID"] == request_id].to_dict(orient="records")[0]
    
    if record["Employee"] != session["user"] and not session.get("is_admin", False):
        return redirect(url_for("list_requests"))
    
    df = df[df["ID"] != request_id]
    df.to_excel(DATA_FILE, index=False)

    flash("申請が正常に削除されました。")
    return redirect(url_for("list_requests"))

@app.route("/confirm/<int:request_id>", methods=["POST"])
def confirm_request(request_id):
    if "user" not in session or not session.get("is_admin", False):
        flash("権限がありません。")
        return redirect(url_for("login"))

    df = pd.read_excel(DATA_FILE)
    current_time = datetime.now().strftime("%Y/%m/%d %H:%M")
    df.loc[df["ID"] == request_id, ["Confirmed", "ConfirmedAt"]] = [True, current_time]
    df.to_excel(DATA_FILE, index=False)

    flash("申請が確認済みになりました。")
    return redirect(url_for("list_requests"))

@app.route("/unconfirm/<int:request_id>", methods=["POST"])
def unconfirm_request(request_id):
    if "user" not in session or not session.get("is_admin", False):
        flash("権限がありません。")
        return redirect(url_for("login"))

    df = pd.read_excel(DATA_FILE)
    df.loc[df["ID"] == request_id, ["Confirmed", "ConfirmedAt"]] = [False, None]
    df.to_excel(DATA_FILE, index=False)

    flash("申請が未確認に戻されました。")
    return redirect(url_for("list_requests"))

if __name__ == "__main__":
    app.run(debug=True)



