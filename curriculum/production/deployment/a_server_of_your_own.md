<div class="lesson-note" markdown="1">

#### This lesson is optional

You can skip this lesson. No later lesson depends on it, and Project: Hello, Production only offers it as extra credit. Read it if you want to understand what Render and Cloud Run do for you behind the scenes, if you want a cheap home for an always-on app, or if job postings you care about mention Linux and SSH. Plenty of them do.

</div>

### Introduction

So far a platform has always run your app for you. Render built your image and handed you an HTTPS address, and Cloud Run did the same with more knobs. Under both of them sits an ordinary Linux computer that somebody else set up, secured, patched and watched. In this lesson you'll be that somebody, once. You'll rent (or simulate) a **VPS**, a "virtual private server": a small virtual machine in a data center that you control completely. You'll log in with SSH, lock it down, keep your app running with systemd or Docker Compose, put Caddy in front of it for automatic HTTPS, and set up updates and backups.

Doing it by hand once pays off even if you never run a server in production. You'll understand what a "managed" platform manages, you'll be comfortable when a job asks you to SSH into a box to read logs, and you'll be able to judge honestly when a $5 server is the right answer and when it's a trap.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Free and cheap ways to get a Linux server, including one on your own laptop.
- Logging in with SSH keys, and turning off password logins.
- Working as a normal user with `sudo` instead of as root.
- A firewall that lets in only SSH and web traffic, and the Docker trap that gets around it.
- Keeping your app running with Docker Compose restart policies or a systemd service.
- Caddy as a reverse proxy with automatic HTTPS.
- Deploys, security updates, backups, and the honest trade-offs against managed platforms.

### Getting a server

You need a machine running **Ubuntu Server 24.04 LTS** (LTS means "long-term support": five years of security updates). Three routes, from free to a few dollars a month:

- **A virtual machine on your laptop.** [Multipass](https://canonical.com/multipass) is a free tool from Canonical, the company behind Ubuntu, that starts an Ubuntu VM with one command and needs no account: `multipass launch 24.04 --name mimir --cpus 2 --memory 2G --disk 15G`. You can practice every step in this lesson except a real public certificate, because nobody on the internet can reach your laptop. Start here if you don't want to sign up for anything.
- **Google Cloud's free e2-micro.** You already have a Google Cloud project from One Real Cloud. Its free tier includes one small e2-micro VM a month in `us-central1`, `us-west1` or `us-east1`, with a 30 GB standard disk. Read the fine print, though: the VM is free, but its public IPv4 address isn't. It costs about half a cent an hour, roughly $3.60 a month, which your trial credit covers while it lasts. The e2-micro also has only 1 GB of memory, which is tight for Docker, Postgres and Python together. It's fine for a demo; don't build your image on it.
- **A paid VPS.** Providers such as Hetzner, DigitalOcean, Vultr and Linode sell small servers that usually cost a few dollars a month, billed by the hour, so a weekend experiment costs cents. Pick the smallest plan with at least 1 GB of memory (2 GB is more comfortable) and Ubuntu 24.04. Oracle Cloud's Always Free tier includes small VMs too, but sign-up needs a card and popular regions often run out of free capacity.

Whichever you choose, write down the server's public IP address. This lesson uses `203.0.113.10`, an address reserved for examples; replace it with yours.

### SSH keys and your first login

**SSH** ("secure shell") gives you an encrypted terminal on another computer. You set up an SSH key for GitHub in Git Basics, and a server works the same way: you keep the **private key**, the server holds your **public key** in a file called `~/.ssh/authorized_keys`, and logging in proves you own the private key without sending it anywhere. Make a separate key for servers, so you can revoke it without touching GitHub:

```bash
# On your laptop. Press Enter for the default answers, and set a passphrase.
ssh-keygen -t ed25519 -C "mimir-server" -f ~/.ssh/mimir_server
cat ~/.ssh/mimir_server.pub      # the PUBLIC half: this is what you paste into the provider
```

When you create the server, paste that public key into the provider's "SSH keys" box. (On Multipass, run `multipass shell mimir` and append it to `~/.ssh/authorized_keys` yourself.) Then log in. Depending on the provider, the first user is `root` or a default user such as `ubuntu`:

```bash
ssh -i ~/.ssh/mimir_server root@203.0.113.10
```

The first time, SSH shows the server's **fingerprint** and asks whether to trust it. Say yes, and SSH remembers it in `~/.ssh/known_hosts`. If that fingerprint ever changes without a reason (you didn't rebuild the server), something is wrong, and SSH will refuse to connect. Don't just delete the line to make the warning go away.

### A user that isn't root

**root** is Linux's all-powerful administrator account. A typo as root can delete the whole system, and an attacker who gets in as root owns everything. So the first job on a new server is to create a normal user who can borrow root's powers on purpose, one command at a time, with `sudo`:

```bash
# On the server, as root. If you logged in as ubuntu, run sudo -i first to become root.
adduser deploy                                   # asks for a password: sudo uses it, SSH won't
usermod -aG sudo deploy                          # members of the sudo group may use sudo
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/     # the same public key logs you in as deploy
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh && chmod 600 /home/deploy/.ssh/authorized_keys

# Turn off password and root logins. Files in sshd_config.d are read in name order,
# and the first value wins, so a 10- file beats a provider's 50-cloud-init.conf.
printf 'PasswordAuthentication no\nKbdInteractiveAuthentication no\nPermitRootLogin no\n' \
  > /etc/ssh/sshd_config.d/10-hardening.conf
sshd -t && systemctl restart ssh                 # sshd -t checks the config before restarting
```

**Keep this terminal open.** In a second terminal, check that `ssh -i ~/.ssh/mimir_server deploy@203.0.113.10` works and that `sudo whoami` prints `root`. Only then close the first one. If you broke something, the open session is how you fix it. Most providers also have a web console for when you lock yourself out completely.

Why bother turning off passwords? A server with a public IP gets thousands of password guesses a day from bots. With key-only login, every guess fails, however weak a password is. Finally, save typing with an entry in `~/.ssh/config` on your laptop, so `ssh mimir` is enough from now on:

```text
Host mimir
    HostName 203.0.113.10
    User deploy
    IdentityFile ~/.ssh/mimir_server
```

### A firewall

A **firewall** decides which network connections may reach the machine. Your server needs exactly three open ports: 22 for SSH, 80 for plain HTTP (Caddy uses it to get certificates and to redirect visitors to HTTPS) and 443 for HTTPS. Ubuntu ships **ufw**, the "uncomplicated firewall":

```bash
sudo ufw default deny incoming     # block everything coming in...
sudo ufw default allow outgoing    # ...but let the server call out (apt, Docker Hub, the model API)
sudo ufw allow OpenSSH             # allow SSH BEFORE enabling, or you lock yourself out
sudo ufw allow 80,443/tcp
sudo ufw enable
sudo ufw status verbose
```

Many clouds also have a firewall outside the VM. On Google Cloud it's a VPC firewall rule, and the VM creation page has "Allow HTTP traffic" and "Allow HTTPS traffic" boxes for ports 80 and 443. A connection has to get through both.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Docker walks around ufw

When Docker publishes a port, such as `ports: - "8000:8000"`, it writes its own network rules, and those are checked before ufw's. Your app would be reachable from the whole internet on port 8000, over plain HTTP, even though `ufw status` doesn't list it. The fix is to publish only on the server's loopback address, `127.0.0.1:8000:8000`, so only programs on the same machine, such as Caddy, can reach it. Never publish Postgres or Redis ports on a server at all.

</div>

### Running your app so it stays running

On your laptop, you start the app and stop it when you're done. On a server, nobody is watching. It has to start when the machine boots, come back when it crashes, and keep its logs somewhere you can read them. On Linux, the program that does all of this is **systemd**. It's the first process the system starts, and it starts and supervises everything else as **services** (also called **units**). Docker itself is a systemd service, and so is the SSH server you just restarted.

The simplest route reuses what you already have. Install Docker by following [Docker's Ubuntu install guide](https://docs.docker.com/engine/install/ubuntu/), and add yourself to the `docker` group with `sudo usermod -aG docker deploy` (log out and back in afterward). Be aware that the `docker` group is as powerful as root, so only trusted users belong in it. Then clone your repository into `~/app` and add a production Compose file next to your `compose.yaml`:

```yaml
# compose.prod.yaml: the same app as compose.yaml, set up to run unattended on a server
services:
  api:
    build: .
    image: mimir-api:${APP_VERSION:-dev}   # tag each build with its commit, for rollbacks
    restart: unless-stopped                # restart on crashes and reboots, unless you stopped it
    env_file: .env                         # lives only on the server, chmod 600, never in Git
    environment:
      APP_VERSION: ${APP_VERSION:-dev}
      DATABASE_URL: postgresql+psycopg://mimir:${POSTGRES_PASSWORD}@db:5432/mimir
    command: ["/bin/sh", "-c", "alembic upgrade head && exec fastapi run main.py --host 0.0.0.0 --port 8000"]
    ports:
      - "127.0.0.1:8000:8000"              # only Caddy, on this machine, can reach the app
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:17
    restart: unless-stopped
    environment:
      POSTGRES_USER: mimir
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}   # Compose reads it from .env
      POSTGRES_DB: mimir
    volumes:
      - pgdata:/var/lib/postgresql/data         # no ports: the database never leaves the machine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mimir -d mimir"]
      interval: 2s
      retries: 15

volumes:
  pgdata:
```

Create `.env` on the server with your model key and a long random `POSTGRES_PASSWORD` (`openssl rand -hex 24` makes one), run `chmod 600 .env` so only `deploy` can read it, and start everything with `docker compose -f compose.prod.yaml up -d --build`. The `-d` flag runs it in the background. A **restart policy** tells Docker what to do when a container stops: `unless-stopped` restarts it after a crash and after a reboot (because the Docker service starts at boot), but leaves it alone if you stopped it yourself. Here's a real bonus: the background worker and Redis from Job Queues and Workers, which cost extra on Render, are just two more services in this file, at no extra cost.

The other route is to let systemd run your app directly, without Docker. This suits a small Python service, such as a bot, that doesn't need a container. You describe the service in a **unit file**:

```ini
# /etc/systemd/system/mimir-api.service
[Unit]
Description=Mimir API
After=network-online.target
Wants=network-online.target

[Service]
User=deploy
WorkingDirectory=/home/deploy/app
EnvironmentFile=/home/deploy/app/.env
ExecStart=/home/deploy/.local/bin/uv run --frozen --no-dev fastapi run main.py --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

`ExecStart` is the command to run, as an absolute path, since systemd doesn't use your shell's `PATH`. `Restart=on-failure` brings the app back five seconds after a crash, and `WantedBy=multi-user.target` means "start this at boot." Load and start it with `sudo systemctl daemon-reload` and `sudo systemctl enable --now mimir-api`. Then `systemctl status mimir-api` shows whether it's running, and `journalctl -u mimir-api -f` follows its logs, which systemd collects from standard output just as Cloud Run does. With Compose, the equivalent is `docker compose -f compose.prod.yaml logs -f api`.

Either way, test the claim: run `sudo reboot`, wait a minute, SSH back in, and check that the app came back on its own.

### Caddy and automatic HTTPS

Your app now listens on `127.0.0.1:8000`, invisible from outside. A **reverse proxy** is a server that sits in front of it, accepts connections from the internet on ports 80 and 443, and passes each request on to your app. It's the right place to handle HTTPS, compression and, later, several apps on one machine. **Caddy** is a reverse proxy that gets and renews HTTPS certificates by itself, from Let's Encrypt, a free certificate authority. Install it with the Ubuntu commands on [Caddy's install page](https://caddyserver.com/docs/install). The package sets Caddy up as a systemd service, so it starts at boot too.

A certificate is issued for a **domain name**, not an IP address, so you need a name that points to your server. If you own a domain, add an `A` record pointing at your IP. If you don't, **sslip.io** is a free service that needs no sign-up: any name with an IP inside it, such as `203-0-113-10.sslip.io`, points to that IP. Then the whole configuration is three lines:

```text
# /etc/caddy/Caddyfile
203-0-113-10.sslip.io {
    reverse_proxy localhost:8000
}
```

Run `sudo systemctl reload caddy`. Within a few seconds Caddy proves to Let's Encrypt that it controls the name (that's why port 80 must be open), saves the certificate, redirects HTTP to HTTPS and starts serving `https://203-0-113-10.sslip.io`. It renews the certificate before it expires, about every two months, with no action from you. If it fails, `journalctl -u caddy` says why, almost always a closed port or a name that doesn't point at the server yet.

On a Multipass VM, Let's Encrypt can't reach you, so use the VM's IP from `multipass list` in the name and add a `tls internal` line inside the block. Caddy then signs its own certificate, and your browser warns about it, which is fine for practice.

### Deploys, updates and backups

On Cloud Run, a release was a script and a rollback was one command. Here you build both yourself. A small script on your laptop can deploy the latest pushed commit:

```bash
#!/usr/bin/env bash
# deploy.sh: ship the latest commit on main to the server, then smoke test it.
set -euo pipefail
ssh mimir 'set -euo pipefail
  cd ~/app && git pull --ff-only
  export APP_VERSION=$(git rev-parse --short HEAD)
  docker compose -f compose.prod.yaml up -d --build
  docker image prune -f'                       # removes untagged leftovers; tagged images stay
uv run python smoke.py https://203-0-113-10.sslip.io
```

Because each image is tagged with its commit, a rollback is `APP_VERSION=3f9c2ab docker compose -f compose.prod.yaml up -d --no-build` on the server, using the old tag. Two honest limits: the app is down for a few seconds while Compose replaces the container, and a rollback doesn't undo a migration, exactly as on Cloud Run.

**Security updates** are now your job too. Ubuntu Server installs security updates automatically through **unattended-upgrades**, which is switched on by default; check with `systemctl status unattended-upgrades`. Some updates, such as a new kernel, take effect only after a reboot, and the file `/var/run/reboot-required` appears when one is waiting. Reboot during a quiet moment; your restart policies bring everything back. Your images need patching too: every few weeks, rebuild with `docker compose -f compose.prod.yaml build --pull` so you pick up the base image's fixes.

**Backups** matter most, because the database lives on this one disk. A nightly dump is a few lines. **cron** is Linux's built-in scheduler: run `crontab -e` and add a line such as `15 3 * * * /home/deploy/app/backup.sh`, meaning "every day at 03:15":

```bash
#!/usr/bin/env bash
# backup.sh: dump the database, keep two weeks of dumps.
set -euo pipefail
mkdir -p ~/backups && cd ~/app
docker compose -f compose.prod.yaml exec -T db pg_dump -U mimir -Fc mimir > ~/backups/mimir-$(date +%F).dump
find ~/backups -name 'mimir-*.dump' -mtime +14 -delete
```

A backup on the same disk isn't a backup: if the server dies, it dies with it. Copy the dumps somewhere else, for example by running `scp "mimir:backups/*.dump" ./backups/` from your laptop, or by sending them to object storage. Many providers also sell whole-disk snapshots for a small fee. And a backup you've never restored is a hope, not a backup; [Managed Postgres and Backups](#/lessons/production/managed-postgres-and-backups), the next section, walks you through a real restore drill.

### The honest trade-offs

| | Your own server | Cloud Run | Render (free) |
| --- | --- | --- | --- |
| Cost | Flat: a few dollars a month, or the free e2-micro plus its IP | Free tier, then pay per use | $0, with limits |
| When idle | Always running, no cold starts | Scales to zero, cold starts | Sleeps after 15 minutes |
| Scaling | One machine; resize by hand | Automatic | Pick a bigger plan |
| OS patches and security | You | Google | Render |
| HTTPS | Caddy, which you run | Built in | Built in |
| Database and backups | Yours to run, back up and restore | Managed, or external | Managed, but the free one expires |
| If the machine dies | Your app is down until you rebuild it | Another instance starts | Another instance starts |

A server of your own wins when your load is steady and always on, when you need things a request-based platform handles badly (long-running background jobs, WebSockets, Redis, a self-hosted tracing tool such as Langfuse), and when a flat, predictable bill matters more than your time. It loses when traffic is spiky or zero most of the day, when nobody has time to patch it, and when the app must stay up if one machine fails. The real cost isn't the few dollars; it's the hours. Every task in this lesson is something a managed platform does while you sleep. That's why the main path of this curriculum uses Cloud Run, and why it's still worth knowing what's underneath.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read DigitalOcean's [Initial Server Setup with Ubuntu](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu), a careful walkthrough of the user, SSH and firewall steps in this lesson, with explanations of what each command does. It works on any provider, not just DigitalOcean.
1. Read Docker's [Packet filtering and firewalls](https://docs.docker.com/engine/network/packet-filtering-firewalls/) page, so you understand why Docker's published ports get past ufw.
   - Read the sections on port publishing and on Docker and ufw. Skim the rest.
1. Read Caddy's [reverse proxy quick-start](https://caddyserver.com/docs/quick-starts/reverse-proxy) and [Automatic HTTPS](https://caddyserver.com/docs/automatic-https).
   - From the second page, read the overview and the requirements for public certificates: those are the conditions to check when a certificate won't issue.
1. Skim Ubuntu's [Automatic updates](https://documentation.ubuntu.com/server/how-to/software/automatic-updates/) page and Docker's [Start containers automatically](https://docs.docker.com/engine/containers/start-containers-automatically/) page, which lists every restart policy and how they differ.
1. Practice: run your LLM-Powered API on a server of your own.
   - Use a Multipass VM if you want zero cost and no sign-up, or a free e2-micro or cheap VPS for a public URL.
   - Create the `deploy` user, log in with your key, and show that `ssh root@...` and password logins are refused.
   - Turn on ufw with only SSH, 80 and 443 open. From your laptop, show that port 8000 is not reachable, then show what happens if you publish it as `8000:8000` instead (and change it back).
   - Run the app with `compose.prod.yaml` behind Caddy, and run `smoke.py` against the HTTPS URL. Reboot and run it again.
   - Run `backup.sh`, copy the dump to your laptop, and write down in your README what it would take to rebuild this server from nothing.
   - When you're done, delete a paid or cloud server so it stops billing, and release its IP address.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What does the free e2-micro cost you, and where can you practice for free with no sign-up at all?](#getting-a-server)
- [Which half of an SSH key goes on the server, and what should you do if a server's fingerprint changes unexpectedly?](#ssh-keys-and-your-first-login)
- [Why work as a normal user with sudo, and why keep one session open while you change the SSH settings?](#a-user-that-isn-t-root)
- [Which ports does the firewall open, and why should a Docker port be published on 127.0.0.1?](#a-firewall)
- [What does systemd do, and what does the unless-stopped restart policy do after a crash, a reboot and a manual stop?](#running-your-app-so-it-stays-running)
- [What does a reverse proxy do, and what does Caddy need before it can get a certificate?](#caddy-and-automatic-https)
- [Why isn't a nightly dump on the server's own disk a real backup?](#deploys-updates-and-backups)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The systemd.service manual](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html) documents every option in a unit file, including all the `Restart=` choices.
- [The ArchWiki's systemd page](https://wiki.archlinux.org/title/Systemd) is a practical guide to units, `systemctl` and `journalctl` that applies to any Linux distribution, not just Arch.
- [Ubuntu's firewall guide](https://documentation.ubuntu.com/server/how-to/security/firewalls/) covers ufw in more depth, including rate-limiting SSH and application profiles.
- [Caddy's reverse_proxy directive](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy) explains load balancing, health checks and headers for when one backend becomes several.
- [Let's Encrypt's rate limits](https://letsencrypt.org/docs/rate-limits/) explain why repeatedly rebuilding a server and asking for a fresh certificate can get you blocked for a while.
- [Google Cloud's Free Tier page](https://cloud.google.com/free/docs/free-cloud-features) has the exact e2-micro terms, and [DuckDNS](https://www.duckdns.org/) is a free alternative to sslip.io that gives you a name that stays the same when your IP changes.

