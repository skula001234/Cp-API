import os
import re
import uuid
import time
import requests
import imaplib
import email
import random
from email.header import decode_header

API_URL = "https://api.classplusapp.com"

ORG_CONFIGS = [
    {"org_code": "ixgioj", "org_id": "735592"},
    {"org_code": "zgoxm", "org_id": "896887"},
    {"org_code": "wuhki", "org_id": "1681"},
    {"org_code": "wfodo", "org_id": "7845"},
]

def generate_random_mobile():
    """Generate a random Indian mobile number."""
    return random.choice(['7','8','9']) + "".join(random.choice("0123456789") for _ in range(9))

def generate_random_name():
    """Generate a random Indian name."""
    return random.choice(["Rahul", "Amit", "Priya", "Sunita", "Vikram"])

def parse_email_accounts():
    """Parse email accounts from environment variable."""
    accounts_str = os.getenv("EMAIL_ACCOUNTS", "")
    accounts = []
    for pair in accounts_str.split(','):
        if ':' in pair:
            email, password = pair.split(':', 1)
            accounts.append({"email": email.strip(), "password": password.strip()})
    return accounts

def generate_gmail_alias(base_email, suffix):
    """Generate Gmail alias using + notation."""
    local_part = base_email.split('@')[0]
    return f"{local_part}+{suffix}@gmail.com"

def fetch_otp_from_gmail(user_email, user_password, target_alias):
    """Fetch OTP from Gmail inbox."""
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(user_email, user_password)
        imap.select("INBOX")
        search_criteria = '(UNSEEN FROM "info@ce.classplus.co")'
        _, messages = imap.search(None, search_criteria)
        if not messages or not messages[0]:
            imap.close()
            imap.logout()
            return None
        
        for email_id in reversed(messages[0].split()):
            _, msg_data = imap.fetch(email_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            to_header = ''.join(p.decode(enc or 'utf-8') if isinstance(p, bytes) else p for p, enc in decode_header(msg.get("To", "")))
            if target_alias in to_header:
                body = msg.get_payload(decode=True).decode()
                otp_match = re.search(r'(\d{4})', body)
                if otp_match:
                    imap.close()
                    imap.logout()
                    return otp_match.group(1)
        imap.close()
        imap.logout()
        return None
    except Exception as e:
        return None

def send_otp_email(email, org_code, org_id):
    """Send OTP email to the specified email address."""
    headers = {"Api-Version": "51", "device-id": str(uuid.uuid4())}
    payload = {'email': email, 'orgId': org_id, 'viaEmail': '1', 'orgCode': org_code}
    try:
        res = requests.post(f"{API_URL}/v2/otp/generate", json=payload, headers=headers, timeout=10)
        if res.status_code == 200:
             return {"success": True, "data": res.json()['data'], "headers": headers}
    except Exception as e: 
        return {"success": False, "error": str(e)}
    return {"success": False, "error": f"Status {res.status_code}: {res.text}"}

def verify_otp_and_register(email, otp, session_id, org_id, headers):
    """Verify OTP and register new user."""
    payload = {
        "otp": otp, 
        "sessionId": session_id, 
        "orgId": org_id, 
        "fingerprintId": str(uuid.uuid4()),
        "name": generate_random_name(), 
        "contact": {"email": email, "mobile": generate_random_mobile()}
    }
    try:
        res = requests.post(f"{API_URL}/v2/users/register", json=payload, headers=headers, timeout=10)
        if res.status_code == 200 and 'token' in res.json().get('data', {}):
            return {"success": True, "token": res.json()['data']['token']}
    except Exception as e: 
        return {"success": False, "error": str(e)}
    return {"success": False, "error": f"Status {res.status_code}: {res.text}"}

def generate_new_token():
    """Generate a new authentication token using available email accounts."""
    accounts = parse_email_accounts()
    if not accounts: 
        return {"success": False, "error": "No email accounts configured in .env"}
    
    account = random.choice(accounts)
    base_email, password = account["email"], account["password"]
    alias = generate_gmail_alias(base_email, f"autogen{int(time.time())}")
    org = random.choice(ORG_CONFIGS)
    
    otp_res = send_otp_email(alias, org["org_code"], org["org_id"])
    if not otp_res.get("success"): 
        return otp_res
    
    time.sleep(15)
    
    otp = fetch_otp_from_gmail(base_email, password, alias)
    if not otp: 
        return {"success": False, "error": f"Could not fetch OTP from {base_email}."}
    
    verify_res = verify_otp_and_register(alias, otp, otp_res["data"]["sessionId"], org["org_id"], otp_res["headers"])
    if verify_res.get("success"):
        verify_res["email_used"] = base_email
    return verify_res
