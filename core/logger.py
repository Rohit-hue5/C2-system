# core/logger.py

import logging
import os
import time
import config

# ─────────────────────────────
# 🔥 GLOBAL SOCKET
# ─────────────────────────────
socketio = None

def attach_socket(io):
    global socketio
    socketio = io


# ─────────────────────────────
# 🔥 CUSTOM HANDLER (KEY FIX)
# ─────────────────────────────
class SocketIOHandler(logging.Handler):
    def emit(self, record):
        try:
            log_entry = self.format(record)

            if socketio:
                socketio.emit("log", {
                    "time": time.strftime("%H:%M:%S"),
                    "message": log_entry
                })
        except Exception:
            pass


# ─────────────────────────────
# 🔥 LOGGER FACTORY
# ─────────────────────────────
def get_logger(name="c2lab"):
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    )

    # 📁 Ensure log dir exists
    os.makedirs(config.LOG_DIR, exist_ok=True)

    # 🔥 FILE HANDLER
    file_handler = logging.FileHandler(os.path.join(config.LOG_DIR, "server.log"))
    file_handler.setFormatter(formatter)

    # 🔥 CONSOLE HANDLER
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # 🔥 SOCKET HANDLER (MAIN FIX)
    socket_handler = SocketIOHandler()
    socket_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.addHandler(socket_handler)

    return logger


# ─────────────────────────────
# 🔥 OPTIONAL SIMPLE LOG FUNCTION
# ─────────────────────────────
def log(message, level="info"):
    logger = get_logger()

    if level == "error":
        logger.error(message)
    elif level == "warning":
        logger.warning(message)
    else:
        logger.info(message)
