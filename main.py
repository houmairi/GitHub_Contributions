from github import Github
from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict
import os
from dotenv import load_dotenv

def analyze_contributions(repo_name, access_token, days_back=90, branch='main'):
    """
    Analyze developer contributions in a GitHub repository
    
    Parameters:
    repo_name (str): Repository name in format 'owner/repo'
    access_token (str): GitHub personal access token
    days_back (int): Number of days to analyze
    branch (str): Branch to analyze (default: 'main')
    
    Returns:
    pd.DataFrame: Contribution statistics per developer
    """
    try:
        g = Github(access_token)
        repo = g.get_repo(repo_name)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Get the specified branch
        try:
            branch_ref = repo.get_branch(branch)
            print(f"Analyzing branch: {branch}")
            print(f"Branch head commit: {branch_ref.commit.sha}")
        except Exception as e:
            print(f"Error getting branch {branch}: {str(e)}")
            print("Available branches:")
            for b in repo.get_branches():
                print(f"- {b.name}")
            return None
        
        # Initialize statistics
        stats = defaultdict(lambda: {
            'commits': 0,
            'additions': 0,
            'deletions': 0,
            'files_changed': 0,
            'active_days': set(),
            'commit_messages': []  # Store commit messages for debugging
        })
        
        # Analyze commits
        commits = repo.get_commits(sha=branch, since=start_date)
        total_commits = 0
        
        print(f"\nAnalyzing commits from {start_date} to {end_date}")
        for commit in commits:
            total_commits += 1
            if not commit.author:
                print(f"Warning: No author for commit {commit.sha[:8]}")
                continue
                
            author = commit.author.login
            stats[author]['commits'] += 1
            stats[author]['active_days'].add(commit.commit.author.date.date())
            stats[author]['commit_messages'].append({
                'date': commit.commit.author.date,
                'message': commit.commit.message,
                'sha': commit.sha[:8]
            })
            
            # Get detailed stats if available
            if commit.stats:
                stats[author]['additions'] += commit.stats.additions
                stats[author]['deletions'] += commit.stats.deletions
                files_count = sum(1 for _ in commit.files)
                stats[author]['files_changed'] += files_count
        
        print(f"\nTotal commits analyzed: {total_commits}")
        
        # Convert to DataFrame
        data = []
        for author, author_stats in stats.items():
            data.append({
                'developer': author,
                'commits': author_stats['commits'],
                'additions': author_stats['additions'],
                'deletions': author_stats['deletions'],
                'files_changed': author_stats['files_changed'],
                'active_days': len(author_stats['active_days']),
                'avg_commits_per_active_day': round(author_stats['commits'] / len(author_stats['active_days']), 2),
                'code_churn': author_stats['additions'] + author_stats['deletions']
            })
            
            # Print detailed commit history for debugging
            print(f"\nCommit history for {author}:")
            for commit in sorted(author_stats['commit_messages'], key=lambda x: x['date']):
                print(f"- {commit['date'].strftime('%Y-%m-%d %H:%M:%S')} [{commit['sha']}] {commit['message'].split()[0]}")
        
        df = pd.DataFrame(data)
        df = df.sort_values('commits', ascending=False)
        return df
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print("If you're getting authentication errors, please check your access token.")
        print("If you're getting repository errors, please check the repository name format (should be 'owner/repo').")
        return None

# Example usage:
if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Get GitHub token from environment variable
    access_token = os.getenv('GITHUB_ACCESS_TOKEN')
    if not access_token:
        raise ValueError("GitHub access token not found in environment variables")
    
    # Replace with your repository name
    REPO_NAME = "houmairi/lms-shop"
    
    df = analyze_contributions(REPO_NAME, access_token, branch='main')
    if df is not None:
        print("\nContribution Summary:")
        print(df.to_string(index=False))