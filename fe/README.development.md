# FE (React + Vite)

Development and build notes for the frontend.

Dev (run in two terminals):

```bash
# terminal 1: client dev server (fast HMR)
cd fe
npm run client:dev

# terminal 2: static server for APIs or to run server-side content
cd fe
npm run server:dev
```

Build for production (outputs files into `public/`):

```bash
cd fe
npm run build
```

Then serve the compiled server:

```bash
npm start
```

Tip: configure API base with `.env` (see `.env.example`) using `VITE_API_BASE` so client points to the proper API host.
