# Deploy: Cloudflare Pages + Hetzner CX23 + Cloudflare Tunnel

Web (Astro) runs on Cloudflare Pages. `/api/*` goes through a Pages Function to the Python API
on a Hetzner server, reachable only through a Cloudflare Tunnel and a shared secret header.

## 1. Cloudflare Tunnel (Zero Trust > Networks > Tunnels)
Create tunnel `mirastela-api`, copy its token. Public hostname: `api-origin.mirastela.com` → `http://localhost:8000`.

## 2. Hetzner server
CX23, Ubuntu 24.04, Nuremberg or Falkenstein, IPv4 + IPv6, SSH key optional.
Paste `deploy/cloud-init.yaml` into "Cloud config", after filling in:
Claude API key, a long random secret, the tunnel token, your GitHub username.
After ~5 minutes `https://api-origin.mirastela.com/api/health` returns `{"ok":true}`.

## 3. Cloudflare Pages
Connect the GitHub repo. Root directory `web`, build `npm run build`, output `dist`.
Variables: `API_ORIGIN=https://api-origin.mirastela.com`, `PROXY_SECRET=<same secret>`, `NODE_VERSION=22`.
Custom domain: `mirastela.com`.

## 4. Cloudflare Access (testing phase)
Zero Trust > Access > Applications > Self-hosted: `mirastela.com`, policy "Allow" with the testers' emails
(one-time PIN login). Remove when going live.

## Updates
Web: push to GitHub, Pages rebuilds. API: on the server `sudo /opt/mirastela/deploy/update.sh`
(Hetzner web console or SSH).
