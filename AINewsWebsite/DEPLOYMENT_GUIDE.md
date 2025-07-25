# AI Intelligence Brief - Deployment Guide

This guide provides step-by-step instructions for deploying the AI Intelligence Brief website to Streamlit Cloud for permanent hosting.

## Deployment to Streamlit Cloud

### Prerequisites

1. A GitHub account
2. A Streamlit Cloud account (free tier available)

### Step 1: Create a GitHub Repository

1. Go to [GitHub](https://github.com) and sign in to your account
2. Click on the "+" icon in the top-right corner and select "New repository"
3. Name your repository (e.g., "ai-intelligence-brief")
4. Make it public or private as per your preference
5. Click "Create repository"
6. Follow the instructions to push your code to the repository:

```bash
git remote add origin https://github.com/YOUR_USERNAME/ai-intelligence-brief.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud) and sign in
2. Click on "New app" button
3. Connect your GitHub account if you haven't already
4. Select the repository you created in Step 1
5. Select the branch (main)
6. Set the main file path to "app.py"
7. Click "Deploy"

Your app will now be deployed and accessible via a URL like:
`https://YOUR_APP_NAME.streamlit.app`

### Step 3: Set Up GitHub Actions for Daily Updates

The GitHub Actions workflow is already included in the repository (.github/workflows/daily-update.yml). It will:

1. Run daily at 1:00 AM UTC
2. Generate a fresh AI news report
3. Commit and push the changes to your repository
4. Streamlit Cloud will automatically detect the changes and update your app

### Step 4: Configure GitHub Secrets (Optional)

If you need to use email functionality or other services that require credentials:

1. Go to your GitHub repository
2. Click on "Settings" > "Secrets" > "Actions"
3. Click "New repository secret"
4. Add your secrets (e.g., EMAIL_PASSWORD, API_KEYS, etc.)
5. Update the GitHub Actions workflow to use these secrets

## Alternative Deployment Options

### Deploy to Render

1. Create a free account at [Render](https://render.com)
2. Connect your GitHub repository
3. Create a new Web Service
4. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py`
5. Set up a Cron Job for daily updates

### Deploy to Heroku

1. Create a free account at [Heroku](https://heroku.com)
2. Install the Heroku CLI and login
3. Run the following commands:
   ```
   heroku create your-app-name
   git push heroku main
   ```
4. Set up a Heroku Scheduler for daily updates

## Troubleshooting

- **App not updating**: Check the GitHub Actions logs to ensure the workflow is running correctly
- **Deployment fails**: Verify that all dependencies are correctly listed in requirements.txt
- **Scraper not working**: Some websites may block scraping; check the logs and update the scraper.py file as needed

## Support

If you encounter any issues with deployment, please refer to:
- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-cloud)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Render Documentation](https://render.com/docs)
- [Heroku Documentation](https://devcenter.heroku.com/)

