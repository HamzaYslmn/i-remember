
import urllib.request
import json

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    ORANGE = '\033[38;5;208m'
    RED = '\033[91m'
    RESET = '\033[0m'

BASE_URL = "https://i-remember.onrender.com/api"

def make_request(method, endpoint="/i-remember", headers=None, json_data=None, color=None):
    url = f"{BASE_URL}{endpoint}"
    data = None
    req_headers = headers.copy() if headers else {}
    if json_data is not None:
        data = json.dumps(json_data).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            resp_data = response.read().decode("utf-8")
            try:
                resp_json = json.loads(resp_data)
            except Exception:
                resp_json = resp_data
            if color:
                print(f"{color}{method} {response.status}: {resp_json}{Colors.RESET}")
            else:
                print(f"{method} {response.status}: {resp_json}")
            return response, resp_json
    except urllib.error.HTTPError as e:
        try:
            error_json = json.loads(e.read().decode("utf-8"))
        except Exception:
            error_json = e.reason
        if color:
            print(f"{color}{method} {e.code}: {error_json}{Colors.RESET}")
        else:
            print(f"{method} {e.code}: {error_json}")
        return e, error_json

if __name__ == "__main__":
    # 1. CREATE: Yeni bir veri ekle
    print(f"{Colors.GREEN}=== 1. Create (Oluştur) ==={Colors.RESET}")
    _, resp_json = make_request("POST", json_data={
        "data": {"location": "Istanbul"},
        "valid": 1
    }, color=Colors.GREEN)
    key = resp_json["detail"]  # Sunucudan dönen anahtar

    # 2. READ: Eklenen veriyi oku
    print(f"\n{Colors.BLUE}=== 2. Read (Oku) ==={Colors.RESET}")
    make_request("GET", headers={"Authorization": key}, color=Colors.BLUE)

    # 3. UPDATE: Veriyi güncelle
    print(f"\n{Colors.ORANGE}=== 3. Update (Güncelle) ==={Colors.RESET}")
    make_request("PUT", headers={"Authorization": key}, json_data={
        "data": {"location": "Ankara"},
        "valid": 5
    }, color=Colors.ORANGE)

    # 4. DELETE: Veriyi sil
    print(f"\n{Colors.RED}=== 4. Delete (Sil) ==={Colors.RESET}")
    make_request("DELETE", headers={"Authorization": key}, json_data={}, color=Colors.RED)