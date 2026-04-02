import socket
import threading
from core.logger import log
from sockets.agent_handler import start_agent_listener


class Listener:
    def __init__(self, host="0.0.0.0", port=5001, socketio=None):
        self.host = host
        self.port = port
        self.socketio = socketio

        self.server = None
        self.running = False

        self.connections = {}  # agent_id → socket

    # ─────────────────────────────
    # ▶ START LISTENER
    # ─────────────────────────────
    def start(self):
        if self.running:
            log("[LISTENER] Already running")
            return

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server.bind((self.host, self.port))
        self.server.listen(100)

        self.running = True

        log(f"[LISTENER] Started on {self.host}:{self.port}")

        threading.Thread(target=self.accept_loop, daemon=True).start()

    # ─────────────────────────────
    # 📡 ACCEPT LOOP
    # ─────────────────────────────
    def accept_loop(self):
        while self.running:
            try:
                client_sock, addr = self.server.accept()

                log(f"[LISTENER] Connection from {addr}")

                # 🔥 RECEIVE REAL AGENT ID
                try:
                    client_sock.settimeout(5)
                    raw = client_sock.recv(1024)

                    if not raw:
                        log("[LISTENER] Empty agent ID, closing")
                        client_sock.close()
                        continue

                    agent_id = raw.decode(errors="ignore").strip()

                    if not agent_id:
                        agent_id = f"{addr[0]}:{addr[1]}"

                except Exception:
                    agent_id = f"{addr[0]}:{addr[1]}"

                client_sock.settimeout(None)

                log(f"[AGENT] Registered ID: {agent_id}")

                # store connection
                self.connections[agent_id] = client_sock

                # 🔥 START HANDLER
                start_agent_listener(agent_id, client_sock, self.socketio)

                # 🔥 OPTIONAL: notify UI
                if self.socketio:
                    self.socketio.emit("agent_connected", {
                        "agent_id": agent_id,
                        "ip": addr[0],
                        "port": addr[1]
                    })

            except Exception as e:
                log(f"[LISTENER ERROR] {e}")

    # ─────────────────────────────
    # ⏹ STOP LISTENER
    # ─────────────────────────────
    def stop(self):
        self.running = False

        # close all agent sockets
        for agent_id, sock in list(self.connections.items()):
            try:
                sock.close()
            except:
                pass

        self.connections.clear()

        if self.server:
            try:
                self.server.close()
            except:
                pass

        log("[LISTENER] Stopped")

    # ─────────────────────────────
    # 📤 SEND COMMAND TO AGENT
    # ─────────────────────────────
    def send_to_agent(self, agent_id, command):
        sock = self.connections.get(agent_id)

        if not sock:
            log(f"[ERROR] Agent not found: {agent_id}")
            return False

        try:
            sock.sendall((command + "\n").encode())
            return True
        except Exception as e:
            log(f"[SEND ERROR] {agent_id}: {e}")
            return False
