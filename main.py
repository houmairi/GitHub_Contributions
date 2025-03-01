#!/usr/bin/env python3
import git
from datetime import datetime
from collections import defaultdict, Counter
import argparse
from datetime import datetime, timedelta
import re
from statistics import mean, median, stdev

# Author mapping to normalize different usernames to a single identity
AUTHOR_MAPPINGS = {
    'ntunjic': 'Niko',
    'Niko': 'Niko',
    'Waluigi-dev': 'Waluigi-dev',
    'if21b503': 'Waluigi-dev'
}

def calculate_streaks(commit_dates):
    """
    Calculate commit streaks from a list of commit dates.
    
    Args:
        commit_dates (list): List of datetime objects representing commit dates
    
    Returns:
        tuple: (longest_streak, current_streak)
    """
    if not commit_dates:
        return 0, 0

    # Convert to dates and sort
    dates = sorted(set(d.date() for d in commit_dates))
    if not dates:
        return 0, 0

    longest_streak = 1
    current_streak = 1
    current_count = 1
    today = datetime.now().date()

    for i in range(1, len(dates)):
        if (dates[i] - dates[i-1]) == timedelta(days=1):
            current_count += 1
        else:
            longest_streak = max(longest_streak, current_count)
            current_count = 1

    # Update longest streak one final time
    longest_streak = max(longest_streak, current_count)

    # Calculate current streak
    if dates[-1] == today or dates[-1] == today - timedelta(days=1):
        current_date = dates[-1]
        current_streak = 1
        idx = len(dates) - 2

        while idx >= 0 and (current_date - dates[idx]) == timedelta(days=1):
            current_streak += 1
            current_date = dates[idx]
            idx -= 1
    else:
        current_streak = 0

    return longest_streak, current_streak

def get_commit_complexity(commit):
    """
    Analyze a commit to determine its complexity and quality.
    
    Args:
        commit: A git commit object
        
    Returns:
        dict: Metrics about the commit's complexity and quality
    """
    # Initialize metrics
    metrics = {
        'test_changes': 0,
        'doc_changes': 0,
        'code_changes': 0,
        'is_fix': False,
        'is_refactor': False,
        'is_feature': False,
        'file_types': set(),
        'commit_size': 0
    }
    
    # Check commit message for patterns
    message = commit.message.lower()
    if re.search(r'fix|bug|issue|error|crash|problem|fail', message):
        metrics['is_fix'] = True
    if re.search(r'refactor|clean|improve|optimize|simplify', message):
        metrics['is_refactor'] = True
    if re.search(r'feature|add|new|implement|support', message):
        metrics['is_feature'] = True
    
    # Analyze changed files
    for file in commit.stats.files:
        changes = commit.stats.files[file]['insertions'] + commit.stats.files[file]['deletions']
        metrics['commit_size'] += changes
        
        if 'test' in file.lower() or '/tests/' in file.lower():
            metrics['test_changes'] += changes
        elif 'doc' in file.lower() or 'readme' in file.lower() or '.md' in file.lower():
            metrics['doc_changes'] += changes
        else:
            metrics['code_changes'] += changes
        
        # Track file types
        if '.' in file:
            extension = file.split('.')[-1].lower()
            metrics['file_types'].add(extension)
    
    return metrics

def analyze_repo(repo_path, start_date=None, end_date=None):
    """
    Analyze git repository for developer contributions.
    
    Args:
        repo_path (str): Path to the git repository
        start_date (str, optional): Start date in 'YYYY-MM-DD' format
        end_date (str, optional): End date in 'YYYY-MM-DD' format
    
    Returns:
        dict: Statistics for each developer's contributions
    """
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
        'weekday_commits': defaultdict(int),
        'tests_added': 0,
        'docs_added': 0,
        'fix_commits': 0,
        'refactor_commits': 0, 
        'feature_commits': 0,
        'file_types': set(),
        'commit_sizes': [],
        'pr_related_commits': 0,
        'commit_messages': []
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
        stats[author_name]['weekday_commits'][commit_date.strftime('%A')] += 1
        
        try:
            for file in commit.stats.files:
                stats[author_name]['files_changed'] += 1
                stats[author_name]['additions'] += commit.stats.files[file]['insertions']
                stats[author_name]['deletions'] += commit.stats.files[file]['deletions']
                
                # Track file types
                if '.' in file:
                    extension = file.split('.')[-1].lower()
                    stats[author_name]['file_types'].add(extension)
                    
            # Analyze commit complexity and quality
            complexity = get_commit_complexity(commit)
            
            # Store commit message for semantic analysis
            stats[author_name]['commit_messages'].append(commit.message)
            
            # Update quality metrics
            stats[author_name]['tests_added'] += complexity['test_changes']
            stats[author_name]['docs_added'] += complexity['doc_changes']
            stats[author_name]['commit_sizes'].append(complexity['commit_size'])
            
            if complexity['is_fix']:
                stats[author_name]['fix_commits'] += 1
            if complexity['is_refactor']:
                stats[author_name]['refactor_commits'] += 1
            if complexity['is_feature']:
                stats[author_name]['feature_commits'] += 1
                
            # Check if commit is related to a PR
            if 'pull request' in commit.message.lower() or 'pr #' in commit.message.lower() or 'merge' in commit.message.lower():
                stats[author_name]['pr_related_commits'] += 1
                
        except Exception as e:
            # Print the specific error for debugging
            print(f"Error processing commit {commit.hexsha[:8]}: {e}")
            continue

    # Calculate additional metrics
    for author in stats:
        data = stats[author]
        
        # Calculate streaks
        longest_streak, current_streak = calculate_streaks(data['commit_dates'])
        data['longest_streak'] = longest_streak
        data['current_streak'] = current_streak
        
        # Calculate active weeks
        week_numbers = {d.isocalendar()[1] for d in data['commit_dates']}
        data['active_weeks'] = len(week_numbers)
        
        # Find most active day
        if data['weekday_commits']:
            data['most_active_day'] = max(data['weekday_commits'].items(), key=lambda x: x[1])[0]
        else:
            data['most_active_day'] = None
        
        # Calculate contribution percentages
        data['commit_percentage'] = (data['commits'] / total_commits) * 100
        
        # Calculate impact metrics
        data['avg_files_per_commit'] = data['files_changed'] / data['commits'] if data['commits'] > 0 else 0
        data['avg_lines_per_commit'] = (data['additions'] + data['deletions']) / data['commits'] if data['commits'] > 0 else 0
        data['code_churn'] = data['additions'] + data['deletions']
        data['impact_ratio'] = (data['additions'] - data['deletions']) / data['code_churn'] if data['code_churn'] > 0 else 0
        
        # Calculate quality metrics
        data['test_ratio'] = data['tests_added'] / data['additions'] if data['additions'] > 0 else 0
        data['doc_ratio'] = data['docs_added'] / data['additions'] if data['additions'] > 0 else 0
        data['fix_ratio'] = data['fix_commits'] / data['commits'] if data['commits'] > 0 else 0
        data['refactor_ratio'] = data['refactor_commits'] / data['commits'] if data['commits'] > 0 else 0
        data['feature_ratio'] = data['feature_commits'] / data['commits'] if data['commits'] > 0 else 0
        data['pr_ratio'] = data['pr_related_commits'] / data['commits'] if data['commits'] > 0 else 0
        
        # Calculate commit size statistics
        if data['commit_sizes']:
            data['median_commit_size'] = median(data['commit_sizes'])
            data['mean_commit_size'] = mean(data['commit_sizes'])
            data['atomic_commits'] = sum(1 for size in data['commit_sizes'] if size <= 50)  # Less than 50 lines is considered atomic
            data['atomic_commit_ratio'] = data['atomic_commits'] / data['commits'] if data['commits'] > 0 else 0
            if len(data['commit_sizes']) > 1:
                data['commit_size_stdev'] = stdev(data['commit_sizes'])
            else:
                data['commit_size_stdev'] = 0
        else:
            data['median_commit_size'] = 0
            data['mean_commit_size'] = 0
            data['commit_size_stdev'] = 0
            data['atomic_commits'] = 0
            data['atomic_commit_ratio'] = 0
        
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
        
        # Streak and pattern metrics
        print(f"\nStreak Metrics:")
        print(f"  Longest streak:    {data['longest_streak']} days")
        print(f"  Current streak:    {data['current_streak']} days")
        print(f"  Active weeks:      {data['active_weeks']}")
        print(f"  Most active day:   {data['most_active_day']}")
        
        # Impact metrics
        print(f"\nImpact Metrics:")
        print(f"  Avg files/commit:  {data['avg_files_per_commit']:.1f}")
        print(f"  Avg lines/commit:  {data['avg_lines_per_commit']:.1f}")
        print(f"  Code churn:        {data['code_churn']} lines")
        print(f"  Impact ratio:      {data['impact_ratio']:.2f}")
        
        # Quality metrics
        print(f"\nQuality Metrics:")
        print(f"  Test contribution: {data['test_ratio']*100:.1f}%")
        print(f"  Doc contribution:  {data['doc_ratio']*100:.1f}%")
        print(f"  Atomic commits:    {data['atomic_commit_ratio']*100:.1f}%")
        print(f"  Median commit size:{data['median_commit_size']:.1f} lines")
        
        # Commit type distribution
        print(f"\nCommit Type Distribution:")
        print(f"  Feature work:      {data['feature_ratio']*100:.1f}%")
        print(f"  Bug fixes:         {data['fix_ratio']*100:.1f}%")
        print(f"  Refactoring:       {data['refactor_ratio']*100:.1f}%")
        print(f"  PR-related:        {data['pr_ratio']*100:.1f}%")
        
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