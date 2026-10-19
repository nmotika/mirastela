#!/bin/bash
# One-time server hardening. Run as root: /opt/mirastela/deploy/harden.sh
# - SSH: keys only (refuses to switch off passwords unless root has an authorized key)
# - fail2ban for SSH, automatic security updates
# - ufw firewall: only SSH in (the API is reached through the Cloudflare Tunnel, which is outbound)
set -euo pipefail
apt-get update -q
DEBIAN_FRONTEND=noninteractive apt-get install -y -q fail2ban ufw unattended-upgrades rclone gnupg >/dev/null

if [ -s /root/.ssh/authorized_keys ]; then
  cat > /etc/ssh/sshd_config.d/10-mirastela.conf <<'CONF'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin prohibit-password
CONF
  sshd -t && systemctl reload ssh
  echo "SSH: key-only login on"
else
  echo "SSH: NO key in /root/.ssh/authorized_keys, password login left on. Add your public key and run again."
fi

cat > /etc/fail2ban/jail.d/sshd.local <<'CONF'
[sshd]
enabled = true
maxretry = 5
bantime = 1h
CONF
systemctl enable --now fail2ban >/dev/null && systemctl restart fail2ban

ufw default deny incoming >/dev/null
ufw default allow outgoing >/dev/null
ufw allow OpenSSH >/dev/null
ufw --force enable >/dev/null
ufw status verbose | head -8

dpkg-reconfigure -f noninteractive unattended-upgrades >/dev/null 2>&1 || true
echo "done"
