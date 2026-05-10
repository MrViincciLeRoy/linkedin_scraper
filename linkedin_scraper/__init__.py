"""LinkedIn Scraper - Async Playwright-based scraper for LinkedIn."""

import traceback

# Version
__version__ = "3.1.2"

# Core modules
print("DEBUG: Importing core modules...")
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
    print("✓ Core modules imported successfully")
except Exception as e:
    print(f"✗ FAILED to import core modules: {e}")
    traceback.print_exc()
    raise

# Scrapers
print("DEBUG: Importing scrapers...")
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
    print("✓ Scrapers imported successfully")
except Exception as e:
    print(f"✗ FAILED to import scrapers: {e}")
    traceback.print_exc()
    raise

# Callbacks
print("DEBUG: Importing callbacks...")
try:
    from .callbacks import (
        ProgressCallback,
        ConsoleCallback,
        SilentCallback,
        JSONLogCallback,
        MultiCallback,
    )
    print("✓ Callbacks imported successfully")
except Exception as e:
    print(f"✗ FAILED to import callbacks: {e}")
    traceback.print_exc()
    raise

# Models
print("DEBUG: Importing models...")
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
    print("✓ Models imported successfully")
except Exception as e:
    print(f"✗ FAILED to import models: {e}")
    traceback.print_exc()
    raise

print("DEBUG: All imports completed successfully!")

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
