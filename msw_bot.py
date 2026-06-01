import requests
import time
import threading
from flask import Flask
import os

app = Flask('')

@app.route('/')
def home():
    return "M3.0 is Alive!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# --- 設定區域 ---
PLAYER_MAP = {
    "20372100000223997": {"name": "別時", "image": "https://mod-file.dn.nexoncdn.co.kr/shop/17/1745254512144.png"},
    "20372100003462156": {"name": "ㄋㄍ奧米加", "image": "https://mod-file.dn.nexoncdn.co.kr/shop/987/1778554167572.png"},
    "20372100004194770": {"name": "阿丞", "image": "https://mod-file.dn.nexoncdn.co.kr/profile/21/1778951712386.png"},
    "20372000486671177": {"name": "韓國愛芮", "image": "https://mod-file.dn.nexoncdn.co.kr/shop/58/1775909266323.png"},
    "20372100003863084": {"name": "阿卡利作者", "image": "https://mod-file.dn.nexoncdn.co.kr/shop/368/1757691781562.png"},
    "20372100003462165": {"name": "奧米加獸作者", "image": "https://mod-file.dn.nexoncdn.co.kr/shop/988/1775817850083.png"},
    "20372000285890864": {"name": "黑子", "image": "https://mod-file.dn.nexoncdn.co.kr/shop/703/1746433990616.png"},
    "20372100002340154": {"name": "金武金", "image": "https://mod-file.dn.nexoncdn.co.kr/shop/746/1777216923670.png"},
    "20372100006407090": {"name": "北極熊初音作者", "image": "https://mod-file.dn.nexoncdn.co.kr/shop/233/1749625499529.png"},
    "20372100005714983": {"name": "AWAWA", "image": "https://mod-file.dn.nexoncdn.co.kr/shop/951/1763371995763.png"},
    "20372100003266920": {"name": "星見雅", "image": "https://mod-file.dn.nexoncdn.co.kr/shop/4/1735907794712.png"},
    "20372100005888267": {"name": "AI愛芮", "image": "https://mod-file.dn.nexoncdn.co.kr/shop/580/1779101350088.png"},
    "20372002064454021": {"name": "寶可夢黑肉", "image": "https://mod-file.dn.nexoncdn.co.kr/profile/78/1777380730697.png"},
    "20372100000376567": {"name": "女僕愛莉作者", "image": "https://mod-file.dn.nexoncdn.co.kr/shop/816/1714161476844.png"},
    "20372100001023713": {"name": "Majajaja", "image": "https://mod-file.dn.nexoncdn.co.kr/shop/415/1779709498317.png"},
    "20372100005173094": {"name": "月亮已經紅了", "image": "https://mod-file.dn.nexoncdn.co.kr/profile/738/1777694497601.png"},
    "20372100001142530": {"name": "北極熊", "image": "https://mod-file.dn.nexoncdn.co.kr/shop/212/1758175186019.png"}
}

DEFAULT_IMAGE = "https://example.com/default.png"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1506776199039553739/0OEemnWdcbnmjCwOl5UrUKnXUFeUKKAnqbFyUhvILB4-f42OG0-1k2LENsoFBuoQsc_J"
DISCORD_WEBHOOK_URL_PAKA = "https://discord.com/api/webhooks/1509309222444208228/GHs_6vvj6nG8WkA9Y9BIuIGklRBJpTOEqGrdG5oG2wzIEC3lwJ7nLjZ90t8l-D4Ofv90"

SPECIAL_PLAYERS = [
    "20372100000223997", # 別時
    "20372100003462156", # ㄋㄍ奧米加
    "20372100004194770", # 阿丞
    "20372100005888267", # AI愛芮
    "20372100000376567", # 女僕愛莉作者
]

# 💡 建議至少調到 30 ~ 60，避免過度頻繁觸發 Cloudflare 鎖 IP
CHECK_INTERVAL = 15 
API_URL_TEMPLATE = "https://mverse-api.nexon.com/social/v1/profile/{}"

last_known_data = {pid: {"is_online": None, "world_name": None} for pid in PLAYER_MAP.keys()}

def send_ip_blocked_warning(status_code):
    """當發現被鎖 IP 時，發送警告到 Discord"""
    print(f"⚠️ [警告] 甲賀金城武MASA太帥了: {status_code}。正在發送通知...")
    payload = {
        "embeds": [{
            "title": "⚠️ 甲賀金城武MASA被自己帥醒了 (Error 1015)",
            "description": f"甲賀金城武MASA照鏡子了。\n**原因**：甲賀金城武MASA，已經帥到 rate limit。\n**HTTP 狀態碼**：`{status_code}`\n\n倒數機制已啟動：**甲賀金城武MASA出門買消夜 10 分鐘**，請女性注意。",
            "color": 16744192,  # 橘色
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except Exception as e:
        print(f"發送 IP 被鎖警告至 DC 失敗: {e}")

def check_players():
    global last_known_data
    print(f"[{time.strftime('%H:%M:%S')}] 啟動掃描...")

    for pid, info in PLAYER_MAP.items():
        time.sleep(0.4) 
        try:
            name = info["name"]
            custom_image = info.get("image", DEFAULT_IMAGE)
            url = API_URL_TEMPLATE.format(pid)
            
            # 偽裝稍微完整一點的瀏覽器頭
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            # 💡 核心新增：如果狀態碼不是 200 (例如 429 或 403)，判定為被鎖 IP
            if response.status_code != 200:
                print(f"❌ 擷取 {name} 失敗，狀態碼: {response.status_code}")
                if response.status_code in [429, 403, 1015]:
                    send_ip_blocked_warning(response.status_code)
                    print("😴 進入冷卻模式，暫停打擾 Nexon 10 分鐘...")
                    time.sleep(600)  # 暫停 600 秒 (10分鐘)
                    return           # 直接跳出這一輪的掃描，重新等待
                continue

            data_root = response.json().get('data', {})
            
            is_online = (data_root.get('isOnline') == 1)
            world_name = data_root.get('worldName') 
            p_code = data_root.get('profileCode', '未知')
            
            prev = last_known_data[pid]

            if prev["is_online"] is None:
                last_known_data[pid] = {"is_online": is_online, "world_name": world_name}
                continue

            should_notify = False
            status_msg = ""
            
            if is_online != prev["is_online"]:
                should_notify = True
                status_msg = "🟢 上線了！" if is_online else "🔴 下線了。"
            elif is_online and world_name != prev["world_name"]:
                should_notify = True
                status_msg = "🔄 切換世界"

            if should_notify:
                last_known_data[pid] = {"is_online": is_online, "world_name": world_name}
                current_world = world_name if world_name else "大廳或選單中"
                
                if is_online:
                    if "切換世界" in status_msg:
                        color = 16776960  
                        title_icon = "🔄"
                    else:
                        color = 65280     
                        title_icon = "🟢"
                else:
                    color = 16711680      
                    title_icon = "🔴"
                
                description = f"代碼：`{p_code}`\n狀態：**{status_msg}**"
                if is_online:
                    description += f"\n目前位置：`{current_world}`"

                payload = {
                    "embeds": [{
                        "title": f"{title_icon} 【{name}】{status_msg}",  
                        "description": description,
                        "thumbnail": {"url": custom_image}, 
                        "color": color,                                  
                        "footer": {"text": f"PPSN: {pid}"},
                        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                    }]
                }
                
                if pid in SPECIAL_PLAYERS:
                    requests.post(DISCORD_WEBHOOK_URL_PAKA, json=payload, timeout=10)
                    print(f"🚀 [dc2] 專屬通知: {name}")
                else:
                    requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
                    print(f"📣 [dc1] 一般通知: {name}")

        except Exception as e:
            print(f"檢查 {pid} ({info['name']}) 出錯: {e}")

def main_loop():
    while True:
        check_players()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    print("--- 正在嘗試發送啟動訊號到 Discord ---")
    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL, 
            json={"content": "🤖 甲賀金城武MASA已現身!"},
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=10
        )
        if response.status_code in [200, 204]:
            print(f"✅ Discord 啟動訊號發送成功！(狀態碼: {response.status_code})")
        else:
            print(f"❌ Discord 拒絕請求，錯誤代碼: {response.status_code}")
            
    except Exception as e:
        print(f"💥 啟動訊號發送過程中發生異常: {e}")

    monitor_thread = threading.Thread(target=main_loop, daemon=True)
    monitor_thread.start()
    print("📡 後台監控線程已啟動，開始循環掃描。")

    print("🌐 正在啟動 Flask Web 服務...")
    run_web()
