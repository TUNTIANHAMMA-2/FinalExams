# ASCII Attendance Frontend

React + Vite frontend for the ASCII attendance MVP.

## Run

Start the Python API first from the project root:

```bash
python -m app.main serve
```

Then start the frontend:

```bash
npm install
npm run dev
```

Open the Vite URL printed in the terminal, usually `http://localhost:5173/`.

The frontend calls `http://127.0.0.1:8765` by default. Override it with `VITE_API_BASE_URL` if you start the API on another port.

## Camera And Recognition

The `/live` page uses the browser camera API (`navigator.mediaDevices.getUserMedia`) to request camera permission, render a real-time ASCII preview, and send camera frames to the Python API for OpenCV LBPH recognition and attendance writing.

Camera access only works on secure origins. `localhost` is allowed, so running the Vite dev server locally is enough.

## Feature Flow

- `/register`: capture a face image and call `POST /api/register`.
- `/live`: stream camera frames as ASCII and call `POST /api/recognize`.
- `/records`: call `GET /api/records` and export CSV.
- `/stats`: call `GET /api/stats` and render attendance summaries.

The Python CLI is still available for standalone demos:

```bash
python -m app.main register --user-id 2026001 --name 张三 --image data/faces/zhangsan.jpg
python -m app.main run
python -m app.main stats
```

## Checks

```bash
npm run lint
npm run build
```
