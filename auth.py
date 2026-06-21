import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Scope required: Read-only access to Google Drive files
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_oauth_credentials(creds_path, token_path):
    """
    Handles the Google Drive OAuth2 authentication flow.
    """
    creds = None
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception as e:
            print(f"[!] Warning: Failed to load existing token file: {e}")
            creds = None
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[*] Access token expired. Refreshing token silently...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"[!] SILENT REFRESH FAILED: {e}")
                creds = None
        
        # If refreshing failed or didn't exist, start interactive flow
        if not creds or not creds.valid:
            if not os.path.exists(creds_path):
                print("[!] Error: credentials.json not found.")
                print(f"    Please place credentials.json at: {os.path.abspath(creds_path)}")
                sys.exit(1)
            print("[*] Launching browser for Google Account authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(token_path, "w", encoding="utf-8") as token_file:
            token_file.write(creds.to_json())
            
    return creds
