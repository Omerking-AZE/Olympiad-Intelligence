# Olympiad Intelligence — Web application

React, TypeScript and Vite frontend for the Olympiad Intelligence research project.

## Run locally

Requirements: Node.js 20.19+ or 22.12+ and npm.

```bash
cd web
npm ci
npm run dev
```

Vite serves the frontend and proxies `/api/*` to `http://127.0.0.1:8000` by default. Start the optional local report intake service in another terminal from the repository root:

```bash
python src/report_server.py
```

To proxy to another local service, set `OI_REPORT_PROXY_TARGET` before starting Vite.

For a separately hosted API, set `VITE_REPORT_API_URL` to its origin when building the frontend (for example, `https://api.example.org`). Configure `OI_REPORT_ALLOWED_ORIGINS` on the report service with the exact frontend origins, comma-separated.

## Scripts

- `npm run dev` — local development server
- `npm run build` — TypeScript project build and production bundle
- `npm run lint` — ESLint

## Demo data and limitations

The JSON files in `public/data/` are static demonstration data. They are downloaded by every visitor and must not contain private student information. The sample profile is marked `is_demo: true`.

The Python report service stores reports in a local JSON file. It is suitable only for local testing or a controlled demonstration. A public deployment should use a managed application server, durable database, authentication/abuse controls, HTTPS, and operational monitoring. Do not expose the development JSON-file service directly to the public internet.

The adaptive recommendation score is a transparent rule-based ranking using weakness priority and difficulty fit; it is not a trained recommender model.
