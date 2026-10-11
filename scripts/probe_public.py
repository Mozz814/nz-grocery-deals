"""Inspect guest-visible store controls before enabling a hosted collector.

No account credentials, browser state, shopping profile or Telegram secrets are
loaded. This diagnostic does not record product prices as verified observations.
"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as runtime:
        browser = await runtime.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://www.woolworths.co.nz/specials-offers', wait_until='domcontentloaded', timeout=60000)
        try:
            await page.get_by_role('heading', name='Specials & offers', exact=True).first.wait_for(timeout=30000)
        except Exception:
            print('Expected offers heading unavailable.')
        print('FINAL URL:', page.url)
        text = await page.locator('body').inner_text()
        print('GUEST HEADER:', text[:3500])
        print('GUEST CONTENT:', text[-7000:])
        print('BUTTONS:', await page.get_by_role('button').all_text_contents())
        print('PRODUCT LINKS:', await page.locator('a[href*="product-details"]').count())
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
