"""Chuyển đổi cookie JSON (từ EditThisCookie) sang chuỗi header string.

Cách dùng:
  1. Mở EditThisCookie trên Chrome (đã đăng nhập Facebook)
  2. Nhấn Export → Copy
  3. Lưu vào file, ví dụ: cookies_raw.json
  4. Chạy:  python convert_cookie.py cookies_raw.json
  5. Copy kết quả dán vào FB_COOKIE trong file .env
"""

import json
import sys


def convert(json_path: str) -> str:
    with open(json_path, encoding="utf-8") as f:
        cookies = json.load(f)

    # Chỉ giữ cookie của facebook.com
    fb_cookies = [
        c for c in cookies
        if "facebook.com" in c.get("domain", "")
    ]

    # Ghép thành header string: name=value; name=value; ...
    parts = [f'{c["name"]}={c["value"]}' for c in fb_cookies]
    return "; ".join(parts)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python convert_cookie.py <đường_dẫn_file_json>")
        print("Ví dụ:    python convert_cookie.py cookies_raw.json")
        sys.exit(1)

    result = convert(sys.argv[1])
    print("\n✅ Dán dòng sau vào FB_COOKIE trong file .env:\n")
    print(result)
