"""
mouse-phone — PC Client (modalità cloud/Render)
Uso: py pc_client.py https://mouse-phone.onrender.com

Per connessione locale usa local_server.py invece.
"""
import sys, time
import socketio
import pyautogui

SERVER_URL = sys.argv[1] if len(sys.argv) > 1 else "https://mouse-phone.onrender.com"
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0
W, H = pyautogui.size()
print(f"🖥  Schermo: {W}x{H}  —  Server: {SERVER_URL}\n")

def sc(x,y): return max(0,min(W-1,int(float(x)*W))), max(0,min(H-1,int(float(y)*H)))

sio = socketio.Client(reconnection=True, reconnection_attempts=0, logger=False, engineio_logger=False)

@sio.event
def connect():
    print("✅ Connesso!"); sio.emit('register',{'role':'pc'})

@sio.event
def disconnect():
    print("❌ Disconnesso...")

@sio.on('registered')
def _(d): print(f"📡 {d.get('message','')}\n📱 In attesa del telefono...\n")

@sio.on('phone_connected')
def _(_): print("📱 Telefono connesso!\n")

@sio.on('move')
def _(d):
    try: x,y=sc(d['x'],d['y']); pyautogui.moveTo(x,y,_pause=False)
    except: pass

@sio.on('click')
def _(d):
    try:
        x,y=sc(d['x'],d['y']); btn=d.get('button','left')
        pyautogui.moveTo(x,y,_pause=False); time.sleep(0.03)
        pyautogui.click(x,y,button=btn,_pause=False)
        print(f"🖱  Click {btn} ({x},{y})")
    except: pass

@sio.on('mouse_down')
def _(d):
    try:
        x,y=sc(d['x'],d['y'])
        pyautogui.moveTo(x,y,_pause=False); time.sleep(0.03)
        pyautogui.mouseDown(x,y,button='left',_pause=False)
        print(f"🖱  MouseDown ({x},{y})")
    except: pass

@sio.on('mouse_up')
def _(d):
    try: pyautogui.mouseUp(button='left',_pause=False); print("🖱  MouseUp")
    except: pass

@sio.on('move_drag')
def _(d):
    try: x,y=sc(d['x'],d['y']); pyautogui.moveTo(x,y,_pause=False)
    except: pass

@sio.on('drag_start')
def _(d):
    try:
        x,y=sc(d['x'],d['y'])
        pyautogui.moveTo(x,y,_pause=False); time.sleep(0.03)
        pyautogui.mouseDown(x,y,button='left',_pause=False)
        print(f"🟠 Drag start ({x},{y})")
    except: pass

@sio.on('drag_end')
def _(d):
    try: pyautogui.mouseUp(button='left',_pause=False); print("🟠 Drag end")
    except: pass

@sio.on('scroll')
def _(d):
    try:
        clicks=-(int(d.get('delta',0))//30)
        if clicks: pyautogui.scroll(clicks)
    except: pass

def main():
    print("="*50+"\n     🖱  MOUSE PHONE — PC Client\n"+"="*50+"\n")
    while True:
        try:
            print(f"Connessione a {SERVER_URL}...")
            sio.connect(SERVER_URL,transports=['websocket']); sio.wait()
        except KeyboardInterrupt:
            print("\n👋 Uscita."); sio.disconnect(); break
        except Exception as e:
            print(f"[ERRORE] {e}\nRiprovo tra 5s..."); time.sleep(5)

if __name__=='__main__': main()
