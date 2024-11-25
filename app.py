from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# SQLiteデータベースの設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance_requests.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# モデル定義
class AttendanceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    employee = db.Column(db.String(50), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    confirmed_at = db.Column(db.DateTime, nullable=True)

# 初回起動時にデータベースを作成
with app.app_context():
    db.create_all()

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
    
    return render_template("index.html", user=session["user"], is_admin=session.get("is_admin", False))

@app.route("/submit", methods=["POST"])
def submit():
    if "user" not in session:
        flash("ログインしてください。")
        return redirect(url_for("login"))

    date = request.form["date"]
    reason = request.form["reason"]
    employee = session["user"]

    # 重複確認
    duplicate = AttendanceRequest.query.filter_by(employee=employee, date=date).first()
    if duplicate:
        flash("同じ修正日で既に申請があります。")
        return redirect(url_for("index"))

    # データベースに新規追加
    new_request = AttendanceRequest(date=date, reason=reason, employee=employee)
    db.session.add(new_request)
    db.session.commit()

    flash("申請が送信されました。")
    return redirect(url_for("list_requests"))

@app.route("/list")
def list_requests():
    if "user" not in session:
        flash("ログインしてください。")
        return redirect(url_for("login"))

    # データを取得
    if session.get("is_admin", False):
        requests = AttendanceRequest.query.all()
    else:
        requests = AttendanceRequest.query.filter_by(employee=session["user"]).all()

    return render_template("list.html", data=requests, user=session["user"], is_admin=session.get("is_admin", False))

@app.route("/edit/<int:request_id>", methods=["GET", "POST"])
def edit_request(request_id):
    request_to_edit = AttendanceRequest.query.get(request_id)
    if not request_to_edit:
        flash("該当の申請が見つかりません。")
        return redirect(url_for("list_requests"))

    if request.method == "POST":
        request_to_edit.date = request.form["date"]
        request_to_edit.reason = request.form["reason"]
        db.session.commit()
        flash("申請が更新されました。")
        return redirect(url_for("list_requests"))

    return render_template("edit.html", record=request_to_edit)

@app.route("/confirm/<int:request_id>", methods=["POST"])
def confirm_request(request_id):
    if "user" not in session or not session.get("is_admin", False):
        flash("権限がありません。")
        return redirect(url_for("login"))

    request_to_confirm = AttendanceRequest.query.get(request_id)
    if request_to_confirm:
        request_to_confirm.confirmed = True
        request_to_confirm.confirmed_at = datetime.now()
        db.session.commit()
        flash("申請が確認済みになりました。")
    else:
        flash("該当の申請が見つかりません。")

    return redirect(url_for("list_requests"))

@app.route("/unconfirm/<int:request_id>", methods=["POST"])
def unconfirm_request(request_id):
    if "user" not in session or not session.get("is_admin", False):
        flash("権限がありません。")
        return redirect(url_for("login"))

    request_to_unconfirm = AttendanceRequest.query.get(request_id)
    if request_to_unconfirm:
        request_to_unconfirm.confirmed = False
        request_to_unconfirm.confirmed_at = None
        db.session.commit()
        flash("申請が未確認に戻されました。")
    else:
        flash("該当の申請が見つかりません。")

    return redirect(url_for("list_requests"))

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)