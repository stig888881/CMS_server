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

global h
h=0
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
    window.tableWidget.setItem(rowCount, 3, QTableWidgetItem("Отключен"))

class ChargePoint(cp):

    """Сообщения приходящие от точки зарядки"""
    @on(Action.BootNotification)
    def on_boot_notification(  self, charge_point_vendor: str, charge_point_model: str, **kwargs):
       global window
       CP = DataBase.connect(DataBase.Get_ChargePoint())
       for row in CP:
            print(row[1])
            if charge_point_vendor == row[1] and charge_point_model == row[2]:
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
        Client = DataBase.connect(DataBase.Get_Client())
        for row in Client:
            if row[2] == id_tag:
                window.tableWidget.setItem(0, 5, QTableWidgetItem(id_tag+": "+row[1]))
                print('another connection')
                return call_result.AuthorizePayload(
                    id_tag_info={
                        'status': 'Accepted'
                        }
                        )
            else:
                print('Denied')
                return call_result.AuthorizePayload(
                    id_tag_info={
                        'status': 'Invalid'
                        }
                        )
            break
    @on(Action.MeterValues)
    def on_meter_values(self, connector_id: int, meter_value: list, **kwargs):
        return call_result.MeterValuesPayload()

    @on(Action.StartTransaction)
    def on_start_transaction(self, connector_id: int, id_tag: str, meter_start: int, timestamp: str, **kwargs):
        DataBase.connect(DataBase.Insert(id_tag))
        return call_result.StartTransactionPayload(
            transaction_id=DataBase.Get_Trans(id_tag),
            id_tag_info = {
            'status': 'Accepted'
                        }
        )
    @on(Action.DataTransfer)
    def on_data_transfer(self, vendor_id: str, **kwargs):
        return call_result.DataTransferPayload(
            status=DataTransferStatus.accepted
        )
    @on(Action.DiagnosticsStatusNotification)
    def on_diagnostics_status(self, status:str):
        return call_result.DiagnosticsStatusNotificationPayload()


    @on(Action.StopTransaction)
    def on_stop_transaction(self, meter_stop: int, timestamp: str, transaction_id: int, **kwargs):
        return call_result.StopTransactionPayload()

    @on(Action.StatusNotification)
    def on_status_notification(self, connector_id: int, error_code: str, status: str, timestamp:str, **kwargs):
        return call_result.StatusNotificationPayload()
    @on(Action.FirmwareStatusNotification)
    def on_firmware_status(self, status:str):
        return call_result.FirmwareStatusNotificationPayload()

    async def change_configuration(self):
        response = await self.call(call.ChangeConfigurationPayload(
            key="HeartbeatInterval",
            value="5"
        ))

        print(response.status)

    async def remote_start_transaction(self):
            global window
            R = window.tableWidget.currentRow()
            N = window.tableWidget.item(R, 5).text()
            request = call.RemoteStartTransactionPayload(
                id_tag=N
               )
            response = await self.call(request)
            if response.status == RemoteStartStopStatus.accepted:
                print("Transaction Started!!!")


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

    async def remotestart():
        global h,N
        while True:
            if h==1:
                if cp.id==N:
                    await cp.remote_start_transaction()
                    h=0
                else:
                    await asyncio.sleep(0.1)
            else:
                await asyncio.sleep(0.1)
    try:
        await asyncio.gather(cp.start(),remotestart())
    except websockets.exceptions.ConnectionClosedError:
        for row in range(window.tableWidget.rowCount()):
            if charge_point_id == window.tableWidget.item(row,0).text():
                window.tableWidget.setItem(row, 3, QTableWidgetItem("Отключен"))
                window.tableWidget.setItem(row, 5, QTableWidgetItem(""))
                break

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
def button_remote():
    global N
    R=window.tableWidget.currentRow()
    C=window.tableWidget.currentColumn()
    N=window.tableWidget.item(R,C).text()
    global h
    h=1


window.pushButton.clicked.connect(close)
window.pushButton_2.clicked.connect(open)
window.pushButton_3.clicked.connect(button_remote)

loop.run_forever()