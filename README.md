# GitHub Repository Contribution Analyzer

A Python tool that analyzes developer contributions in GitHub repositories. This tool provides detailed statistics about commits, code changes, and developer activity over a specified time period.

## Features

- Analyzes commits, additions, deletions, and file changes
- Tracks developer activity patterns and contributions
- Calculates code churn and average commits per active day
- Supports analysis of specific branches
- Provides detailed commit history for each developer
- Outputs results in a convenient DataFrame format

## Requirements

- Python 3.x
- Required Python packages:
  ```
  PyGithub
  pandas
  python-dotenv
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/houmairi/GitHub_Contributions
   cd github-contributions
   ```

2. Install required packages:
   ```bash
   pip install PyGithub pandas python-dotenv
   ```

3. Create a `.env` file in the project root and add your GitHub access token:
   ```
   GITHUB_ACCESS_TOKEN="your_github_token_here"
   ```

   To create a GitHub access token:
   1. Go to GitHub Settings > Developer settings > Personal access tokens
   2. Generate a new token with 'repo' access
   3. Copy the token and paste it in your `.env` file

## Usage

1. Configure the repository you want to analyze by modifying the `REPO_NAME` variable in `main.py`:
   ```python
   REPO_NAME = "owner/repository"
   ```

2. Run the script:
   ```bash
   python main.py
   ```

The script will output:
- Branch information
- Total commits analyzed
- Detailed commit history per developer
- Summary statistics in a table format

### Example Output

```
Analyzing branch: main
Branch head commit: abc123...

Total commits analyzed: 150

Commit history for developer1:
- 2024-01-01 12:00:00 [abc123] Initial commit
...

Contribution Summary:
developer  commits  additions  deletions  files_changed  active_days  avg_commits_per_active_day  code_churn
dev1       50       1000       500        75            20           2.5                         1500
dev2       30       800        300        45            15           2.0                         1100
```

## Customization

You can modify the analysis parameters when calling the function:

```python
analyze_contributions(
    repo_name,          # Repository name (owner/repo)
    access_token,       # GitHub access token
    days_back=90,       # Number of days to analyze (default: 90)
    branch='main'       # Branch to analyze (default: 'main')
)
```

## Error Handling

The script includes comprehensive error handling for:
- Authentication issues
- Repository access problems
- Branch validation
- Missing author information

## Security Notes

- Never commit your `.env` file to version control
- Keep your GitHub access token secure
- The `.gitignore` file is configured to exclude sensitive information

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.