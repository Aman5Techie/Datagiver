# Datagiver

A minimal shared wall website.

Users can post text, and all other users visiting the website can see it.

## Run locally

```bash
python3 app.py
```

Open:

- http://127.0.0.1:8000

## Deploy quickly (Render)

1. Push this repository to GitHub.
2. Create a new **Web Service** on Render from this repo.
3. Use:
   - **Build Command:** *(empty)*
   - **Start Command:** `python3 app.py`
   - **Environment Variable:** `HOST=0.0.0.0`
4. Deploy.

Render will provide a public URL after deployment.
