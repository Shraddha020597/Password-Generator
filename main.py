from flask import Flask, render_template, request
import random, string
import datetime
import json
import os

app = Flask(__name__)

log_file = "usage_log.json"


if not os.path.exists(log_file):
    with open(log_file, "w") as f:
        json.dump({"total_users": 0, "last_used": "", "users": [], "passwords": []}, f)

@app.route("/", methods=["GET", "POST"])
def index():
    password = ""
    if request.method == "POST":
        length = int(request.form.get("length", 12))
        include_upper = request.form.get("uppercase")
        include_lower = request.form.get("lowercase")
        include_digits = request.form.get("digits")
        include_symbols = request.form.get("symbols")
        username = request.form.get("username") or "Anonymous"

        chars = ""
        if include_upper:
            chars += string.ascii_uppercase
        if include_lower:
            chars += string.ascii_lowercase
        if include_digits:
            chars += string.digits
        if include_symbols:
            chars += string.punctuation

        if chars:
            password = ''.join(random.choice(chars) for _ in range(length))
            update_log(username, password)

    return render_template("index.html", password=password, log=read_log())

def update_log(username, password):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(log_file, "r+") as f:
            data = json.load(f)
            if username not in data["users"]:
                data["users"].append(username)
            data["total_users"] = len(data["users"])
            data["last_used"] = now
            if "passwords" not in data:
                data["passwords"] = []
            data["passwords"].append({"username": username, "password": password, "timestamp": now})
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
    except (json.JSONDecodeError, FileNotFoundError):
        with open(log_file, "w") as f:
         
            data = {"total_users": 1, "last_used": now, "users": [username], "passwords": [{"username": username, "password": password, "timestamp": now}]}
            json.dump(data, f, indent=2)

def read_log():
    try:
        with open(log_file) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        
        return {"total_users": 0, "last_used": "", "users": [], "passwords": []}

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
