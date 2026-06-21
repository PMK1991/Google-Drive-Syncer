#!/usr/bin/env python3
import os
import sys
import argparse
from googleapiclient.discovery import build
from auth import get_oauth_credentials
from sync_engine import SyncEngine

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synchronize a Google Drive folder structure recursively and incrementally.")
    parser.add_argument("folder_id", nargs="?", help="Google Drive Folder ID to download")
    parser.add_argument("dest_dir", nargs="?", help="Local destination folder path to save items")
    parser.add_argument("--credentials", default="credentials.json", help="Path to credentials.json secret file (default: credentials.json in script dir)")
    parser.add_argument("--token", default="token.json", help="Path to token.json storage file (default: token.json in script dir)")
    
    args = parser.parse_args()
    
    # Try loading from .env if variables are present
    env_folder_id = None
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, _, value = line.partition("=")
                    if key.strip() == "GD_FOLDER_ID":
                        env_folder_id = value.strip().strip('"').strip("'")

    folder_id = args.folder_id or env_folder_id
    if not folder_id:
        print("[!] Error: Google Drive Folder ID is required.")
        print("    Specify it as the first argument, or define GD_FOLDER_ID in a local .env file.")
        parser.print_help()
        sys.exit(1)
        
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Resolve credentials and token path relative to script directory if they are default filenames
    creds_path = args.credentials
    if creds_path == "credentials.json" and not os.path.isabs(creds_path):
        creds_path = os.path.join(script_dir, "credentials.json")
        
    token_path = args.token
    if token_path == "token.json" and not os.path.isabs(token_path):
        token_path = os.path.join(script_dir, "token.json")
        
    dest_dir = args.dest_dir
    if not dest_dir:
        dest_dir = os.getcwd()
        print(f"[*] Destination folder not specified. Defaulting to current working directory: {os.path.abspath(dest_dir)}")
    else:
        dest_dir = os.path.abspath(dest_dir)
        print(f"[*] Destination folder specified: {dest_dir}")
        
    # Get credentials and initialize Google Drive client
    creds = get_oauth_credentials(creds_path, token_path)
    service = build('drive', 'v3', credentials=creds)
    
    # Run Sync Engine
    engine = SyncEngine(service)
    engine.sync(folder_id, dest_dir)
