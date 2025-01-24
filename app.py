# from flask import Flask, request, render_template, redirect, url_for, flash, session
# from datetime import datetime
# import os
# import pandas as pd
# import boto3
# from io import BytesIO
# from dotenv import load_dotenv

# # 環境変数を読み込み
# load_dotenv()

# app = Flask(__name__)
# app.secret_key = "supersecretkey"

# # 環境変数から AWS 設定を取得
# S3_BUCKET = os.environ.get("S3_BUCKET")
# S3_REGION = os.environ.get("S3_REGION")
# S3_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
# S3_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

# # boto3 クライアントの設定
# s3 = boto3.client(
#     "s3",
#     region_name=S3_REGION,
#     aws_access_key_id=S3_ACCESS_KEY,
#     aws_secret_access_key=S3_SECRET_KEY,
# )


# # 確認用データフレーム
# df = pd.DataFrame({"id": [1], "name": ["テスト"]})

# # S3に保存
# buffer = BytesIO()
# df.to_excel(buffer, index=False)
# buffer.seek(0)
# s3.put_object(Bucket=S3_BUCKET, Key="test.xlsx", Body=buffer.getvalue())
# print("S3に保存しました")

# # S3から読み込み
# obj = s3.get_object(Bucket=S3_BUCKET, Key="test.xlsx")
# df_loaded = pd.read_excel(BytesIO(obj["Body"].read()))
# print("S3から読み込み:", df_loaded)

# # Excel ファイル名
# EXCEL_FILE_KEY = "attendance_requests.xlsx"

# # Excel からデータを読み込む関数
# def read_requests():
#     try:
#         obj = s3.get_object(Bucket=S3_BUCKET, Key=EXCEL_FILE_KEY)
#         return pd.read_excel(BytesIO(obj["Body"].read()))
#     except s3.exceptions.NoSuchKey:
#         # 初回読み込み時にファイルがない場合の対応
#         return pd.DataFrame(columns=["id", "date", "reason", "employee", "confirmed", "confirmed_at"])
#     except Exception as e:
#         flash(f"データの読み込み中にエラーが発生しました: {e}")
#         return pd.DataFrame(columns=["id", "date", "reason", "employee", "confirmed", "confirmed_at"])

# # Excel にデータを保存する関数
# def save_requests(df):
#     try:
#         with BytesIO() as output:
#             df.to_excel(output, index=False)
#             output.seek(0)
#             s3.put_object(Bucket=S3_BUCKET, Key=EXCEL_FILE_KEY, Body=output.getvalue())
#     except Exception as e:
#         flash(f"データの保存中にエラーが発生しました: {e}")

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

#     df = read_requests()

#     # 重複確認
#     if not df[df["date"].eq(date) & df["employee"].eq(employee)].empty:
#         flash("同じ修正日で既に申請があります。")
#         return redirect(url_for("index"))

#     # 新しい申請を追加
#     new_id = df["id"].max() + 1 if not df.empty else 1
#     new_request = {
#         "id": new_id,
#         "date": date,
#         "reason": reason,
#         "employee": employee,
#         "confirmed": False,
#         "confirmed_at": None
#     }
#     df = pd.concat([df, pd.DataFrame([new_request])], ignore_index=True)
#     save_requests(df)

#     flash("申請が送信されました。")
#     return redirect(url_for("list_requests"))

# @app.route("/list")
# def list_requests():
#     if "user" not in session:
#         flash("ログインしてください。")
#         return redirect(url_for("login"))

#     df = read_requests()

#     requests = (
#         df.to_dict("records")
#         if session.get("is_admin", False)
#         else df[df["employee"].eq(session["user"])].to_dict("records")
#     )
#     return render_template("list.html", data=requests, user=session["user"], is_admin=session.get("is_admin", False))

# @app.route("/edit/<int:request_id>", methods=["GET", "POST"])
# def edit_request(request_id):
#     df = read_requests()
#     request_to_edit = df[df["id"] == request_id]

#     if request_to_edit.empty:
#         flash("該当の申請が見つかりません。")
#         return redirect(url_for("list_requests"))

#     if request.method == "POST":
#         df.loc[df["id"] == request_id, ["date", "reason", "confirmed", "confirmed_at"]] = [
#             request.form["date"],
#             request.form["reason"],
#             False,
#             None
#         ]
#         save_requests(df)
#         flash("申請が更新されました。")
#         return redirect(url_for("list_requests"))

#     return render_template("edit.html", record=request_to_edit.iloc[0])

# @app.route("/delete_request/<int:request_id>", methods=["POST"])
# def delete_request(request_id):
#     if "user" not in session or not session.get("is_admin", False):
#         flash("権限がありません。")
#         return redirect(url_for("login"))

#     df = read_requests()
#     if request_id in df["id"].values:
#         df = df[df["id"] != request_id]
#         save_requests(df)
#         flash("申請が削除されました。")
#     else:
#         flash("該当の申請が見つかりません。")

#     return redirect(url_for("list_requests"))

# @app.route("/confirm/<int:request_id>", methods=["POST"])
# def confirm_request(request_id):
#     if "user" not in session or not session.get("is_admin", False):
#         flash("権限がありません。")
#         return redirect(url_for("login"))

#     df = read_requests()
#     if request_id in df["id"].values:
#         df.loc[df["id"] == request_id, ["confirmed", "confirmed_at"]] = [True, datetime.now()]
#         save_requests(df)
#         flash("申請が確認済みになりました。")
#     else:
#         flash("該当の申請が見つかりません。")

#     return redirect(url_for("list_requests"))

# @app.route("/unconfirm/<int:request_id>", methods=["POST"])
# def unconfirm_request(request_id):
#     if "user" not in session or not session.get("is_admin", False):
#         flash("権限がありません。")
#         return redirect(url_for("login"))

#     df = read_requests()
#     if request_id in df["id"].values:
#         df.loc[df["id"] == request_id, ["confirmed", "confirmed_at"]] = [False, None]
#         save_requests(df)
#         flash("申請が未確認に戻されました。")
#     else:
#         flash("該当の申請が見つかりません。")

#     return redirect(url_for("list_requests"))

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port)













from flask import Flask, request, render_template, redirect, url_for, flash, session
from datetime import datetime
import os
import pandas as pd
import boto3
from io import BytesIO
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"

# 環境変数から AWS 設定を取得
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_REGION = os.environ.get("S3_REGION")
S3_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
S3_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

# boto3 クライアントの設定
s3 = boto3.client(
    "s3",
    region_name=S3_REGION,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
)

# Excel ファイル名
EXCEL_FILE_KEY = "attendance_requests.xlsx"

# Excel からデータを読み込む関数
def read_requests():
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=EXCEL_FILE_KEY)
        return pd.read_excel(BytesIO(obj["Body"].read()))
    except s3.exceptions.NoSuchKey:
        # 初回読み込み時にファイルがない場合の対応
        return pd.DataFrame(columns=["id", "date", "reason", "employee", "confirmed", "confirmed_at"])
    except Exception as e:
        flash(f"データの読み込み中にエラーが発生しました: {e}")
        return pd.DataFrame(columns=["id", "date", "reason", "employee", "confirmed", "confirmed_at"])

# Excel にデータを保存する関数
def save_requests(df):
    try:
        with BytesIO() as output:
            df.to_excel(output, index=False)
            output.seek(0)
            s3.put_object(Bucket=S3_BUCKET, Key=EXCEL_FILE_KEY, Body=output.getvalue())
    except Exception as e:
        flash(f"データの保存中にエラーが発生しました: {e}")

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

    df = read_requests()

    # 重複確認
    if not df[df["date"].eq(date) & df["employee"].eq(employee)].empty:
        flash("同じ修正日で既に申請があります。")
        return redirect(url_for("index"))

    # 新しい申請を追加
    new_id = df["id"].max() + 1 if not df.empty else 1
    new_request = {
        "id": new_id,
        "date": date,
        "reason": reason,
        "employee": employee,
        "confirmed": False,
        "confirmed_at": None
    }
    df = pd.concat([df, pd.DataFrame([new_request])], ignore_index=True)
    df = df.sort_values(by="date", ascending=False).reset_index(drop=True)  # 日付順で並べ替え
    save_requests(df)

    flash("申請が送信されました。")
    return redirect(url_for("list_requests"))

@app.route("/list")
def list_requests():
    if "user" not in session:
        flash("ログインしてください。")
        return redirect(url_for("login"))

    df = read_requests()

    # 日付フォーマットを追加
    df["formatted_confirmed_at"] = df["confirmed_at"].apply(
        lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) else "未確認"
    )

    requests = (
        df.to_dict("records")
        if session.get("is_admin", False)
        else df[df["employee"].eq(session["user"])].to_dict("records")
    )
    return render_template("list.html", data=requests, user=session["user"], is_admin=session.get("is_admin", False))

@app.route("/edit/<int:request_id>", methods=["GET", "POST"])
def edit_request(request_id):
    df = read_requests()
    request_to_edit = df[df["id"] == request_id]

    if request_to_edit.empty:
        flash("該当の申請が見つかりません。")
        return redirect(url_for("list_requests"))

    if request.method == "POST":
        df.loc[df["id"] == request_id, ["date", "reason", "confirmed", "confirmed_at"]] = [
            request.form["date"],
            request.form["reason"],
            False,
            None
        ]
        save_requests(df)
        flash("申請が更新されました。")
        return redirect(url_for("list_requests"))

    return render_template("edit.html", record=request_to_edit.iloc[0])

@app.route("/delete_request/<int:request_id>", methods=["POST"])
def delete_request(request_id):
    if "user" not in session:
        flash("ログインしてください。")
        return redirect(url_for("login"))

    df = read_requests()
    if request_id in df["id"].values:
        df = df[df["id"] != request_id]
        save_requests(df)
        flash("申請が削除されました。")
    else:
        flash("該当の申請が見つかりません。")

    return redirect(url_for("list_requests"))

@app.route("/confirm/<int:request_id>", methods=["POST"])
def confirm_request(request_id):
    if "user" not in session or not session.get("is_admin", False):
        flash("権限がありません。")
        return redirect(url_for("login"))

    df = read_requests()
    if request_id in df["id"].values:
        df.loc[df["id"] == request_id, ["confirmed", "confirmed_at"]] = [True, datetime.now()]
        save_requests(df)
        flash("申請が確認済みになりました。")
    else:
        flash("該当の申請が見つかりません。")

    return redirect(url_for("list_requests"))

@app.route("/unconfirm/<int:request_id>", methods=["POST"])
def unconfirm_request(request_id):
    if "user" not in session or not session.get("is_admin", False):
        flash("権限がありません。")
        return redirect(url_for("login"))

    df = read_requests()
    if request_id in df["id"].values:
        df.loc[df["id"] == request_id, ["confirmed", "confirmed_at"]] = [False, None]
        save_requests(df)
        flash("申請が未確認に戻されました。")
    else:
        flash("該当の申請が見つかりません。")

    return redirect(url_for("list_requests"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)