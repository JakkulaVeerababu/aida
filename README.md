# AI Universal Data Analysis — Deployment

This repository contains a Streamlit application. I prepared automated container builds so you can get a deployable Docker image right away.

What I added for deployment:

- `Dockerfile` — builds a container image that runs the Streamlit app.
- `.github/workflows/docker-publish.yml` — GitHub Actions workflow that builds & pushes the image to GitHub Container Registry (GHCR) on each push to `main`.

How to get a public URL (pick one):

1) Quick: Deploy on Render (recommended for heavy Python packages)

- Visit https://render.com and create an account (GitHub sign-in supported).
- New → Web Service → Connect your GitHub repo `JakkulaVeerababu/AI-UNIVERSAL-DATA-ANALYSIS`.
- For the service you can either:
  - Deploy directly from the repo (Render will build from `Dockerfile`), or
  - Use the published GHCR image: `ghcr.io/<your-github-username>/ai-universal-data-analysis:latest`
- Start command (if not using Docker):
```
streamlit run app.py --server.port $PORT --server.enableCORS false
```

2) Streamlit Community Cloud (easiest but may struggle for heavy packages like `pycaret`)

- Go to https://streamlit.io/cloud → New app → select this repo, branch `main`, main file `app.py`.
- Make sure `requirements.txt` includes all dependencies (it does now).

Notes:
- The GHCR image is published automatically by GitHub Actions when you push to `main`. The image URL will be:

```
ghcr.io/<your-github-username>/ai-universal-data-analysis:latest
```

- After Render creates a service you will get a public URL (Render assigns one automatically).

If you want, I can:
- Create the Render service for you if you provide a Render API key, or
- Walk you through the Streamlit Cloud one-click deploy (you can click and it's done).
# AI-UNIVERSAL-DATA-ANALYSIS