from mitmproxy import http

real_chains = {}

def response(flow: http.HTTPFlow):
    if "windowsupdate" in flow.request.pretty_url or "google.com" in flow.request.pretty_url:
        chain = flow.server_conn.peer_certificates
        real_chains[flow.request.pretty_url] = [cert.to_pem() for cert in chain]
        print(f"Extracted chain: {len(chain)} certs for {flow.request.pretty_url}")
