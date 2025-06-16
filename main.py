# ✅ IMPORTS
import asyncio
import json
import websockets
import requests
from telegram import Bot

# ✅ TELEGRAM CONFIG
TELEGRAM_TOKEN = "8016639456:AAG8QOB8H9OE3BkCSnstPI08tVr-zA7k5Fo"
CHAT_ID = 6939235005

# ✅ FILTER SETTINGS
MIN_BUYERS = 50
MIN_LP_LOCKED_SOL = 3
MIN_MC = 8000
MAX_MC = 25000
REQUIRED_TRUSTED_WALLETS = 3

# ✅ WALLET LIST
TRUSTED_WALLETS = [
    "3BLjRcxWGtR7WRshJ3hL25U3RjWr5Ud98wMcczQqk4Ei",
    "719sfKUjiMThumTt2u39VMGn612BZyCcwbM5Pe8SqFYz",
    "Av3xWHJ5EsoLZag6pr7LKbrGgLRTaykXomDD5kBhL9YQ",
    "3kebnKw7cPdSkLRfiMEALyZJGZ4wdiSRvmoN4rD1yPzV",
    "4BdKaxN8G6ka4GYtQQWk4G4dZRUTX2vQH9GcXdBREFUk",
    "5t9xBNuDdGTGpjaPTx6hKd7sdRJbvtKS8Mhq6qVbo8Qz",
    "3h65MmPZksoKKyEpEjnWU2Yk2iYT5oZDNitGy5cTaxoE",
    "Di75xbVUg3u1qcmZci3NcZ8rjFMj7tsnYEoFdEMjS4ow",
    "As7HjL7dzzvbRbaD3WCun47robib2kmAKRXMvjHkSMB5",
    "2m8Mc2ngJCmpbEEoYhwT9U929z6C4CPKLatWnR775u9a",
    "4DdrfiDHpmx55i4SPssxVzS9ZaKLb8qr45NKY9Er9nNh",
    "G3g1CKqKWSVEVURZDNMazDBv7YAhMNTjhJBVRTiKZygk",
    "CvNiezB8hofusHCKqu8irJ6t2FKY7VjzpSckofMzk5mB",
    "DYAn4XpAkN5mhiXkRB7dGq4Jadnx6XYgu8L5b3WGhbrt",
    "9yYya3F5EJoLnBNKW6z4bZvyQytMXzDcpU5D6yYr4jqL",
    "4AHgEkTsGqY77qtde4UJn9yZCrbGcM7UM3vjT3qM4G5H",
    "8deJ9xeUvXSJwicYptA9mHsU2rN2pDx37KWzkDkEXhU6",
    "ApRnQN2HkbCn7W2WWiT2FEKvuKJp9LugRyAE1a9Hdz1",
    "EHg5YkU2SZBTvuT87rUsvxArGp3HLeye1fXaSDfuMyaf",
    "2T5NgDDidkvhJQg8AHDi74uCFwgp25pYFMRZXBaCUNBH",
    "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
]

bot = Bot(token=TELEGRAM_TOKEN)

# ✅ CONTRACT SAFETY CHECK (mock)
def is_contract_clean(tx):
    return not ("mint" in tx or "freeze" in tx or "updateAuthority" in tx)

# ✅ FILTER CHECK FUNCTION
def passes_filters(tx):
    try:
        buyers = tx.get("buyers", 0)
        lp_locked = tx.get("lp_locked", 0)
        mc = tx.get("market_cap", 0)
        trusted = len([w for w in tx.get("wallets", []) if w in TRUSTED_WALLETS])
        
        return (
            buyers >= MIN_BUYERS and
            lp_locked >= MIN_LP_LOCKED_SOL and
            MIN_MC <= mc <= MAX_MC and
            trusted >= REQUIRED_TRUSTED_WALLETS and
            is_contract_clean(tx.get("contract", {}))
        )
    except:
        return False

# ✅ MAIN STREAMING FUNCTION
async def listen():
    url = "wss://rpc.helius.xyz/?api-key=7dba3ed1-7418-4c81-9c48-9d551f1a221a"
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({"type": "subscribe", "accounts": TRUSTED_WALLETS}))
        print("🚀 Listening to Smart Wallets...")

        while True:
            try:
                message = await ws.recv()
                data = json.loads(message)
                tx = data.get("events", {})

                if passes_filters(tx):
                    token = tx.get("token", {}).get("symbol", "Unknown")
                    wallet = tx.get("account", "...")
                    mc = tx.get("market_cap", "?")
                    buyers = tx.get("buyers", "?")
                    
                    text = f"🚨 New Smart Entry\nToken: {token}\nWallet: {wallet[:6]}...{wallet[-4:]}\nBuyers: {buyers} | MC: ${mc}\n🔗 [Solscan](https://solscan.io/account/{wallet})"
                    bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='Markdown')

            except Exception as e:
                print("❌ Error:", e)

if __name__ == "__main__":
    asyncio.run(listen())
