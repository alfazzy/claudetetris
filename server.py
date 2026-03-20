import socket
import threading
import json
import time

HOST = '0.0.0.0'
import os
PORT = int(os.environ.get('PORT', 5555))

clients = {}       # id -> conn
player_states = {} # id -> board state dict
lock = threading.Lock()
next_id = 0

def broadcast(data, exclude=None):
    msg = (json.dumps(data) + '\n').encode()
    dead = []
    with lock:
        for pid, conn in clients.items():
            if pid == exclude:
                continue
            try:
                conn.sendall(msg)
            except:
                dead.append(pid)
    for pid in dead:
        remove_player(pid)

def send_to(pid, data):
    msg = (json.dumps(data) + '\n').encode()
    with lock:
        conn = clients.get(pid)
    if conn:
        try:
            conn.sendall(msg)
        except:
            remove_player(pid)

def remove_player(pid):
    with lock:
        clients.pop(pid, None)
        player_states.pop(pid, None)
    broadcast({'type': 'player_left', 'id': pid})
    print(f"Player {pid} disconnected. Players remaining: {list(clients.keys())}")

def handle_client(conn, pid):
    buffer = ''
    try:
        while True:
            data = conn.recv(4096).decode()
            if not data:
                break
            buffer += data
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line)
                except:
                    continue
                mtype = msg.get('type')

                if mtype == 'state_update':
                    with lock:
                        player_states[pid] = msg['state']
                    broadcast({'type': 'opponent_state', 'id': pid, 'state': msg['state']}, exclude=pid)

                elif mtype == 'garbage':
                    lines = msg.get('lines', 0)
                    # Send garbage to all opponents
                    with lock:
                        opponents = [oid for oid in clients if oid != pid]
                    for oid in opponents:
                        send_to(oid, {'type': 'garbage', 'lines': lines, 'from': pid})

                elif mtype == 'game_over':
                    broadcast({'type': 'player_lost', 'id': pid})

    except Exception as e:
        print(f"Error with player {pid}: {e}")
    finally:
        remove_player(pid)
        conn.close()

def accept_loop(server):
    global next_id
    while True:
        try:
            conn, addr = server.accept()
            pid = next_id
            next_id += 1
            with lock:
                clients[pid] = conn
            print(f"Player {pid} connected from {addr}. Players: {list(clients.keys())}")
            # Send this player their ID and existing players' states
            with lock:
                existing = {str(k): v for k, v in player_states.items()}
            send_to(pid, {'type': 'welcome', 'id': pid, 'existing_states': existing})
            # Tell others a new player joined
            broadcast({'type': 'player_joined', 'id': pid}, exclude=pid)
            t = threading.Thread(target=handle_client, args=(conn, pid), daemon=True)
            t.start()
        except Exception as e:
            print(f"Accept error: {e}")
            break

if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(8)
    print(f"🎮 Tetris LAN Server running on port {PORT}")
    print(f"   Share your local IP with friends to connect!")
    accept_loop(server)
