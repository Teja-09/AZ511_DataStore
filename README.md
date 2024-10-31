# Weather Data Archiving Project

This project fetches weather data from an API and archives it in a MySQL database. It is scheduled to run every 30 minutes using GitHub Actions. The workflow is designed to ensure that the database is updated with the latest weather data.

## Table of Contents

- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [GitHub Actions Workflow](#github-actions-workflow)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Using ngrok for Local Database Access](#using-ngrok-for-local-database-access)
- [Running the Project Locally](#running-the-project-locally)

## Project Structure

```
.
├── .gitignore
├── archieve_data.py
├── cameras.py
├── db_schema.sql
├── requirements.txt
├── weather.py
└── .github
    └── workflows
        └── archive_data.yml
```

### File Descriptions

- **archieve_data.py**: The main script that fetches weather data, processes it, and updates the MySQL database.
- **cameras.py**: (If applicable) Contains camera-related functionality or data.
- **db_schema.sql**: SQL schema file for setting up the database tables.
- **requirements.txt**: Lists the Python dependencies required for the project.
- **weather.py**: (If applicable) Contains additional functionality related to weather data.
- **.github/workflows/archive_data.yml**: GitHub Actions workflow configuration file.

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Teja-09/AZ511_DataStore.git
   cd AZ511_DataStore
   ```

2. **Set Up a Virtual Environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** in the project root directory with the following content:
   ```plaintext
   AZ511_API_KEY=your_api_key
   DB_HOST=your_db_host
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_NAME=your_db_name
   ```

5. **Set Up Your MySQL Database**:
   - Use the `db_schema.sql` file to create the necessary tables in your MySQL database.

## GitHub Actions Workflow

### Overview

The workflow is defined in the `.github/workflows/archive_data.yml` file. It runs the `archieve_data.py` script every 30 minutes.

### Workflow Configuration

```yaml
name: Archive Data

on:
  schedule:
    - cron: '*/30 * * * *'  # Runs every 30 minutes

jobs:
  run-archive-data:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12.1'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run archieve_data.py
        env:
          AZ511_API_KEY: ${{ secrets.AZ511_API_KEY }}  
          DB_HOST: ${{ secrets.DB_HOST }} 
          DB_USER: ${{ secrets.DB_USER }}  
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
          DB_NAME: ${{ secrets.DB_NAME }} 
        run: python archieve_data.py
```

### Steps Explained

- **Checkout Code**: This step retrieves the latest code from the repository.
- **Set Up Python**: Installs the specified version of Python.
- **Install Dependencies**: Upgrades pip and installs required Python packages from `requirements.txt`.
- **Run Script**: Executes the `archieve_data.py` script using the specified environment variables.

## Environment Variables

Ensure the following secrets are set in your GitHub repository:

- **AZ511_API_KEY**: Your API key for the weather data service.
- **DB_HOST**: The host address for your MySQL database (ngrok address if using ngrok).
- **DB_USER**: Your MySQL database username.
- **DB_PASSWORD**: Your MySQL database password.
- **DB_NAME**: The name of your MySQL database.

## Database Setup

1. Use the provided `db_schema.sql` file to create the necessary tables in your MySQL database.
2. Ensure your database is accessible to the GitHub Actions environment, either by hosting it on a cloud service or by tunneling with ngrok.

## Using ngrok for Local Database Access

If you are using a local MySQL database, you can expose it using ngrok. Follow these steps:

1. **Install ngrok**:
   - Download and install ngrok from the [ngrok website](https://ngrok.com/download).

2. **Start ngrok**:
   ```bash
   ngrok tcp 3306
   ```
   - This will expose your local MySQL database to the internet.

3. **Update GitHub Secrets**:
   - Update `DB_HOST` and `DB_PORT` in your GitHub repository secrets with the address provided by ngrok.

## Running the Project Locally

To test the script locally:

1. Ensure your database is running.
2. Set up your `.env` file with the correct credentials.
3. Run the script manually:
   ```bash
   python archieve_data.py
   ```

## Troubleshooting

- **Database Connection Issues**: Ensure your database is accessible and the credentials are correct.
- **API Key Errors**: Double-check your API key and ensure it is correctly set in the environment variables.
- **GitHub Actions Failures**: Check the logs in the Actions tab of your GitHub repository for detailed error messages.

## Conclusion

This README provides an overview of the setup and usage of the weather data archiving project. By following these steps, you can ensure that your project is correctly configured and can run smoothly on GitHub Actions.
