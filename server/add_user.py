# add_user.py
import time
from server.server import RemoteControlServer

if __name__ == "__main__":
    server = RemoteControlServer()
    success, message = server.add_user("Nsfr750", "22243", is_admin=True)
    print(f"Success: {success}, Message: {message}")