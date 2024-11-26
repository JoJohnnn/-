# from flask import Flask, request, render_template, redirect, url_for, flash, session
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime
# import os

# app = Flask(__name__)
# app.secret_key = "supersecretkey"

# # データベースの設定 (PostgreSQL or SQLite)
# DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///attendance_requests.db")
# if DATABASE_URL.startswith("postgres://"):
#     DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")  # SQLAlchemy用に修正
# app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# # モデル定義
# class AttendanceRequest(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.String(10), nullable=False)
#     reason = db.Column(db.String(255), nullable=False)
#     employee = db.Column(db.String(50), nullable=False)
#     confirmed = db.Column(db.Boolean, default=False)
#     confirmed_at = db.Column(db.DateTime, nullable=True)

# # 初回起動時にデータベースを作成
# with app.app_context():
#     db.create_all()

# USER_CREDENTIALS = {
#     "Q": "1234",
#     "ジョン": "1234", 
#     "ラン": "1234",
#     "サキ": "1234", 
#     "氷河": "1234",
#     "クリス": "1234", 
#     "アグ": "1234",
#     "admin": "admin"
# }

# ADMIN_USERS = ["admin"]

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]

#         if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
#             session["user"] = username
#             session["is_admin"] = username in ADMIN_USERS
#             flash(f"ログイン成功しました。こんにちは、{username}さん！")
#             return redirect(url_for("index"))
#         else:
#             flash("ユーザー名またはパスワードが間違っています。")
#             return redirect(url_for("login"))

#     return render_template("login.html")

# @app.route("/logout", methods=["POST"])
# def logout():
#     session.pop("user", None)
#     session.pop("is_admin", None)
#     flash("ログアウトしました。")
#     return redirect(url_for("login"))

# @app.route("/")
# def index():
#     if "user" not in session:
#         flash("ログインしてください。")
#         return redirect(url_for("login"))
    
#     users = USER_CREDENTIALS.keys() if session.get("is_admin", False) else None
#     return render_template("index.html", user=session["user"], is_admin=session.get("is_admin", False), users=users)

# @app.route("/submit", methods=["POST"])
# def submit():
#     if "user" not in session:
#         flash("ログインしてください。")
#         return redirect(url_for("login"))

#     date = request.form["date"]
#     reason = request.form["reason"]
#     employee = request.form["employee"] if session.get("is_admin", False) else session["user"]

#     # 重複確認
#     duplicate = AttendanceRequest.query.filter_by(employee=employee, date=date).first()
#     if duplicate:
#         flash("同じ修正日で既に申請があります。")
#         return redirect(url_for("index"))

#     # データベースに新規追加
#     new_request = AttendanceRequest(date=date, reason=reason, employee=employee)
#     db.session.add(new_request)
#     db.session.commit()

#     flash("申請が送信されました。")
#     return redirect(url_for("list_requests"))

# @app.route("/list")
# def list_requests():
#     if "user" not in session:
#         flash("ログインしてください。")
#         return redirect(url_for("login"))

#     requests = (
#         AttendanceRequest.query.all()
#         if session.get("is_admin", False)
#         else AttendanceRequest.query.filter_by(employee=session["user"]).all()
#     )
#     return render_template("list.html", data=requests, user=session["user"], is_admin=session.get("is_admin", False))

# @app.route("/edit/<int:request_id>", methods=["GET", "POST"])
# def edit_request(request_id):
#     request_to_edit = AttendanceRequest.query.get(request_id)
#     if not request_to_edit:
#         flash("該当の申請が見つかりません。")
#         return redirect(url_for("list_requests"))

#     if request.method == "POST":
#         # 更新処理
#         request_to_edit.date = request.form["date"]
#         request_to_edit.reason = request.form["reason"]

#         # 確認ステータスをリセット
#         if request_to_edit.confirmed:
#             request_to_edit.confirmed = False
#             request_to_edit.confirmed_at = None

#         db.session.commit()
#         flash("申請が更新され、確認ステータスは未確認に戻りました。")
#         return redirect(url_for("list_requests"))

#     return render_template("edit.html", record=request_to_edit)

# @app.route("/delete_request/<int:request_id>", methods=["POST"])
# def delete_request(request_id):
#     if "user" not in session or not session.get("is_admin", False):
#         flash("権限がありません。")
#         return redirect(url_for("login"))

#     request_to_delete = AttendanceRequest.query.get(request_id)
#     if request_to_delete:
#         db.session.delete(request_to_delete)
#         db.session.commit()
#         flash("申請が削除されました。")
#     else:
#         flash("該当の申請が見つかりません。")

#     return redirect(url_for("list_requests"))

# @app.route("/confirm/<int:request_id>", methods=["POST"])
# def confirm_request(request_id):
#     if "user" not in session or not session.get("is_admin", False):
#         flash("権限がありません。")
#         return redirect(url_for("login"))

#     request_to_confirm = AttendanceRequest.query.get(request_id)
#     if request_to_confirm:
#         request_to_confirm.confirmed = True
#         request_to_confirm.confirmed_at = datetime.now()
#         db.session.commit()
#         flash("申請が確認済みになりました。")
#     else:
#         flash("該当の申請が見つかりません。")

#     return redirect(url_for("list_requests"))

# @app.route("/unconfirm/<int:request_id>", methods=["POST"])
# def unconfirm_request(request_id):
#     if "user" not in session or not session.get("is_admin", False):
#         flash("権限がありません。")
#         return redirect(url_for("login"))

#     request_to_unconfirm = AttendanceRequest.query.get(request_id)
#     if request_to_unconfirm:
#         request_to_unconfirm.confirmed = False
#         request_to_unconfirm.confirmed_at = None
#         db.session.commit()
#         flash("申請が未確認に戻されました。")
#     else:
#         flash("該当の申請が見つかりません。")

#     return redirect(url_for("list_requests"))

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port)











from flask import Flask, request, render_template, redirect, url_for, flash, session
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Excelファイルの保存先
EXCEL_FILE = "attendance_requests.xlsx"

# 初期データの準備（必要に応じて空ファイルを作成）
if not os.path.exists(EXCEL_FILE):
    pd.DataFrame(columns=["id", "date", "reason", "employee", "confirmed", "confirmed_at"]).to_excel(EXCEL_FILE, index=False)

# ユーザー情報
USER_CREDENTIALS = {
    "Q": "1234",
    "ジョン": "1234",
    "ラン": "1234",
    "サキ": "1234",
    "氷河": "1234",
    "クリス": "1234",
    "アグ": "1234",
    "admin": "admin"
}

ADMIN_USERS = ["admin"]

# Excel操作用関数
def read_excel_data():
    try:
        return pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["id", "date", "reason", "employee", "confirmed", "confirmed_at"])

def save_to_excel(dataframe):
    dataframe.to_excel(EXCEL_FILE, index=False)

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
    users = USER_CREDENTIALS.keys() if session.get("is_admin", False) else None
    return render_template("index.html", user=session["user"], is_admin=session.get("is_admin", False), users=users)

@app.route("/submit", methods=["POST"])
def submit():
    if "user" not in session:
        flash("ログインしてください。")
        return redirect(url_for("login"))

    date = request.form["date"]
    reason = request.form["reason"]
    employee = request.form["employee"] if session.get("is_admin", False) else session["user"]

    df = read_excel_data()

    if not df[(df["employee"] == employee) & (df["date"] == date)].empty:
        flash("同じ修正日で既に申請があります。")
        return redirect(url_for("index"))

    new_entry = {
        "id": df["id"].max() + 1 if not df.empty else 1,
        "date": date,
        "reason": reason,
        "employee": employee,
        "confirmed": False,
        "confirmed_at": None,
    }
    df = df.append(new_entry, ignore_index=True)
    save_to_excel(df)

    flash("申請が送信されました。")
    return redirect(url_for("list_requests"))

@app.route("/list")
def list_requests():
    if "user" not in session:
        flash("ログインしてください。")
        return redirect(url_for("login"))

    df = read_excel_data()

    if not session.get("is_admin", False):
        df = df[df["employee"] == session["user"]]

    return render_template("list.html", data=df.to_dict(orient="records"), user=session["user"], is_admin=session.get("is_admin", False))

@app.route("/confirm/<int:request_id>", methods=["POST"])
def confirm_request(request_id):
    if "user" not in session or not session.get("is_admin", False):
        flash("権限がありません。")
        return redirect(url_for("login"))

    df = read_excel_data()

    if request_id in df["id"].values:
        df.loc[df["id"] == request_id, "confirmed"] = True
        df.loc[df["id"] == request_id, "confirmed_at"] = datetime.now()
        save_to_excel(df)
        flash("申請が確認済みになりました。")
    else:
        flash("該当の申請が見つかりません。")

    return redirect(url_for("list_requests"))

@app.route("/unconfirm/<int:request_id>", methods=["POST"])
def unconfirm_request(request_id):
    if "user" not in session or not session.get("is_admin", False):
        flash("権限がありません。")
        return redirect(url_for("login"))

    df = read_excel_data()

    if request_id in df["id"].values:
        df.loc[df["id"] == request_id, "confirmed"] = False
        df.loc[df["id"] == request_id, "confirmed_at"] = None
        save_to_excel(df)
        flash("申請が未確認に戻されました。")
    else:
        flash("該当の申請が見つかりません。")

    return redirect(url_for("list_requests"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)