# Deploy Polyglot to Vercel

## Important

**The voice agent itself cannot run on Vercel.** It needs:

- Your microphone and speakers
- Local Ollama + Piper + Whisper models

What Vercel hosts is the **project showcase website** in the `web/` folder (architecture, tech stack, setup instructions).

---

## Option A — Vercel CLI

1. Install Node.js, then:

```powershell
npm install -g vercel
cd C:\Users\utpal\polyglot
vercel login
vercel
```

2. Accept defaults. Vercel reads `vercel.json` and deploys the `web/` folder.

3. Production deploy:

```powershell
vercel --prod
```

---

## Option B — GitHub + Vercel dashboard

1. Push the repo to GitHub (see README).

2. Go to [vercel.com/new](https://vercel.com/new).

3. Import your GitHub repository.

4. Settings:
   - **Framework Preset:** Other
   - **Root Directory:** `web`  ← important (avoids `main.py` Python error)
   - **Build Command:** leave empty
   - **Output Directory:** `.` (because root is already `web`)

5. Deploy.

If you deploy from repo root instead, `vercel.json` + `.vercelignore` tell Vercel to serve only `web/` and ignore `main.py`.

### Fix: "main.py does not export app"

Vercel tried to run your CLI as a Python API. Use one of these:

- **Dashboard:** Project Settings → General → **Root Directory** = `web`
- **CLI:** deploy from `web` folder: `cd web` then `vercel --prod`
- **Repo:** ensure `.vercelignore` and updated `vercel.json` are committed, then redeploy

---

## After deploy

- Update the GitHub link in `web/index.html` (`View on GitHub` button) with your real repo URL.
- Redeploy: `vercel --prod`

---

## Local preview of the site

```powershell
cd C:\Users\utpal\polyglot\web
npx --yes serve .
```

Open the URL shown (usually http://localhost:3000).
