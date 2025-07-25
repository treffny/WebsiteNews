# AI Intelligence Brief

A professional AI news aggregation website that provides daily updates on artificial intelligence developments from 25+ premium sources.

## Features

- **Real-time AI News**: Fresh content scraped daily from 25+ premium sources
- **Comprehensive Coverage**: 10-15 items per section (45 total items)
- **Defense & Security Focus**: 40-50% of content focused on AI in defense and security
- **Automated Updates**: Daily updates at 1:00 AM London time
- **Email Newsletter**: Automatic delivery to specified email addresses
- **Professional Design**: Clean, modern interface with clickable news items

## Deployment Instructions

### Option 1: Deploy to Streamlit Cloud (Recommended)

1. Create a free account at [Streamlit Cloud](https://streamlit.io/cloud)
2. Connect your GitHub account
3. Create a new GitHub repository and push this code to it
4. Deploy the app from the Streamlit Cloud dashboard by selecting your repository
5. Set up a GitHub Action for daily updates (see below)

### Option 2: Deploy to Heroku

1. Create a free account at [Heroku](https://heroku.com)
2. Install the Heroku CLI and login
3. Clone this repository and navigate to it
4. Run the following commands:
   ```
   heroku create your-app-name
   git push heroku main
   ```
5. Set up a Heroku Scheduler for daily updates

### Option 3: Deploy to Render

1. Create a free account at [Render](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py`
5. Set up a Cron Job for daily updates

## Setting Up Daily Updates

### GitHub Actions (for Streamlit Cloud)

Create a file `.github/workflows/daily-update.yml` with:

```yaml
name: Daily AI News Update

on:
  schedule:
    - cron: '0 1 * * *'  # Runs at 1:00 AM UTC daily
  workflow_dispatch:  # Allows manual triggering

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run update script
        run: python generate_and_push_report.py
      - name: Commit and push changes
        run: |
          git config --global user.name 'GitHub Actions'
          git config --global user.email 'actions@github.com'
          git add daily_ai_news_report.md
          git commit -m "Daily AI News Update $(date +'%Y-%m-%d')" || echo "No changes to commit"
          git push
```

## Configuration

- **Email Settings**: Update recipient email in `generate_and_push_report.py`
- **Update Schedule**: Modify the cron schedule in your deployment platform
- **News Sources**: Add or remove sources in `scraper.py`

## Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run app.py`
4. Generate a new report: `python generate_and_push_report.py`

## License

MIT License

