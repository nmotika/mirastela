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

## Production hardening (once)
1. **Firewall, fail2ban, SSH keys:** `sudo /opt/mirastela/deploy/harden.sh`. Password login is switched off only
   if `/root/.ssh/authorized_keys` has a key; otherwise the script says so and leaves it on.
2. **Backups:** the timer `mirastela-backup` runs `deploy/backup.sh` every night at 03:30 (7 local copies in
   `/var/backups/mirastela`). For the offsite copy use the Cloudflare R2 bucket `mirastela-backup` (EU jurisdiction, hence the `.eu.` endpoint) and an
   R2 API token (Object Read & Write, that bucket only), then write `/etc/mirastela-backup.env` (chmod 600):
   ```
   BACKUP_PASSPHRASE=<long random passphrase, also keep it in your password manager>
   R2_BUCKET=mirastela-backup
   RCLONE_CONFIG_R2_TYPE=s3
   RCLONE_CONFIG_R2_PROVIDER=Cloudflare
   RCLONE_CONFIG_R2_ACCESS_KEY_ID=<key id>
   RCLONE_CONFIG_R2_SECRET_ACCESS_KEY=<secret>
   RCLONE_CONFIG_R2_ENDPOINT=https://8447929ad03d3df3bfc8b452650aca37.eu.r2.cloudflarestorage.com
   ```
   Test: `systemctl start mirastela-backup && journalctl -u mirastela-backup -n 20`, then `deploy/restore-test.sh`.
3. **Uptime monitoring:** UptimeRobot (free), HTTP monitors every 5 minutes with email alerts on
   `https://api-origin.mirastela.com/api/health` (API and tunnel) and `https://mirastela.com/pl/` (site).
4. **Turnstile:** Cloudflare > Turnstile > add widget for `mirastela.com` (Managed). Site key goes into
   `web/src/i18n/config.ts` (TURNSTILE_SITEKEY), secret into `/etc/mirastela.env` as `TURNSTILE_SECRET`.

## Data requests (GDPR)
Customers can download or delete their data themselves on `/{lang}/account/`. By hand:
`/opt/mirastela/deploy/data.sh export someone@example.com > someone.json` or `... delete someone@example.com`.

## Coupons
`MIRASTELA_COUPONS` in `/etc/mirastela.env`, comma separated, then `update.sh`:
`MIRASTELA_COUPONS=MS-FREE-K7Q2,MIRA50:50,ANA15:15`
- `CODE` alone: free access (all reports and the subscription of that order).
- `CODE:NN`: NN % off the report and every add-on bought for that order; the subscription stays full price.
An empty value (`MIRASTELA_COUPONS=`) switches all codes off. Without the line the old test code MIRATEST works.
