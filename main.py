import requests
import time
from datetime import datetime

WALLET_ADDRESS = "ltc1qdhwzah4cat32vdepdwwzkeah02zq0d568rn6gt"
WEBHOOK_URL = "https://discord.com/api/webhooks/1360213152381407293/va2f_2YQo2FmGjHvvqCUIH1fPlX0u5h4JtTiNclsSjaU5q8SpPpRh9wo0sVixK7bpurC"
CHECK_INTERVAL = 60  # seconds

def get_latest_transaction():
    url = f"https://api.blockcypher.com/v1/ltc/main/addrs/{WALLET_ADDRESS}?limit=1"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    if 'txrefs' in data and len(data['txrefs']) > 0:
        return data['txrefs'][0]
    return None

def send_to_discord(tx):
    tx_hash = tx['tx_hash']
    confirmations = tx.get('confirmations', 0)
    amount = tx['value'] / 1e8  # convert satoshis to LTC
    received = tx.get('tx_input_n', -1) == -1  # true if this address received the LTC
    direction = "➕ Received" if received else "➖ Sent"

    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    message = {
        "content": (
            f"📦 **New Litecoin Transaction Detected!**\n"
            f"{direction}: **{amount:.8f} LTC**\n"
            f"🔗 [View TX](https://live.blockcypher.com/ltc/tx/{tx_hash})\n"
            f"⏰ Time: {timestamp}\n"
            f"🔄 Confirmations: {confirmations}"
        )
    }
    requests.post(WEBHOOK_URL, json=message)

def main():
    print("🚀 Litecoin Wallet Monitor Started...")
    last_seen_tx = None

    while True:
        try:
            latest_tx = get_latest_transaction()
            if latest_tx:
                if latest_tx['tx_hash'] != last_seen_tx:
                    send_to_discord(latest_tx)
                    last_seen_tx = latest_tx['tx_hash']
                    print(f"🔔 New TX Sent: {last_seen_tx}")
                else:
                    print("No new transaction.")
            else:
                print("No transactions found yet.")
        except Exception as e:
            print(f"⚠️ Error: {e}")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
