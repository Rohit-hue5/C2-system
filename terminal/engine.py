# terminal/engine.py

import subprocess
import os
import pty
import select
import threading
import time
import signal
from typing import Dict, Optional

from core.state import STATE
from payloads.manager import PayloadManager
from network.scanner import scan_network

payload_manager = PayloadManager()

class MSFTerminal:
    """Persistent MSFconsole process manager"""

    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.ptys: Dict[str, int] = {}
        self.buffers: Dict[str, str] = {}

        # FIX: define path properly (no config needed for now)
        self.msf_path = "/usr/bin/msfconsole"        
    def start_msf(self, session_id: str) -> bool:
        """Spawn MSFconsole with persistent session"""
        try:
            if session_id in self.processes:
                return True  # Already running
                
            # Create PTY for interactive MSFconsole
            master_fd, slave_fd = pty.openpty()
            
            # MSFconsole with database + non-interactive startup
            cmd = [
                self.msf_path, "-q",  # Quiet mode
                "-x", "db_connect msf:msf@127.0.0.1/msf",  # Auto-connect DB
                "--color=false"
            ]
            
            proc = subprocess.Popen(
                cmd,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid,
                cwd=os.getcwd()
            )
            
            self.processes[session_id] = proc
            self.ptys[session_id] = master_fd
            self.buffers[session_id] = ""
            
            # Start output reader thread
            threading.Thread(target=self._read_output, args=(session_id,), daemon=True).start()
            return True
            
        except Exception as e:
            print(f"MSF spawn error: {e}")
            return False
    
    def _read_output(self, session_id: str):
        """Read MSFconsole output continuously"""
        fd = self.ptys[session_id]
        while fd in select.select([fd], [], [], 0)[0]:
            try:
                data = os.read(fd, 1024).decode('utf-8', errors='ignore')
                if data:
                    self.buffers[session_id] += data
            except:
                break
    
    def write_msf(self, session_id: str, command: str) -> str:
        """Send command to MSFconsole"""
        if session_id not in self.processes:
            return "[ERROR] MSF session not started. Use: msf start"
        
        try:
            os.write(self.ptys[session_id], (command + '\n').encode())
            time.sleep(0.1)  # Let MSF process
            
            output = self.buffers[session_id]
            self.buffers[session_id] = ""  # Clear after read
            return output or "[No output]"
            
        except Exception as e:
            return f"[MSF Error] {e}"
    
    def list_msf(self) -> str:
        """List available exploits/payloads"""
        if not self.processes:
            return "msf> search -h\nNo MSF sessions active"
        return "msf> " + " | ".join(self.processes.keys())
    
    def stop_msf(self, session_id: str) -> str:
        """Kill MSF session"""
        if session_id in self.processes:
            proc = self.processes[session_id]
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait()
            self.processes.pop(session_id, None)
            self.ptys.pop(session_id, None)
            return f"[+] MSF session {session_id} terminated"
        return "[ERROR] No such session"

# Global MSF manager
msf_terminal = MSFTerminal()

class TerminalEngine:
    def __init__(self):
        self.current_session = None
        self.cwd = os.getcwd()
        self.current_msf_session = None  # Track active MSF

    # ─────────────────────────────
    # MAIN ENTRY (MSF-ENHANCED)
    # ─────────────────────────────
    def execute(self, command: str) -> str:
        try:
            command = command.strip()
            if not command:
                return ""

            parts = command.split(maxsplit=1)
            cmd = parts[0]
            args = parts[1] if len(parts) > 1 else ""

            # ───────── MSF CONSOLE ─────────
            if cmd == "msf":
                return self.handle_msf(args)
            
            # ───────── ORIGINAL COMMANDS ─────────
            if cmd == "help":
                return self.help()
            elif cmd == "clear":
                return "__CLEAR__"
            elif cmd == "sessions":
                return self.sessions()
            elif cmd == "use":
                return self.use(args.split())
            elif cmd == "agents":
                return self.list_agents()
            elif cmd == "payload":
                return self.payload(args.split())
            elif cmd == "scan":
                return self.scan(args.split())
            elif cmd == "cd":
                return self.change_directory(args.split())
            elif cmd == "pwd":
                return self.cwd

            # ───────── REAL SHELL ─────────
            return self.exec_system(command)

        except Exception as e:
            return f"[ERROR] {str(e)}"

    # ─────────────────────────────
    # MSF HANDLER (NEW)
    # ─────────────────────────────
    def handle_msf(self, args: str) -> str:
        """Handle all msf* commands"""
        parts = args.split(maxsplit=1)
        subcmd = parts[0]
        subargs = parts[1] if len(parts) > 1 else ""
        
        if subcmd == "start":
            session_id = subargs or "default"
            if msf_terminal.start_msf(session_id):
                self.current_msf_session = session_id
                return f"[+] MSFconsole started: {session_id}\nmsf6 > "
            return "[ERROR] Failed to start MSFconsole"
        
        elif subcmd == "stop":
            session_id = subargs or self.current_msf_session or "default"
            return msf_terminal.stop_msf(session_id)
        
        elif subcmd == "list":
            return msf_terminal.list_msf()
        
        elif subcmd == "sessions":
            # Execute in current MSF session
            session_id = self.current_msf_session or "default"
            return msf_terminal.write_msf(session_id, args)
        
        else:
            # Direct MSF command
            if not self.current_msf_session:
                return "[ERROR] No active MSF session. Use: msf start"
            return msf_terminal.write_msf(self.current_msf_session, args)

    # ─────────────────────────────
    # MSFVENOM (QUICK ACCESS)
    # ─────────────────────────────
    def msfvenom(self, args: str) -> str:
        """One-shot msfvenom generation"""
        try:
            cmd = f"msfvenom {' '.join(args.split())} -o /tmp/payload_{int(time.time())}.exe"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            return result.stdout + result.stderr
        except Exception as e:
            return f"[msfvenom error] {e}"

    # ─────────────────────────────
    # ORIGINAL COMMANDS (UNCHANGED)
    # ─────────────────────────────
    def help(self):
        return """
Core:
  help, clear, sessions, use <id>

MSF Console ⚡ (NEW):
  msf start [name]     # Start MSFconsole
  msf stop [name]      # Stop MSF session  
  msf list             # List sessions
  msf <command>        # Send to active MSF (use, search, exploit, etc)

Agents: agents
Payload: payload <generate|list>
Network: scan <target>
Shell: cd, pwd, ls...

PRO TIP: msf start && use exploit/windows/smb/ms17_010_eternalblue
        """

    def sessions(self):
        agents = STATE.get_agents()
        if not agents:
            return "No active sessions."
        return "\n".join([f"{a['id']} | {a.get('status')}" for a in agents])

    def use(self, args):
        if not args:
            return "Usage: use <session_id>"
        self.current_session = args[0]
        return f"[+] Using session {args[0]}"

    def list_agents(self):
        agents = STATE.get_agents()
        if not agents:
            return "No agents connected"
        return "\n".join([f"{a['id']} | {a.get('status')}" for a in agents])

    def change_directory(self, args):
        if not args:
            return self.cwd
        try:
            new_path = os.path.join(self.cwd, args[0])
            os.chdir(new_path)
            self.cwd = os.getcwd()
            return self.cwd
        except Exception as e:
            return f"[cd error] {str(e)}"

    def exec_system(self, command):
        try:
            result = subprocess.run(
                command, shell=True, cwd=self.cwd,
                capture_output=True, text=True
            )
            output = result.stdout + result.stderr
            return output.strip()
        except Exception as e:
            return f"[exec error] {str(e)}"

    def payload(self, args):
        if not args:
            return "Usage: payload <generate|list>"
        if args[0] == "generate":
            return str(payload_manager.generate())
        elif args[0] == "list":
            return str(payload_manager.output_dir)
        return "Invalid payload command"

    def scan(self, args):
        if not args:
            return "Usage: scan <target>"
        return str(scan_network(args[0]))
