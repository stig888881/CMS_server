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

import DB_chargepoint
import DB_client
import DataBase

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QTableWidgetItem, QDialog, QMessageBox
import MainWindow
from asyncqt import QEventLoop

import Start_remote


class MainWin(QtWidgets.QMainWindow, MainWindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWin,self).__init__(parent)
        self.parent=parent
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.pushButton_4.clicked.connect(self.createDialogADDclient)
        self.pushButton_5.clicked.connect(self.createDialogADDchargepoint)
        self.pushButton_6.clicked.connect(self.createDialogStartRemote)

    def createDialogADDclient(self):
        self.dialog = DB_Client(self.parent)
        self.dialog.show()
    def createDialogADDchargepoint(self):
        self.dialog = DB_ChargePoint(self.parent)
        self.dialog.show()
    def createDialogStartRemote(self):
        R=self.tableWidget.currentRow()
        C=self.tableWidget.currentColumn()
        N=self.tableWidget.item(R,C).text()
        CP_conn=DataBase.Get_Connector(N)
        self.dialog = StartRemote(self.parent)
        self.dialog.label.setText(N)
        for column in CP_conn:
            ind= CP_conn.index(column)
            if column!="Нет":
                self.dialog.comboBox.addItem("Конектор № "+str(ind+1)+":"+column)
        self.dialog.show()


class DB_Client(QtWidgets.QMainWindow, DB_client.Ui_Form):
    def __init__(self, parent=None):
        super(DB_Client,self).__init__(parent)
        self.parent=parent
        self.setupUi(self)
        self.pushButton.clicked.connect(self.add_client)
        self.pushButton.clicked.connect(self.lineEdit.clear)
        self.pushButton.clicked.connect(self.lineEdit_2.clear)
        self.pushButton.clicked.connect(self.lineEdit_3.clear)



    def add_client(self):
        clinet = self.lineEdit.text()
        id_tag = self.lineEdit_2.text()
        parentid = self.lineEdit_3.text()
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Информация")
        dlg.setText("Клиент добавлен")
        dlg.exec()
        DataBase.connect(DataBase.Insert_client(clinet, id_tag, parentid))
        view_CL()

class DB_ChargePoint(QtWidgets.QMainWindow, DB_chargepoint.Ui_Form):
    def __init__(self, parent=None):
        super(DB_ChargePoint,self).__init__(parent)
        self.parent=parent
        self.setupUi(self)
        self.pushButton.clicked.connect(self.add_cp)
        self.pushButton.clicked.connect(self.lineEdit.clear)
        self.pushButton.clicked.connect(self.lineEdit_2.clear)
        self.pushButton.clicked.connect(self.lineEdit_3.clear)
        self.pushButton.clicked.connect(self.lineEdit_4.clear)

    def add_cp(self):
        vendor = self.lineEdit.text()
        model = self.lineEdit_2.text()
        ip = self.lineEdit_3.text()
        cp_tag = self.lineEdit_4.text()
        Conn_1=self.comboBox.currentText()
        Conn_2 = self.comboBox_2.currentText()
        Conn_3 = self.comboBox_3.currentText()
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Информация")
        dlg.setText("Точка зарядки добавлен")
        dlg.exec()
        DataBase.connect(DataBase.Insert_cp(vendor, model, ip, cp_tag))
        DataBase.connect(DataBase.Insert_cp_connector(cp_tag, Conn_1, Conn_2, Conn_3))
        view_CP()

class StartRemote(QtWidgets.QMainWindow, Start_remote.Ui_Form):
    def __init__(self, parent=None):
        super(StartRemote,self).__init__(parent)
        self.parent=parent
        self.setupUi(self)



global h
h=0
app = QtWidgets.QApplication(sys.argv)
loop = QEventLoop(app)
l=asyncio.new_event_loop()
window = MainWin()
Add_Client=DB_Client()
Add_CP=DB_ChargePoint()
window.show()

logging.basicConfig(level=logging.INFO)
def view_CP():
    CP = DataBase.connect(DataBase.Get_ChargePoint())
    window.tableWidget.setRowCount(0)
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
view_CP()
def view_CL():
    CL=DataBase.connect(DataBase.Get_Client())
    window.tableWidget_2.setRowCount(0)
    for row in CL:
        rowCount=window.tableWidget_2.rowCount()
        window.tableWidget_2.insertRow(rowCount)
        Client=row[1]
        idToken=row[2]
        window.tableWidget_2.setItem(rowCount,0, QTableWidgetItem(Client))
        window.tableWidget_2.setItem(rowCount,1,QTableWidgetItem(idToken))
view_CL()


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
                res=call_result.BootNotificationPayload(
                    current_time=datetime.utcnow().isoformat(),
                    interval=10,
                    status=RegistrationStatus.accepted
                )
                break
            else:
                   B=call_result.BootNotificationPayload(current_time=datetime.utcnow().isoformat(), interval=10, status=RegistrationStatus.rejected)

       return res

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
                window.tableWidget.setItem(0, 5, QTableWidgetItem(id_tag))
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
        Cl = DataBase.connect(DataBase.Get_Client())
        for row in Cl:
            if row[2] == id_tag:
                status="Accepted"
                break
            else:
                status="Invalid"
        if status=="Accepted":
            DataBase.connect(DataBase.Start_transaction(id_tag,status,self.id,timestamp,connector_id,meter_start))
            t=DataBase.connect(DataBase.Get_Trans(id_tag))
            return call_result.StartTransactionPayload(
                    transaction_id=t[0],
                    id_tag_info={
                        'status': 'Accepted'
                    }
                    )
        else:
            DataBase.connect(DataBase.Start_transaction(id_tag, status,self.id,timestamp,connector_id,meter_start))
            return call_result.StartTransactionPayload(
                    transaction_id=DataBase.Get_Trans(id_tag),
                    id_tag_info={
                        'status': 'Invalid'
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
        DataBase.connect(DataBase.Stop_transaction(timestamp,meter_stop,transaction_id))
        return call_result.StopTransactionPayload()

    @on(Action.StatusNotification)
    def on_status_notification(self, connector_id: int, error_code: str, status: str, timestamp:str, **kwargs):
        return call_result.StatusNotificationPayload()
    @on(Action.FirmwareStatusNotification)
    def on_firmware_status(self, status:str):
        return call_result.FirmwareStatusNotificationPayload()

    """Сообщения исходящие от центральной системы"""
    async def change_configuration(self):
        response = await self.call(call.ChangeConfigurationPayload(
            key="HeartbeatInterval",
            value="5"
        ))

        print(response.status)

    async def remote_start_transaction(self):
            global window
            R = window.tableWidget_2.currentRow()
            N = window.tableWidget_2.item(R, 1).text()
            request = call.RemoteStartTransactionPayload(
                id_tag=N
               )
            response = await self.call(request)
            if response.status == RemoteStartStopStatus.accepted:
                print("Transaction Started!!!")

    async def set_charging_profile(self):
        request=call.SetChargingProfilePayload


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