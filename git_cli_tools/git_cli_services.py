import subprocess
from common import logger
from typing import Optional


def _run_command(command: list[str], cwd: str = ".") -> dict:
    """
    Helper function to run git commands and return the output.
    
    :param command: Git command as a list of strings
    :param cwd: Working directory for the git command
    :return: Dictionary with success status, stdout, stderr, and return code
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "Command timed out after 30 seconds",
            "return_code": -1
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "return_code": -1
        }


def git_issue_list(
    repo_path: str = ".",
    assignee: Optional[str] = None,
    author: Optional[str] = None,
    jq: Optional[str] = None,
    json_fields: Optional[list[str]] = None,
    label: Optional[list[str]] = None,
    limit: int = 30,
    mention: Optional[str] = None,
    milestone: Optional[str] = None,
    search: Optional[str] = None,
    state: str = "open"
) -> dict:
    """
    List GitHub issues using the GitHub CLI (gh issue list).
    
    Supported flags and their usage:
    
    :param repo_path: Path to the git repository (default: current directory)
    :param assignee: Filter by assignee username (e.g., "octocat" or "@me" for yourself)
    :param author: Filter by author username
    :param jq: Filter JSON output using a jq expression (e.g., ".[] | .title")
    :param json_fields: Output JSON with specified fields. Supported fields:
                        ["assignees", "author", "body", "closed", "closedAt", "comments",
                         "createdAt", "id", "labels", "milestone", "number", "projectCards",
                         "projectItems", "reactionGroups", "state", "title", "updatedAt", "url"]
    :param label: Filter by label names (e.g., ["bug", "feature"])
    :param limit: Maximum number of issues to fetch (default: 30, max: 1000)
    :param mention: Filter by mentioned username
    :param milestone: Filter by milestone number or title
    :param search: Search issues with query string (GitHub search syntax)
    :param state: Filter by state - must be one of: "open", "closed", "all" (default: "open")
    :return: Dictionary with success status, output, error, and return code
    
    Examples:
        # List open issues:
        git_issue_list(repo_path="/path/to/repo")
        
        # List closed issues assigned to you:
        git_issue_list(repo_path="/path/to/repo", assignee="@me", state="closed")
        
        # List issues with bug label as JSON:
        git_issue_list(repo_path="/path/to/repo", label=["bug"], json_fields=["number", "title", "state"])
        
        # Search issues:
        git_issue_list(repo_path="/path/to/repo", search="crash in testing")
    """
    logger.info(f"Listing GitHub issues in {repo_path} with filters")
    
    # Build the gh issue list command
    command = ["gh", "issue", "list"]
    
    # Add flags based on parameters
    if assignee:
        command.extend(["--assignee", assignee])
    
    if author:
        command.extend(["--author", author])
    
    if jq:
        command.extend(["--jq", jq])
    
    if json_fields:
        command.extend(["--json", ",".join(json_fields)])
    
    if label:
        for lbl in label:
            command.extend(["--label", lbl])
    
    if limit != 30:  # Only add if not default
        command.extend(["--limit", str(limit)])
    
    if mention:
        command.extend(["--mention", mention])
    
    if milestone:
        command.extend(["--milestone", milestone])
    
    if search:
        command.extend(["--search", search])
    
    if state != "open":  # Only add if not default
        command.extend(["--state", state])
    
    result = _run_command(command, cwd=repo_path)
    
    if result["success"]:
        logger.info(f"Successfully listed issues")
    else:
        logger.error(f"Failed to list issues: {result['error']}")
    
    return result


def git_issue_view(
    issue_identifier: str,
    repo_path: str = ".",
    comments: bool = False,
    jq: Optional[str] = None,
    json_fields: Optional[list[str]] = None
) -> dict:
    """
    View a specific GitHub issue using the GitHub CLI (gh issue view).
    
    Supported flags and their usage:
    
    :param issue_identifier: Issue number or URL (required, e.g., "123" or full GitHub issue URL)
    :param repo_path: Path to the git repository (default: current directory)
    :param comments: View issue comments (default: False)
    :param jq: Filter JSON output using a jq expression (e.g., ".title")
    :param json_fields: Output JSON with specified fields. Supported fields:
                        ["assignees", "author", "body", "closed", "closedAt",
                         "closedByPullRequestsReferences", "comments", "createdAt", "id",
                         "isPinned", "labels", "milestone", "number", "projectCards",
                         "projectItems", "reactionGroups", "state", "stateReason",
                         "title", "updatedAt", "url"]
    :return: Dictionary with success status, output, error, and return code
    
    Examples:
        # View issue #42:
        git_issue_view(issue_identifier="42", repo_path="/path/to/repo")
        
        # View issue with comments:
        git_issue_view(issue_identifier="42", repo_path="/path/to/repo", comments=True)
        
        # View issue as JSON with specific fields:
        git_issue_view(issue_identifier="42", json_fields=["number", "title", "state", "body"])
        
        # View issue by URL:
        git_issue_view(issue_identifier="https://github.com/owner/repo/issues/42")
    """
    if not issue_identifier:
        return {
            "success": False,
            "output": "",
            "error": "issue_identifier is required (e.g., issue number or URL)",
            "return_code": -1
        }
    
    logger.info(f"Viewing GitHub issue '{issue_identifier}' in {repo_path}")
    
    # Build the gh issue view command
    command = ["gh", "issue", "view", issue_identifier]
    
    # Add flags based on parameters
    if comments:
        command.append("--comments")
    
    if jq:
        command.extend(["--jq", jq])
    
    if json_fields:
        command.extend(["--json", ",".join(json_fields)])
    
    result = _run_command(command, cwd=repo_path)
    
    if result["success"]:
        logger.info(f"Successfully viewed issue '{issue_identifier}'")
    else:
        logger.error(f"Failed to view issue '{issue_identifier}': {result['error']}")
    
    return result


def git_pr_list(
    repo_path: str = ".",
    assignee: Optional[str] = None,
    author: Optional[str] = None,
    base: Optional[str] = None,
    draft: Optional[bool] = None,
    head: Optional[str] = None,
    jq: Optional[str] = None,
    json_fields: Optional[list[str]] = None,
    label: Optional[list[str]] = None,
    limit: int = 30,
    search: Optional[str] = None,
    state: str = "open"
) -> dict:
    """
    List GitHub pull requests using the GitHub CLI (gh pr list).
    
    Supported flags and their usage:
    
    :param repo_path: Path to the git repository (default: current directory)
    :param assignee: Filter by assignee username (e.g., "octocat" or "@me")
    :param author: Filter by author username
    :param base: Filter by base branch (e.g., "main", "develop")
    :param draft: Filter by draft state (True for drafts only, False for ready PRs, None for all)
    :param head: Filter by head branch
    :param jq: Filter JSON output using a jq expression (e.g., ".[] | .title")
    :param json_fields: Output JSON with specified fields. Supported fields:
                        ["additions", "assignees", "author", "autoMergeRequest", "baseRefName",
                         "baseRefOid", "body", "changedFiles", "closed", "closedAt",
                         "closingIssuesReferences", "comments", "commits", "createdAt",
                         "deletions", "files", "fullDatabaseId", "headRefName", "headRefOid",
                         "headRepository", "headRepositoryOwner", "id", "isCrossRepository",
                         "isDraft", "labels", "latestReviews", "maintainerCanModify",
                         "mergeCommit", "mergeStateStatus", "mergeable", "mergedAt", "mergedBy",
                         "milestone", "number", "potentialMergeCommit", "projectCards",
                         "projectItems", "reactionGroups", "reviewDecision", "reviewRequests",
                         "reviews", "state", "statusCheckRollup", "title", "updatedAt", "url"]
    :param label: Filter by label names (e.g., ["bug", "feature"])
    :param limit: Maximum number of PRs to fetch (default: 30)
    :param search: Search pull requests with query string (GitHub search syntax)
    :param state: Filter by state - must be one of: "open", "closed", "merged", "all" (default: "open")
    :return: Dictionary with success status, output, error, and return code
    
    Examples:
        # List open PRs:
        git_pr_list(repo_path="/path/to/repo")
        
        # List merged PRs by author:
        git_pr_list(repo_path="/path/to/repo", author="octocat", state="merged")
        
        # List draft PRs:
        git_pr_list(repo_path="/path/to/repo", draft=True)
        
        # List PRs targeting main branch as JSON:
        git_pr_list(repo_path="/path/to/repo", base="main", json_fields=["number", "title", "state"])
        
        # Search PRs:
        git_pr_list(repo_path="/path/to/repo", search="fix bug in login")
    """
    logger.info(f"Listing GitHub pull requests in {repo_path} with filters")
    
    # Build the gh pr list command
    command = ["gh", "pr", "list"]
    
    # Add flags based on parameters
    if assignee:
        command.extend(["--assignee", assignee])
    
    if author:
        command.extend(["--author", author])
    
    if base:
        command.extend(["--base", base])
    
    if draft is not None:
        if draft:
            command.append("--draft")
        else:
            # To filter for non-draft PRs, we use --draft=false
            command.append("--draft=false")
    
    if head:
        command.extend(["--head", head])
    
    if jq:
        command.extend(["--jq", jq])
    
    if json_fields:
        command.extend(["--json", ",".join(json_fields)])
    
    if label:
        for lbl in label:
            command.extend(["--label", lbl])
    
    if limit != 30:  # Only add if not default
        command.extend(["--limit", str(limit)])
    
    if search:
        command.extend(["--search", search])
    
    if state != "open":  # Only add if not default
        command.extend(["--state", state])
    
    result = _run_command(command, cwd=repo_path)
    
    if result["success"]:
        logger.info(f"Successfully listed pull requests")
    else:
        logger.error(f"Failed to list pull requests: {result['error']}")
    
    return result


def git_pr_view(
    pr_identifier: Optional[str] = None,
    repo_path: str = ".",
    comments: bool = False,
    jq: Optional[str] = None,
    json_fields: Optional[list[str]] = None,
    repo: Optional[str] = None
) -> dict:
    """
    View a specific GitHub pull request using the GitHub CLI (gh pr view).
    
    Supported flags and their usage:
    
    :param pr_identifier: PR number, URL, or branch name (optional - defaults to current branch)
    :param repo_path: Path to the git repository (default: current directory)
    :param comments: View pull request comments (default: False)
    :param jq: Filter JSON output using a jq expression (e.g., ".title")
    :param json_fields: Output JSON with specified fields. Supported fields:
                        ["additions", "assignees", "author", "autoMergeRequest", "baseRefName",
                         "baseRefOid", "body", "changedFiles", "closed", "closedAt",
                         "closingIssuesReferences", "comments", "commits", "createdAt",
                         "deletions", "files", "fullDatabaseId", "headRefName", "headRefOid",
                         "headRepository", "headRepositoryOwner", "id", "isCrossRepository",
                         "isDraft", "labels", "latestReviews", "maintainerCanModify",
                         "mergeCommit", "mergeStateStatus", "mergeable", "mergedAt", "mergedBy",
                         "milestone", "number", "potentialMergeCommit", "projectCards",
                         "projectItems", "reactionGroups", "reviewDecision", "reviewRequests",
                         "reviews", "state", "statusCheckRollup", "title", "updatedAt", "url"]
    :param repo: Select another repository using [HOST/]OWNER/REPO format (e.g., "microsoft/vscode")
    :return: Dictionary with success status, output, error, and return code
    
    Examples:
        # View PR #42:
        git_pr_view(pr_identifier="42", repo_path="/path/to/repo")
        
        # View PR with comments:
        git_pr_view(pr_identifier="42", repo_path="/path/to/repo", comments=True)
        
        # View PR as JSON with specific fields:
        git_pr_view(pr_identifier="42", json_fields=["number", "title", "state", "body"])
        
        # View PR by URL:
        git_pr_view(pr_identifier="https://github.com/owner/repo/pull/42")
        
        # View PR by branch name:
        git_pr_view(pr_identifier="feature-branch", repo_path="/path/to/repo")
        
        # View PR from another repository:
        git_pr_view(pr_identifier="42", repo="owner/repo")
        
        # View current branch's PR:
        git_pr_view(repo_path="/path/to/repo")
    """
    logger.info(f"Viewing GitHub pull request '{pr_identifier or 'current branch'}' in {repo_path}")
    
    # Build the gh pr view command
    command = ["gh", "pr", "view"]
    
    # Add PR identifier if provided
    if pr_identifier:
        command.append(pr_identifier)
    
    # Add flags based on parameters
    if comments:
        command.append("--comments")
    
    if jq:
        command.extend(["--jq", jq])
    
    if json_fields:
        command.extend(["--json", ",".join(json_fields)])
    
    if repo:
        command.extend(["--repo", repo])
    
    result = _run_command(command, cwd=repo_path)
    
    if result["success"]:
        logger.info(f"Successfully viewed pull request '{pr_identifier or 'current branch'}'")
    else:
        logger.error(f"Failed to view pull request '{pr_identifier or 'current branch'}': {result['error']}")
    
    return result


def git_pr_diff(
    pr_identifier: Optional[str] = None,
    repo_path: str = ".",
    color: str = "auto",
    name_only: bool = False,
    patch: bool = False
) -> dict:
    """
    View the diff for a GitHub pull request using the GitHub CLI (gh pr diff).
    
    Supported flags and their usage:
    
    :param pr_identifier: PR number, URL, or branch name (optional - defaults to current branch)
    :param repo_path: Path to the git repository (default: current directory)
    :param color: Use color in diff output - must be one of: "always", "never", "auto" (default: "auto")
    :param name_only: Display only names of changed files (default: False)
    :param patch: Display diff in patch format (default: False)
    :return: Dictionary with success status, output, error, and return code
    
    Examples:
        # View diff for PR #42:
        git_pr_diff(pr_identifier="42", repo_path="/path/to/repo")
        
        # View only changed file names:
        git_pr_diff(pr_identifier="42", repo_path="/path/to/repo", name_only=True)
        
        # View diff in patch format:
        git_pr_diff(pr_identifier="42", repo_path="/path/to/repo", patch=True)
        
        # View diff with color always enabled:
        git_pr_diff(pr_identifier="42", repo_path="/path/to/repo", color="always")
        
        # View diff by URL:
        git_pr_diff(pr_identifier="https://github.com/owner/repo/pull/42")
        
        # View diff by branch name:
        git_pr_diff(pr_identifier="feature-branch", repo_path="/path/to/repo")
        
        # View current branch's PR diff:
        git_pr_diff(repo_path="/path/to/repo")
    """
    logger.info(f"Viewing diff for GitHub pull request '{pr_identifier or 'current branch'}' in {repo_path}")
    
    # Build the gh pr diff command
    command = ["gh", "pr", "diff"]
    
    # Add PR identifier if provided
    if pr_identifier:
        command.append(pr_identifier)
    
    # Add flags based on parameters
    if color != "auto":  # Only add if not default
        command.extend(["--color", color])
    
    if name_only:
        command.append("--name-only")
    
    if patch:
        command.append("--patch")
    
    result = _run_command(command, cwd=repo_path)
    
    if result["success"]:
        logger.info(f"Successfully retrieved diff for pull request '{pr_identifier or 'current branch'}'")
    else:
        logger.error(f"Failed to retrieve diff for pull request '{pr_identifier or 'current branch'}': {result['error']}")
    
    return result