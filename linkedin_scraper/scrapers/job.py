"""
Job scraper for LinkedIn.

Extracts job posting information from LinkedIn job pages.
"""
import re
import logging
from typing import Optional
from playwright.async_api import Page

from ..models.job import Job
from ..core.exceptions import ProfileNotFoundError
from ..callbacks import ProgressCallback, SilentCallback
from .base import BaseScraper

logger = logging.getLogger(__name__)


class JobScraper(BaseScraper):
    """
    Scraper for LinkedIn job postings.

    Example:
        async with BrowserManager() as browser:
            scraper = JobScraper(browser.page)
            job = await scraper.scrape("https://www.linkedin.com/jobs/view/123456/")
            print(job.to_json())
    """

    def __init__(self, page: Page, callback: Optional[ProgressCallback] = None):
        super().__init__(page, callback or SilentCallback())

    async def scrape(self, linkedin_url: str) -> Job:
        logger.info(f"Starting job scraping: {linkedin_url}")
        await self.callback.on_start("Job", linkedin_url)

        await self.navigate_and_wait(linkedin_url)
        await self.callback.on_progress("Navigated to job page", 10)

        await self.check_rate_limit()

        job_title = await self._get_job_title()
        await self.callback.on_progress(f"Got job title: {job_title}", 20)

        company = await self._get_company()
        await self.callback.on_progress("Got company name", 30)

        location = await self._get_location()
        await self.callback.on_progress("Got location", 40)

        posted_date = await self._get_posted_date()
        await self.callback.on_progress("Got posted date", 50)

        applicant_count = await self._get_applicant_count()
        await self.callback.on_progress("Got applicant count", 60)

        job_description = await self._get_description()
        await self.callback.on_progress("Got job description", 80)

        company_url = await self._get_company_url()
        await self.callback.on_progress("Got company URL", 90)

        job = Job(
            linkedin_url=linkedin_url,
            job_title=job_title,
            company=company,
            company_linkedin_url=company_url,
            location=location,
            posted_date=posted_date,
            applicant_count=applicant_count,
            job_description=job_description
        )

        await self.callback.on_progress("Scraping complete", 100)
        await self.callback.on_complete("Job", job)

        logger.info(f"Successfully scraped job: {job_title}")
        return job

    async def _get_job_title(self) -> Optional[str]:
        try:
            title_elem = self.page.locator('h1').first
            await title_elem.wait_for(timeout=5000)
            return (await title_elem.inner_text()).strip()
        except:
            return None

    async def _get_company(self) -> Optional[str]:
        try:
            company_links = await self.page.locator('a[href*="/company/"]').all()
            for link in company_links:
                text = (await link.inner_text()).strip()
                if text and len(text) > 1 and not text.startswith('logo'):
                    return text
        except:
            pass
        return None

    async def _get_company_url(self) -> Optional[str]:
        try:
            company_link = self.page.locator('a[href*="/company/"]').first
            if await company_link.count() > 0:
                href = await company_link.get_attribute('href')
                if href:
                    href = href.split('?')[0]
                    if not href.startswith('http'):
                        href = f"https://www.linkedin.com{href}"
                    return href
        except:
            pass
        return None

    async def _get_primary_description_parts(self):
        """Return split parts from the primary description container, or []."""
        try:
            container = self.page.locator(
                '.job-details-jobs-unified-top-card__primary-description-container'
            ).first
            if await container.count() > 0:
                text = await container.inner_text()
                return [p.strip() for p in text.split('·')]
        except:
            pass
        return []

    async def _get_location(self) -> Optional[str]:
        parts = await self._get_primary_description_parts()
        if parts:
            # parts[0] may be "CompanyName\nCity, State" — take the last non-empty line
            lines = [l.strip() for l in parts[0].split('\n') if l.strip()]
            if lines:
                return lines[-1]

        # Fallback: scan spans for something that looks like a location
        try:
            job_panel = self.page.locator('h1').first.locator('xpath=ancestor::*[5]')
            if await job_panel.count() > 0:
                title = await self._get_job_title()
                for elem in await job_panel.locator('span, div').all():
                    text = (await elem.inner_text()).strip()
                    if (
                        text
                        and (',' in text or 'Remote' in text or 'United States' in text)
                        and text != title
                        and 3 < len(text) < 100
                        and not text.startswith('$')
                    ):
                        return text
        except:
            pass
        return None

    async def _get_posted_date(self) -> Optional[str]:
        parts = await self._get_primary_description_parts()
        if len(parts) > 1:
            segment = parts[1]
            match = re.search(
                r'(\d+\s+(?:hour|day|week|month|year)s?\s+ago)', segment, re.IGNORECASE
            )
            if match:
                return match.group(1)
            # Fallback: first line of the segment
            first_line = segment.split('\n')[0].strip()
            if first_line:
                return first_line

        # Fallback: scan page for a time-ago string in a short element
        try:
            for elem in await self.page.locator('span, div').all():
                text = (await elem.inner_text()).strip()
                if text and len(text) < 50:
                    match = re.search(
                        r'(\d+\s+(?:hour|day|week|month|year)s?\s+ago)', text, re.IGNORECASE
                    )
                    if match:
                        return match.group(1)
        except:
            pass
        return None

    async def _get_applicant_count(self) -> Optional[str]:
        parts = await self._get_primary_description_parts()
        for part in parts[1:]:
            match = re.search(
                r'([\w\s,+]+(?:applicant|people clicked|applied)s?)', part, re.IGNORECASE
            )
            if match:
                return match.group(1).strip()

        # Fallback: scan main content
        try:
            main_content = self.page.locator('main').first
            if await main_content.count() > 0:
                for elem in await main_content.locator('span, div').all():
                    text = (await elem.inner_text()).strip()
                    if text and len(text) < 50:
                        text_lower = text.lower()
                        if 'applicant' in text_lower or 'people clicked' in text_lower or 'applied' in text_lower:
                            return text
        except:
            pass
        return None

    async def _get_description(self) -> Optional[str]:
        try:
            await self.page.wait_for_selector('article', timeout=5000)
            about_heading = self.page.locator('h2:has-text("About the job")').first
            if await about_heading.count() > 0:
                article = about_heading.locator('xpath=ancestor::article[1]')
                if await article.count() > 0:
                    return (await article.inner_text()).strip()

            article = self.page.locator('article').first
            if await article.count() > 0:
                return (await article.inner_text()).strip()
        except:
            pass
        return None
