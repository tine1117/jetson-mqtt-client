import os, uuid, hashlib, socket

#DEFAULT SETTING
DEFAULT_ID = "edgi-"

#GET CLIENT ID - 고유 아이디 생성 (리눅스, 윈도우)
def get_id() -> str:
    try:
        with open("/etc/machine-id", "r") as f:
            return DEFAULT_ID + _convert(f.read().strip())
    except Exception:
        pass

    try:
        import winreg
        k = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography",
            0,
            winreg.KEY_READ | getattr(winreg, "KEY_WOW64_64KEY", 0),
        )
        val, _ = winreg.QueryValueEx(k, "MachineGuid")
        winreg.CloseKey(k)
        return DEFAULT_ID +  _convert(val)
    except Exception:
        pass

    #MAC 예비
    try:
        return DEFAULT_ID + _convert(f"{uuid.getnode():012x}")
    except Exception:
        return DEFAULT_ID + str(00000)
    
def get_ip():
    return socket.gethostbyname(socket.gethostname())

def _convert(temp : str) -> str: #SHA-> INT(16) -> %100000 -> split:5
    temp = "".join(temp.split())
    num = int(hashlib.sha1(temp.encode()).hexdigest(), 16) % 100000 
    return f"{num:05d}"