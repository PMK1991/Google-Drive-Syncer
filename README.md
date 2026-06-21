# Google Drive Syncer

A lightweight, modular, and dynamic Python command-line utility to recursively and incrementally synchronize a Google Drive folder (including Shared/Team Drives) to your local machine.

## Features
*   **Incremental Downloads**: Only downloads new/missing files and folders, skipping files that are already present locally.
*   **Recursive Folder Syncing**: Automatically crawls nested folder structures on Google Drive and mirrors them locally.
*   **Shared Drive Support**: Works out of the box with standard Google Drive and Shared/Team Drives.
*   **Windows Filename Sanitization**: Strips/replaces characters that are illegal in Windows filenames (e.g. `/`, `:`, `*`, etc.) to prevent file download errors.
*   **Google Workspace Document Export**: Automatically exports Google Workspace files (Docs, Sheets, Slides) into standard Microsoft formats (`.docx`, `.xlsx`, `.pptx`).

---

## File Structure
```text
Google Drive Syncer/
├── auth.py          # Handles Google OAuth2 authentication flow
├── drive_api.py     # Wraps Google Drive API v3 listing and download queries
├── gdrive_syncer.py # main CLI script, parses arguments and loads env configs
├── sync_engine.py   # Recursive orchestrator and sync state manager
└── utils.py         # Utility functions (Windows filename sanitization)
```

---

## Prerequisites

1.  **Python 3.6+**
2.  **Install Dependencies**:
    ```bash
    pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
    ```

---

## Getting Started

1.  **OAuth Setup**:
    *   Enable the Google Drive API in your Google Cloud Console.
    *   Create OAuth 2.0 Client credentials (type: Desktop app).
    *   Download the JSON file, rename it to `credentials.json`, and place it in the same directory as this script.
2.  **Configuration (Optional)**:
    *   Create a `.env` file in the same directory as the script.
    *   Add your default Google Drive folder ID:
        ```env
        GD_FOLDER_ID="YOUR_GOOGLE_DRIVE_FOLDER_ID"
        ```

---

## Usage

Run the sync script from your terminal:

```bash
python gdrive_syncer.py [folder_id] [local_destination_directory] [--credentials path] [--token path]
```

### Parameters
*   `folder_id` *(Optional)*: Google Drive Folder ID to sync. If omitted, the script tries to load `GD_FOLDER_ID` from the local `.env` file.
*   `local_destination_directory` *(Optional)*: Absolute or relative local path to save downloaded folders. Defaults to the current working directory if not specified.
*   `--credentials` *(Optional)*: Custom path to a `credentials.json` file.
*   `--token` *(Optional)*: Custom path to a `token.json` file.

---

## License
MIT License
