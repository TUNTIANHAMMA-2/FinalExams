# ASCII Attendance Frontend

React + Vite frontend for the ASCII attendance MVP.

## Run

```bash
npm install
npm run dev
```

Open the Vite URL printed in the terminal, usually `http://localhost:5173/`.

## Camera Preview

The `/live` page uses the browser camera API (`navigator.mediaDevices.getUserMedia`) to request camera permission and render a real-time ASCII preview in the browser.

Camera access only works on secure origins. `localhost` is allowed, so running the Vite dev server locally is enough.

## Current Integration Boundary

This frontend currently handles the visual demo layer:

- Browser camera permission
- Real-time ASCII preview
- Static pages for registration, records, and stats

The OpenCV face recognition and attendance writing logic still runs from the Python CLI:

```bash
python -m app.main register --user-id 2026001 --name 张三 --image data/faces/zhangsan.jpg
python -m app.main run
python -m app.main stats
```

The frontend and Python recognizer are not connected through an HTTP API yet.

## Checks

```bash
npm run lint
npm run build
```
