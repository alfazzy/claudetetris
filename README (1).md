# 🎮 Tetris Versus — Cloud Multiplayer (Railway)

Play competitive Tetris with friends over the internet using a free Railway server.

---

## 📦 Files

| File | Purpose |
|---|---|
| `server.py` | WebSocket game server — deploy this to Railway |
| `client.py` | Pygame client — everyone runs this locally |
| `requirements.txt` | Server dependencies (just `websockets`) |
| `Procfile` | Tells Railway how to start the server |

---

## 🚀 Step 1 — Deploy the server to Railway (free, one-time)

1. Create a free account at **railway.app**
2. Create a new GitHub repo and push these 4 files into it:
   - `server.py`
   - `requirements.txt`
   - `Procfile`
   - (optionally) `README.md`
3. In Railway: **New Project → Deploy from GitHub repo** → select your repo
4. Railway will auto-detect and deploy. Wait ~1 minute.
5. Go to your project → **Settings → Networking → Generate Domain**
6. You'll get a URL like: `your-app-name.up.railway.app`

That's your server URL. **Share it with your friends.**

---

## 🎮 Step 2 — Everyone installs and runs the client

```bash
pip install pygame websockets
python client.py
```

When the connect screen appears, type your Railway URL:
```
your-app-name.up.railway.app
```
Press Enter. Done — you're connected!

---

## 🕹️ Controls

| Key | Action |
|---|---|
| ← → | Move |
| ↑ | Rotate clockwise |
| Z | Rotate counter-clockwise |
| ↓ | Soft drop |
| Space | Hard drop |
| C / LShift | Hold piece |
| Escape | Quit |

---

## 💥 Garbage System

| Lines cleared | Garbage sent |
|---|---|
| 1 line | 0 rows |
| 2 lines | 1 row |
| 3 lines | 2 rows |
| 4 lines (Tetris!) | 4 rows |
| Combo (2+ consecutive) | +1 row per 2 combos |

Incoming garbage is **cancelled** by your own line clears.

---

## 🔧 Troubleshooting

**"Connection failed"** — Double-check your Railway URL. Make sure you generated a public domain in Railway's Networking settings.

**Lag** — Railway free tier cold-starts after inactivity. First connection may take 10–15 seconds; subsequent ones are instant.

**Port issues** — Railway handles port assignment automatically via the `PORT` environment variable. Nothing to configure.
