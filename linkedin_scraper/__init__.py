"""LinkedIn Scraper - Async Playwright-based scraper for LinkedIn."""

import sys
import traceback

# Version
__version__ = "3.1.2"

# Track what was successfully imported
_import_errors = []

# Core modules
try:
    from .core import (
        BrowserManager,
        login_with_credentials,
        login_with_cookie,
        is_logged_in,
        wait_for_manual_login,
        load_credentials_from_env,
        # Exceptions
        LinkedInScraperException,
        AuthenticationError,
        RateLimitError,
        ElementNotFoundError,
        ProfileNotFoundError,
        NetworkError,
        ScrapingError,
    )
except Exception as e:
    _import_errors.append(f"core: {type(e).__name__}: {e}")
    traceback.print_exc()
    print(f"\n❌ FAILED to import core modules: {e}\n", file=sys.stderr)

# Scrapers
try:
    from .scrapers import (
        PersonScraper,
        CompanyScraper,
        JobScraper,
        JobSearchScraper,
        CompanyPostsScraper,
        # Added from HEAD
        PostReactionsScraper,
        ExtractUsersFromPostsScraper,
    )
except Exception as e:
    _import_errors.append(f"scrapers: {type(e).__name__}: {e}")
    traceback.print_exc()
    print(f"\n❌ FAILED to import scrapers: {e}\n", file=sys.stderr)

# Callbacks
try:
    from .callbacks import (
        ProgressCallback,
        ConsoleCallback,
        SilentCallback,
        JSONLogCallback,
        MultiCallback,
    )
except Exception as e:
    _import_errors.append(f"callbacks: {type(e).__name__}: {e}")
    traceback.print_exc()
    print(f"\n❌ FAILED to import callbacks: {e}\n", file=sys.stderr)

# Models
try:
    from .models import (
        Person,
        Experience,
        Education,
        Contact,
        Accomplishment,
        Interest,
        Company,
        CompanySummary,
        Employee,
        Job,
        Post,
        # Added from HEAD
        PostEngagementUser,
        ExtractUsersResult,
    )
except Exception as e:
    _import_errors.append(f"models: {type(e).__name__}: {e}")
    traceback.print_exc()
    print(f"\n❌ FAILED to import models: {e}\n", file=sys.stderr)

# Print summary if there were errors
if _import_errors:
    print("\n" + "="*60, file=sys.stderr)
    print("⚠️  IMPORT ERRORS DETECTED:", file=sys.stderr)
    for error in _import_errors:
        print(f"  - {error}", file=sys.stderr)
    print("="*60 + "\n", file=sys.stderr)

__all__ = [
    # Version
    "__version__",
    # Core
    "BrowserManager",
    "login_with_credentials",
    "login_with_cookie",
    "is_logged_in",
    "wait_for_manual_login",
    "load_credentials_from_env",
    # Scrapers
    "PersonScraper",
    "CompanyScraper",
    "JobScraper",
    "JobSearchScraper",
    "CompanyPostsScraper",
    "PostReactionsScraper",
    "ExtractUsersFromPostsScraper",
    # Exceptions
    "LinkedInScraperException",
    "AuthenticationError",
    "RateLimitError",
    "ElementNotFoundError",
    "ProfileNotFoundError",
    "NetworkError",
    "ScrapingError",
    # Callbacks
    "ProgressCallback",
    "ConsoleCallback",
    "SilentCallback",
    "JSONLogCallback",
    "MultiCallback",
    # Models
    "Person",
    "Experience",
    "Education",
    "Contact",
    "Accomplishment",
    "Interest",
    "Company",
    "CompanySummary",
    "Employee",
    "Job",
    "Post",
    "PostEngagementUser",
    "ExtractUsersResult",
]
