# Deploying to Google Cloud Run

This guide will walk you through the steps to deploy your FastAPI application to Google Cloud Run for free, with continuous deployment using GitHub Actions.

## Step 1: Set up your Google Cloud Project

1.  **Create a Google Cloud Project**: If you don't have one already, go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project. You will get a unique **Project ID**.
2.  **Enable APIs**: In your new project, enable the following APIs:
    *   Cloud Run API
    *   Artifact Registry API
    *   Cloud Build API
3.  **Create an Artifact Registry Repository**: This is where your Docker images will be stored.
    *   Go to Artifact Registry in the console.
    *   Click "Create Repository".
    *   Choose a name (e.g., `loomer-repo`), select "Docker" as the format, and choose a region (e.g., `us-central1`).
4.  **Create a Service Account**: This is a special account that GitHub Actions will use to authenticate with Google Cloud.
    *   Go to "IAM & Admin" -> "Service Accounts".
    *   Click "Create Service Account".
    *   Give it a name (e.g., `github-actions-deployer`).
    *   Grant it the following roles:
        *   `Cloud Run Admin`
        *   `Artifact Registry Writer`
        *   `Service Account User`
    *   After creating the service account, click on it, go to the "Keys" tab, click "Add Key" -> "Create new key", and choose "JSON". A JSON key file will be downloaded. **Keep this file secure!**

## Step 2: Set up your GitHub Repository Secrets

In your GitHub repository, go to "Settings" -> "Secrets and variables" -> "Actions" and add the following secrets:

*   `GCP_PROJECT_ID`: Your Google Cloud Project ID.
*   `GCP_SA_KEY`: The entire JSON content of the service account key file you downloaded.
*   `MONGODB_URI`: Your MongoDB connection string.
*   `GEMINI_API_KEY`: Your API key for the Gemini model.

## Step 3: Push to `main`

The GitHub Actions workflow is configured to trigger a new deployment every time you push a commit to the `main` branch.

Once you push, you can go to the "Actions" tab in your GitHub repository to watch the deployment process. If everything is configured correctly, your API will be live on Google Cloud Run within a few minutes!

You can find the public URL for your service in the Cloud Run section of the Google Cloud Console.