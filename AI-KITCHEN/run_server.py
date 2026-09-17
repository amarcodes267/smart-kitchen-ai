import sys
import os
import traceback
import logging

log_file = os.path.join(os.path.dirname(__file__), "server.log")
f_log = open(log_file, "a", buffering=1, encoding="utf-8")
log_file = os.path.join(os.path.dirname(__file__), "server_activity.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

if sys.stdout is None or not hasattr(sys.stdout, "write"):
    sys.stdout = f_log
if sys.stderr is None or not hasattr(sys.stderr, "write"):
    sys.stderr = f_log
logging.info("Starting AI Kitchen Server...")

try:
    from app import app
    print("Starting AI Kitchen Server on port 5000...", file=f_log)
    logging.info("Flask app imported successfully. Starting on 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False, threaded=True)
except Exception as e:
    logging.exception(f"Server crashed: {e}")
    err_file = os.path.join(os.path.dirname(__file__), "run_server_error.log")
    with open(err_file, "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
finally:
    logging.info("Server execution finished.")
