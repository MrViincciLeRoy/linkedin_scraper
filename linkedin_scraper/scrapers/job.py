import re
import logging
from typing import Optional
from playwright.async_api import Page

from ..models.job import Job
from ..callbacks import ProgressCallback, SilentCallback
from .base import BaseScraper

logger = logging.getLogger(__name__)


class JobScraper(BaseScraper):

    def __init__(self, page: Page, callback: Optional[ProgressCallback] = None):
        super().__init__(page, callback or SilentCallback())

    async def scrape(self, linkedin_url: str) -> Job:
        await self.callback.on_start("Job", linkedin_url)
        await self.navigate_and_wait(linkedin_url)
        await self.callback.on_progress("Navigated to job page", 10)
        await self.check_rate_limit()

        company = await self._get_company()
        job = Job(
            linkedin_url=linkedin_url,
            job_title=await self._get_job_title(),
            company=company,
            company_linkedin_url=await self._get_company_url(),
            location=await self._get_location(company),
            posted_date=await self._get_posted_date(),
            applicant_count=await self._get_applicant_count(),
            job_description=await self._get_description(),
        )

        await self.callback.on_progress("Scraping complete", 100)
        await self.callback.on_complete("Job", job)
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
            for link in await self.page.locator('a[href*="/company/"]').all():
                text = (await link.inner_text()).strip()
                if text and len(text) > 1 and not text.startswith('logo'):
                    return text
        except:
            pass
        return None

    async def _get_company_url(self) -> Optional[str]:
        try:
            link = self.page.locator('a[href*="/company/"]').first
            if await link.count() > 0:
                href = await link.get_attribute('href')
                if href:
                    href = href.split('?')[0]
                    return href if href.startswith('http') else f"https://www.linkedin.com{href}"
        except:
            pass
        return None

    async def _get_primary_description_parts(self):
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

    async def _get_location(self, company: Optional[str] = None) -> Optional[str]:
        parts = await self._get_primary_description_parts()
        if parts:
            segment = parts[0].strip()
            if company and segment.startswith(company):
                segment = segment[len(company):].strip()

            lines = [l.strip() for l in segment.split('\n') if l.strip()]
            if lines:
                return lines[-1]

            chunks = re.split(r'\s{2,}', segment)
            if len(chunks) > 1:
                return chunks[-1].strip()
            return segment or None
        return None

    async def _get_posted_date(self) -> Optional[str]:
        parts = await self._get_primary_description_parts()
        if len(parts) > 1:
            match = re.search(r'(\d+\s+(?:hour|day|week|month|year)s?\s+ago)', parts[1], re.IGNORECASE)
            if match:
                return match.group(1)

        try:
            for elem in await self.page.locator('span, div').all():
                text = (await elem.inner_text()).strip()
                if text and len(text) < 50:
                    match = re.search(r'(\d+\s+(?:hour|day|week|month|year)s?\s+ago)', text, re.IGNORECASE)
                    if match:
                        return match.group(1)
        except:
            pass
        return None

    async def _get_applicant_count(self) -> Optional[str]:
        parts = await self._get_primary_description_parts()
        for part in parts[1:]:
            cleaned = re.sub(r'\d+\s+(?:hour|day|week|month|year)s?\s+ago', '', part, flags=re.IGNORECASE).strip()
            match = re.search(
                r'((?:over\s+)?[\d,+]+\s+(?:applicant|people clicked|applied)s?)',
                cleaned, re.IGNORECASE
            )
            if match:
                return match.group(1).strip()
        return None

    async def _get_description(self) -> Optional[str]:
        for selector in [
            '.jobs-description__content',
            '.jobs-description-content__text',
            '[class*="jobs-description"]',
            '#job-details',
            'div[id="job-details"]',
            'article',
        ]:
            try:
                await self.page.wait_for_selector(selector, timeout=3000)
                elem = self.page.locator(selector).first
                if await elem.count() > 0:
                    text = (await elem.inner_text()).strip()
                    if text and len(text) > 50:
                        return text
            except:
                continue
        return None
