import asyncio
import websockets
from datetime import datetime

from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call


class ChargePoint(cp):
    async def change_configuration(self):
        response = await self.call(call.ChangeConfigurationPayload(
            key="HeartbeatInterval",
            value="10"
        ))

        print(response.status)


async def on_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint instance
    and start listening for messages.

    """
    charge_point_id = path.strip('/')
    cp = ChargePoint(charge_point_id, websocket)

    await asyncio.gather(cp.start(), cp.change_configuration())


async def main():
    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        9000,
        subprotocols=['ocpp1.6']
    )

    await server.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())