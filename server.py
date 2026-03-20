import asyncio
import websockets
import json
import os

PORT = int(os.environ.get('PORT', 8765))

clients = {}        # id -> websocket
player_states = {}  # id -> state dict
next_id = 0
lock = asyncio.Lock()

async def broadcast(data, exclude=None):
    msg = json.dumps(data)
    dead = []
    async with lock:
        targets = list(clients.items())
    for pid, ws in targets:
        if pid == exclude:
            continue
        try:
            await ws.send(msg)
        except:
            dead.append(pid)
    for pid in dead:
        await remove_player(pid)

async def send_to(pid, data):
    async with lock:
        ws = clients.get(pid)
    if ws:
        try:
            await ws.send(json.dumps(data))
        except:
            await remove_player(pid)

async def remove_player(pid):
    async with lock:
        clients.pop(pid, None)
        player_states.pop(pid, None)
    await broadcast({'type': 'player_left', 'id': pid})
    print(f"Player {pid} left. Online: {list(clients.keys())}")

async def handle_client(websocket):
    global next_id
    async with lock:
        pid = next_id
        next_id += 1
        clients[pid] = websocket

    print(f"Player {pid} connected. Online: {list(clients.keys())}")

    # Send welcome with existing states
    async with lock:
        existing = {str(k): v for k, v in player_states.items()}
    await send_to(pid, {'type': 'welcome', 'id': pid, 'existing_states': existing})
    await broadcast({'type': 'player_joined', 'id': pid}, exclude=pid)

    try:
        async for message in websocket:
            try:
                msg = json.loads(message)
            except:
                continue

            mtype = msg.get('type')

            if mtype == 'state_update':
                async with lock:
                    player_states[pid] = msg['state']
                await broadcast({'type': 'opponent_state', 'id': pid, 'state': msg['state']}, exclude=pid)

            elif mtype == 'garbage':
                lines = msg.get('lines', 0)
                async with lock:
                    opponents = [oid for oid in clients if oid != pid]
                for oid in opponents:
                    await send_to(oid, {'type': 'garbage', 'lines': lines, 'from': pid})

            elif mtype == 'game_over':
                await broadcast({'type': 'player_lost', 'id': pid})

    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        print(f"Error with player {pid}: {e}")
    finally:
        await remove_player(pid)

async def main():
    print(f"🎮 Tetris WS Server on port {PORT}")
    async with websockets.serve(handle_client, '0.0.0.0', PORT):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
