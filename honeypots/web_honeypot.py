import os
import sys
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
)
sys.path.append(".")
from helpers.logger import create_logging_filehandler

base_dir = os.getcwd()
http_audits_log_filepath = os.path.join(base_dir, "log_files", "http_audits.log")

funnel_logger = create_logging_filehandler(
    logger_name="FunnelLogger",
    log_filepath=http_audits_log_filepath,
    log_format="%(asctime)s %(message)s"
)

def web_honeypot(input_username: str="admin", input_password: str="password"):
    app = Flask(__name__, template_folder="../templates")

    @app.route("/")

    def index():
        return render_template("wp-admin.html")
    
    @app.route("/wp-admin-login", methods=["POST"])
    
    def login():
        username = request.form["username"]
        password = request.form["password"]

        ip_address = request.remote_addr

        funnel_logger.info(f"Client with IP Address: {ip_address}, entered\n Username: {username}, Password: {password}")

        if username == input_username and password == input_password:
            return "Please go to https://r.mtdv.me/gYVb1JYxGw"
        else:
            return "Invalid username or password. Please try again."

    return app


def run_web_honeypot(port: str=4000, input_username: str="admin", input_password: str="password"):
    run_web_honeypot_app = web_honeypot(input_username, input_password)
    run_web_honeypot_app.run(debug=True, port=port, host="0.0.0.0")

    return run_web_honeypot_app
