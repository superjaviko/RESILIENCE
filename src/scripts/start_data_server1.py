# launch_server.py
import sys
import bge

# Agrega la ruta donde está el archivo del servidor
#sys.path.append(bge.logic.expandPath("//scripts/data_server1.py"))  # O ajusta según tu estructura

from data_server1 import GoogleSheetServer  # O ServerThread

cont = bge.logic.getCurrentController()
own = cont.owner

if "server_started" not in own:
    own["server_started"] = True
    server = GoogleSheetServer()
    server.start()
    print("🟢 Google Sheet server iniciado en segundo plano.")
