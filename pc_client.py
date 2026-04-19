"""
mouse-phone — PC Client (Touchpad mode)
Riceve movimenti relativi dal telefono e muove il mouse.

Installazione:
    pip install "python-socketio[client]" pyautogui

Uso:
    python pc_client.py
    python pc_client.py https://il-tuo-server.onrender.com
"""

import sys
import time
import pyautogui
import socketio

SERVER_URL = sys.argv[1] if len(sys.argv) > 1 else "https://mouse-phone.onrender.com"

pyautogui.FAILSAFE = True   # angolo in alto a sinistra = stop emergenza
pyautogui.PAUSE    = 0

W, H = pyautogui.size()
print(f"🖥  Schermo: {W}x{H}")
print(f"🌐  Server:  {SERVER_URL}")
print(f"⚠️  Porta il mouse nell'angolo in alto a sinistra per fermare\n")

sio = socketio.Client(reconnection=True, reconnection_attempts=0, logger=False)


@sio.event
def connect():
    print("✅ Connesso al server!")
    sio.emit('register', {'role': 'pc'})


@sio.event
def disconnect():
    print("❌ Disconnesso. Riconnessione...")


@sio.on('registered')
def on_registered(data):
    print(f"📡 Registrato — {data.get('message', '')}")
    print("📱 Apri l'URL del server sul telefono e inizia a usarlo!\n")


@sio.on('phone_connected')
def on_phone_connected(data):
    print("📱 Telefono connesso!")


@sio.on('move_rel')
def on_move_rel(data):
    """Muove il mouse di un delta relativo."""
    try:
        dx = float(data['dx'])
        dy = float(data['dy'])
        x, y = pyautogui.position()
        # Clamp dentro lo schermo
        nx = max(0, min(W - 1, x + dx))
        ny = max(0, min(H - 1, y + dy))
        pyautogui.moveTo(int(nx), int(ny))
    except Exception as e:
        print(f"[MOVE ERR] {e}")


@sio.on('click')
def on_click(data):
    try:
        button = data.get('button', 'left')
        print(f"🖱  Click {button}")
        pyautogui.click(button=button)
    except Exception as e:
        print(f"[CLICK ERR] {e}")


@sio.on('double_click')
def on_double_click(data):
    try:
        print("🖱  Doppio click")
        pyautogui.doubleClick()
    except Exception as e:
        print(f"[DBLCLICK ERR] {e}")


@sio.on('scroll')
def on_scroll(data):
    try:
        delta = int(data.get('delta', 0))
        clicks = -delta // 30
        if clicks != 0:
            pyautogui.scroll(clicks)
    except Exception as e:
        print(f"[SCROLL ERR] {e}")


def main():
    print("=" * 45)
    print("    🖱  MOUSE PHONE — PC Client")
    print("=" * 45 + "\n")
    while True:
        try:
            print(f"Connessione a {SERVER_URL}...")
            sio.connect(SERVER_URL, transports=['websocket'])
            sio.wait()
        except KeyboardInterrupt:
            print("\n👋 Uscita.")
            sio.disconnect()
            break
        except Exception as e:
            print(f"[ERRORE] {e} — riprovo tra 5s...")
            time.sleep(5)


if __name__ == '__main__':
    main()
