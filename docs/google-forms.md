# Google Forms Integration

This document explains how to set up and use the Google Forms integration feature in this Django application.

## Overview

The application can fetch and display responses from Google Forms using Google's official Forms API. The integration uses service account authentication for server-side access and includes simple in-memory caching to reduce API calls.

## Prerequisites

1. **Google Cloud Project**: You need a Google Cloud project with billing enabled
2. **Google Form**: A Google Form with responses you want to access
3. **Service Account**: A service account with appropriate permissions

## Setup Instructions

### 1. Create a Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project or create a new one
3. Navigate to **IAM & Admin** → **Service Accounts**
4. Click **Create Service Account**
5. Enter a name (e.g., "forms-reader") and description
6. Click **Create and Continue**
7. Skip adding roles for now (we'll add permissions later)
8. Click **Done**

### 2. Enable Required APIs

In your Google Cloud project, enable these APIs:

1. **Google Forms API**
   - Go to **APIs & Services** → **Library**
   - Search for "Google Forms API"
   - Click **Enable**

2. **Google Drive API** (required for form access)
   - Search for "Google Drive API"
   - Click **Enable**

### 3. Create and Download Service Account Key

1. Go to **IAM & Admin** → **Service Accounts**
2. Find your service account and click on it
3. Go to the **Keys** tab
4. Click **Add Key** → **Create new key**
5. Select **JSON** as the key type
6. Click **Create**
7. Download the JSON file and save it securely (e.g., `service-account.json`)

### 4. Share the Google Form

The service account needs permission to access the form:

1. Open your Google Form
2. Click **Share** (top right)
3. Under "General access", add the service account email:
   - Find the email in your service account details (looks like `your-service-account@your-project.iam.gserviceaccount.com`)
   - Add it as a **Viewer**
4. Click **Send**

### 5. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual values:
   ```env
   # Path to your service account JSON file
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account.json
   
   # Your Google Form ID (from the form URL)
   GOOGLE_FORM_ID=your-form-id-here
   
   # Cache TTL in seconds (optional, defaults to 60)
   FORMS_CACHE_SECONDS=60
   ```

### 6. Find Your Form ID

Your Form ID is in the Google Form URL:
```
https://docs.google.com/forms/d/FORM_ID/edit
```

Copy the `FORM_ID` part and add it to your `.env` file.

## Installation and Running

### 1. Install Dependencies

```bash
poetry install
```

### 2. Run the Development Server

```bash
poetry run python src/manage.py runserver
```

### 3. Access the Form Responses

Visit `http://localhost:8000/forms/responses/` to see the form responses.

## Features

- **Read-only Access**: Only fetches responses, doesn't modify anything
- **Automatic Caching**: Responses are cached for 60 seconds by default (configurable)
- **Multiple Answer Types**: Handles text, multiple choice, checkbox, date/time, and file upload answers
- **Error Handling**: Graceful error messages for configuration or permission issues
- **Dynamic Columns**: Automatically adjusts to your form's question structure

## Troubleshooting

### Common Issues

1. **"Google credentials file not found"**
   - Check that `GOOGLE_APPLICATION_CREDENTIALS` in `.env` points to the correct file path
   - Ensure the JSON file exists and is readable

2. **"Permission denied" errors**
   - Verify the service account email has been added to the form with Viewer permissions
   - Check that both Google Forms API and Google Drive API are enabled

3. **"No form responses available"**
   - Ensure the form has actual responses
   - Verify the Form ID is correct
   - Check the service account has proper permissions

4. **API errors**
   - Check that all required APIs are enabled in Google Cloud Console
   - Verify your service account has the correct scopes

### Debugging

The application logs errors to the console. Check the Django development server output for detailed error messages.

## Security Notes

- **Never commit** your service account JSON file to version control
- Keep your `.env` file out of version control (it's already in `.gitignore`)
- The service account only needs read permissions (Viewer role)
- Consider using environment-specific configurations for production

## API Limits

Google Forms API has usage limits:
- Read requests: 100 per minute per project
- The built-in caching helps stay within these limits

## Support

For issues related to:
- **Google Cloud setup**: Refer to Google Cloud documentation
- **Google Forms API**: Check the [Google Forms API documentation](https://developers.google.com/forms)
- **Application bugs**: Check Django logs and create an issue in the project repository
