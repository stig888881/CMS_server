import sys
import asyncio
import logging
import websockets
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result, call
from ocpp.v16.enums import *
from threading import Thread
import DataBase

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QTableWidgetItem
import MainWindow
from asyncqt import QEventLoop

class MainWin(QtWidgets.QMainWindow, MainWindow.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна


app = QtWidgets.QApplication(sys.argv)
loop = QEventLoop(app)
l=asyncio.new_event_loop()
window = MainWin()
window.show()

logging.basicConfig(level=logging.INFO)

CP = DataBase.connect(DataBase.Get_ChargePoint())
for row in CP:
    rowCount = window.tableWidget.rowCount()
    window.tableWidget.insertRow(rowCount)
    CP_N=row[4]
    Vendor = row[1]
    Model = row[2]
    window.tableWidget.setItem(rowCount, 0, QTableWidgetItem(CP_N))
    window.tableWidget.setItem(rowCount, 1, QTableWidgetItem(Vendor))
    window.tableWidget.setItem(rowCount, 2, QTableWidgetItem(Model))

class ChargePoint(cp):
    @on(Action.BootNotification)
    def on_boot_notification(  self, charge_point_vendor: str, charge_point_model: str, **kwargs):
       global window
       CP = DataBase.connect(DataBase.Get_ChargePoint())
       for row in CP:
            if charge_point_vendor == row[2] and charge_point_model == row[1]:
                window.tableWidget.setItem(row[0]-1, 3, QTableWidgetItem("Подключен"))
                B=call_result.BootNotificationPayload(
                    current_time=datetime.utcnow().isoformat(),
                    interval=10,
                    status=RegistrationStatus.accepted
                )
                break
            else:
                   B=call_result.BootNotificationPayload(current_time=datetime.utcnow().isoformat(), interval=10, status=RegistrationStatus.rejected)

       return B

    @on("Heartbeat")
    def on_heartbeat(self):
        print("Got a Heartbeat!", self.id)
        return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        )
    @on(Action.Authorize)
    def on_autorize(self, id_tag: str, **kwargs):
        return call_result.AuthorizePayload(
            id_tag_info={
                'status': 'Accepted'
            }
        )
    async def change_configuration(self):
        response = await self.call(call.ChangeConfigurationPayload(
            key="HeartbeatInterval",
            value="5"
        ))

        print(response.status)


async def on_connect(websocket, path):
    """For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
    try:
        requested_protocols = websocket.request_headers["Sec-WebSocket-Protocol"]
    except KeyError:
        logging.error("Client hasn't requested any Subprotocol. Closing Connection")
        return await websocket.close()
    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        # In the websockets lib if no subprotocols are supported by the
        # client and the server, it proceeds without a subprotocol,
        # so we have to manually close the connection.
        logging.warning(
            "Protocols Mismatched | Expected Subprotocols: %s,"
            " but client supports  %s | Closing connection",
            websocket.available_subprotocols,
            requested_protocols,
        )
        return await websocket.close()

    charge_point_id = path.strip("/")
    cp = ChargePoint(charge_point_id, websocket)
    print(charge_point_id)
    print(websocket.remote_address[0])

    async def hhhh():
        global h
        while True:
            if h==1:
                if cp.id=="CP_1":
                    await cp.change_configuration()
                    h=0
                else:
                    await asyncio.sleep(0.1)
            else:
                await asyncio.sleep(0.1)

    await asyncio.gather(cp.start())

async def main():
    global server
    server = await websockets.serve(
        on_connect, "0.0.0.0", 9000, subprotocols=["ocpp1.6"]
    )

    logging.info("Server Started listening to new connections...")
    await server.wait_closed()

async def master():
    await main()

def close():
    global server
    server.close()
def open():
    asyncio.create_task(master())


window.pushButton.clicked.connect(close)
window.pushButton_2.clicked.connect(open)

loop.run_forever()