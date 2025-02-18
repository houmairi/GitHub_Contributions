#!/usr/bin/env python3
import git
from datetime import datetime
from collections import defaultdict, Counter
import argparse
from datetime import datetime, timedelta

AUTHOR_MAPPINGS = {
    'ntunjic': 'Niko',
    'Niko': 'Niko',
    'Waluigi-dev': 'Waluigi-dev',
    'if21b503': 'Waluigi-dev'
}

def analyze_repo(repo_path, start_date=None, end_date=None):
    """Analyze git repository for developer contributions."""
    repo = git.Repo(repo_path)
    
    # Convert dates to datetime objects if provided
    start = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
    end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
    
    # Initialize statistics dictionaries
    stats = defaultdict(lambda: {
        'commits': 0,
        'files_changed': 0,
        'additions': 0,
        'deletions': 0,
        'active_days': set(),
        'commit_dates': [],
    })
    
    total_commits = 0
    
    # Analyze commits
    for commit in repo.iter_commits():
        author_name = commit.author.name
        author_name = AUTHOR_MAPPINGS.get(author_name, author_name)
        commit_date = datetime.fromtimestamp(commit.committed_date)
        
        # Skip if commit is outside date range
        if start and commit_date < start:
            continue
        if end and commit_date > end:
            continue
        
        total_commits += 1
        stats[author_name]['commits'] += 1
        stats[author_name]['active_days'].add(commit_date.date())
        stats[author_name]['commit_dates'].append(commit_date)
        
        try:
            for file in commit.stats.files:
                stats[author_name]['files_changed'] += 1
                stats[author_name]['additions'] += commit.stats.files[file]['insertions']
                stats[author_name]['deletions'] += commit.stats.files[file]['deletions']
        except:
            continue

    # Calculate additional metrics
    for author in stats:
        data = stats[author]
        
        # Calculate contribution percentages
        data['commit_percentage'] = (data['commits'] / total_commits) * 100
        
        # Calculate impact metrics
        data['avg_files_per_commit'] = data['files_changed'] / data['commits'] if data['commits'] > 0 else 0
        data['avg_lines_per_commit'] = (data['additions'] + data['deletions']) / data['commits'] if data['commits'] > 0 else 0
        data['code_churn'] = data['additions'] + data['deletions']
        data['impact_ratio'] = (data['additions'] - data['deletions']) / data['code_churn'] if data['code_churn'] > 0 else 0
        
        # Calculate velocity metrics
        active_days = len(data['active_days'])
        data['active_days_count'] = active_days
        if active_days > 0:
            data['commits_per_active_day'] = data['commits'] / active_days
        
        # Calculate time patterns
        hour_distribution = Counter([d.hour for d in data['commit_dates']])
        data['peak_hour'] = max(hour_distribution.items(), key=lambda x: x[1])[0] if hour_distribution else None

    return stats

def print_stats(stats):
    """Print formatted statistics."""
    print("\nDeveloper Contribution Analysis")
    print("=" * 80)
    
    # Sort by number of commits (descending)
    sorted_authors = sorted(stats.items(), key=lambda x: x[1]['commits'], reverse=True)
    
    for author, data in sorted_authors:
        print(f"\nDeveloper: {author}")
        print("-" * 50)
        
        # Basic stats
        print(f"Basic Metrics:")
        print(f"  Total commits:     {data['commits']} ({data['commit_percentage']:.1f}% of all commits)")
        print(f"  Files changed:     {data['files_changed']}")
        print(f"  Lines added:       {data['additions']}")
        print(f"  Lines deleted:     {data['deletions']}")
        print(f"  Net lines:         {data['additions'] - data['deletions']}")
        
        # Impact metrics
        print(f"\nImpact Metrics:")
        print(f"  Avg files/commit:  {data['avg_files_per_commit']:.1f}")
        print(f"  Avg lines/commit:  {data['avg_lines_per_commit']:.1f}")
        print(f"  Code churn:        {data['code_churn']} lines")
        print(f"  Impact ratio:      {data['impact_ratio']:.2f}")
        
        # Activity metrics
        print(f"\nActivity Metrics:")
        print(f"  Active days:       {data['active_days_count']}")
        print(f"  Commits/active day:{data['commits_per_active_day']:.1f}")
        print(f"  Peak commit hour:  {data['peak_hour']:02d}:00")

def main():
    parser = argparse.ArgumentParser(description='Analyze git repository contributions')
    parser.add_argument('repo_path', help='Path to git repository')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    try:
        stats = analyze_repo(args.repo_path, args.start_date, args.end_date)
        print_stats(stats)
    except Exception as e:
        print(f"Error analyzing repository: {e}")

if __name__ == "__main__":
    main()