# GraphQL Admin Takeover
A fully automated Python tool to exploit a GraphQL‑based admin panel via password‑reset and 2FA brute‑force, ending in an auto‑logged‑in browser session.


## Description

This script performs:

1. **Password reset** via a GraphQL `devForgotPassword` mutation.
2. **Password update** using the reset token.
3. **Login trigger** to generate a 2FA session ID.
4. **Batch OTP brute‑force** (configurable batch size and delay).
5. **Browser takeover** by dropping a small HTML file that injects the JWT into `localStorage` and redirects to the billing page.

## Installation

```bash
git clone https://github.com/kit4py/graphql-admin-takeover.git
cd graphql-admin-takeover
pip install -r requirements.txt
```

## Usage

```bash
python main.py [--url URL] [--email EMAIL] [--password PASS] [--batch-size N] [--interval SEC]
```

### Example

```bash
python main.py \
  --url http://10.0.0.1:4000/graphql \
  --email admin@example.com \
  --password NewPass123! \
  --batch-size 500 \
  --interval 3
```

### Options

* `--url`         GraphQL endpoint (default: `http://83.136.253.59:31498/graphql`)
* `--email`       Admin email address (default: `admin@speednet.htb`)
* `--password`    New admin password (default: `P@ssw0rd123!`)
* `--batch-size`  Number of OTP codes per batch (default: `500`)
* `--interval`    Seconds to wait between batches (default: `2`)

## License

MIT
