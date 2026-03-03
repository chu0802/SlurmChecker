# Shiba Alert 🤖

> 🚨 **DISCLAIMER:** This project was created entirely through "vibe coding" (using AI assistance). Please be aware that it allows a bot to directly interact with and execute commands on remote servers, which may pose potential safety and security risks. Use with caution and review the code before deployment.

A powerful Slackbot for monitoring and managing Slurm jobs across multiple remote servers. Built with FastAPI and designed to keep you updated on your experiment's status and accuracy metrics directly within Slack.

## 🚀 Features

- **Job Monitoring**: Real-time tracking of Slurm jobs.
  - Detects status changes (e.g., Pending `PD` ➡️ Running `R`).
  - Parses logs for experiment accuracy/metrics (via `/show`).
- **Slack Commands**: A comprehensive suite of commands to interact with your Slurm clusters.
- **Multi-Server Support**: Manage jobs across different computing clusters.
- **Code Sync**: Synchronize project code across all servers with a single command (`/sync`).
- **Notifications**: Get alerted in a specific channel when job status changes or new results are available.
- **Easy Deployment**: Dockerized setup with Cloudflare Tunnel integration.

## 🛠 Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `/sq` | `/sq <server>` | Runs `squeue` to show current job queue. |
| `/share` | `/share <server>` | Runs `sshare` to show fairshare usage. |
| `/show` | `/show <server> <job_id>` | Fetches the last 20 lines of the job's output log. |
| `/bind` | `/bind <server> [job_id...]` | Start monitoring specific jobs. If no ID provided, binds **all** your running jobs. |
| `/unbind` | `/unbind <server> [job_id...]` | Stop monitoring specific jobs. If no ID provided, unbinds **all** monitored jobs for that server. |
| `/lsbind` | `/lsbind` | Lists all jobs currently being monitored and their status. |
| `/scancel` | `/scancel <server> <job_id>` | Cancels a running job. |
| `/sync` | `/sync [project_name]` | Runs `git pull` in `~/scratch/<project_name>` on all configured `SSH_SERVERS`. Defaults to `semantic_selector`. |
| `/run` | `/run [servers] <args...>` | Runs `python -m script.build_script <args> && sbatch inference.sh` on specified or all servers. |
| `/lsconfig` | `/lsconfig` | Show current configuration by running `python -m script.show_config` on the first server. |

## ⚙️ Configuration

### Prerequisites
1. **Docker & Docker Compose** installed.
2. **SSH Access** to your target Slurm servers configured with ControlMaster sockets (for persistent connections).

### Environment Variables (.env)
Create a `.env` file in the root directory:

```ini
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_LOG_CHANNEL_ID=C0123456789  # Channel ID for notifications

# SSH Configuration
SSH_HOST=compute.example.com     # Domain suffix for servers
SSH_USER=your_username
SSH_SERVERS=server1,server2,server3 # Comma-separated list of servers for /sync

# Cloudflare Tunnel
TUNNEL_TOKEN=your-cloudflare-tunnel-token

# Slurm Commands Customization
SLURM_CMD_SQUEUE=squeue
SLURM_CMD_FULL_SQUEUE=squeue -o "%.18i %.9P %.8j %.8u %.2t %.10M %.6D %R"
SLURM_CMD_SSHARE=sshare -U
```

### SSH Setup
The bot relies on existing SSH sockets mounted from the host machine. Ensure you have `~/.ssh/sockets` directory and your SSH config is set up to use ControlPath.

Host `~/.ssh/config` example:
```ssh
Host *
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%r@%h:%p
    ControlPersist 600
```

### Git Sync Configuration
For `/sync` to work, each remote server must have a private key for GitHub access located at `~/.ssh/<server_name>`. The bot will automatically use this key when running `git pull`.

## 🐳 Deployment

1. **Build and Run**:
   ```bash
   docker-compose up -d --build
   ```

2. **Verify**:
   The bot service runs on port `8000` and is exposed via Cloudflare Tunnel.

## 📁 Project Structure

```
├── main.py                # FastAPI entry point & command dispatcher
├── docker-compose.yml     # Docker services (Bot + Cloudflare Tunnel)
├── requirements.txt       # Python dependencies
├── src/
│   ├── config.py          # Settings and env var loading
│   ├── monitor.py         # Job monitoring logic (background thread)
│   ├── ssh_client.py      # SSH execution wrapper
│   └── command/           # Command handlers
│       ├── base.py        # Abstract base class for commands
│       ├── bind_unbind.py # /bind and /unbind logic
│       ├── scancel.py     # /scancel logic
│       └── ...
```

## 🛡 Security
- **Slack Signature Verification**: Ensures requests actually come from Slack (`src/security.py`).
- **SSH Isolation**: Runs inside a container, utilizing mounted sockets for authentication without storing private keys inside the image.

## 📝 License
[MIT](LICENSE)
