#!/usr/bin/env python3
"""
Hybrid iShares ETF Scraper - Final Corrected Version
=====================================================
This script uses a hybrid approach to avoid API rate limits and includes a
patch (`nest_asyncio`) for Windows/Python 3.12 compatibility.
The table selectors have been corrected based on the provided HTML structure.
The Skyvern prompt has been updated to handle consent pop-ups.
"""

import asyncio
import sys
import httpx
import json
from datetime import datetime
import nest_asyncio

# Apply the patch for Windows + Python 3.12 compatibility
nest_asyncio.apply()

from playwright.async_api import async_playwright
from skyvern import Skyvern

# --- PART 1: Use Playwright to navigate and get the direct ETF links ---
async def get_etf_urls():
    """
    Uses Playwright to navigate the initial iShares welcome/consent screens
    and scrape the direct URLs of the first two ETFs from the main table.
    """
    print("--- Starting Part 1: Navigating with Playwright ---")
    etf_urls = []
    async with async_playwright() as p:
        # Set headless=True for production runs to hide the browser window
        browser = await p.chromium.launch(headless=True) 
        page = await browser.new_page()
        
        try:
            print("Navigating to the iShares page...")
            await page.goto(
                "https://www.ishares.com/de/privatanleger/de/produkte/etf-investments#/?productView=all&pageNumber=1&sortColumn=totalFundSizeInMillions&sortDirection=desc&dataView=keyFacts&keyFacts=all",
                timeout=60000
            )
            
            # Step 1: Click "Alle Akzeptieren" on the cookie pop-up
            print("Step 1: Clicking 'Alle Akzeptieren'...")
            await page.locator('#onetrust-accept-btn-handler').click(timeout=15000)
            
            # Step 2: Click the "Weiter" LINK to continue
            print("Step 2: Clicking 'Weiter' to continue...")
            await page.locator('a[data-link-event="Accept t&c: individual"]:has-text("Weiter")').click(timeout=15000)
            
            # --- THIS IS THE FIX ---
            # Wait for the table element itself to be visible, using the correct class from inspection.
            table_selector = 'table.mat-table'
            print(f"Waiting for the ETF table ({table_selector}) to be visible...")
            await page.wait_for_selector(table_selector, timeout=30000)

            # Define the correct selector for the links within the table.
            link_selector = f'{table_selector} a.link-to-product-page'
            print("Table is visible. Waiting for links to populate...")
            await page.wait_for_selector(link_selector, timeout=15000)
            # ---------------------------------------------
            
            # Now we can safely collect the links.
            print("Table data loaded. Collecting the ETF URLs...")
            links = await page.locator(link_selector).all()
            
            # Get the href attribute from the first two links
            for i in range(min(1, len(links))): # Changed back to 2 for a better test
                href = await links[i].get_attribute('href')
                if href:
                    base_url = f"https://www.ishares.com{href}"
                    # --- THIS IS THE FIX ---
                    # Append the special parameters to the URL to bypass the consent screen directly.
                    # This is more robust than trying to click through the UI.
                    if "?" in base_url:
                        full_url = f"{base_url}&switchLocale=y&siteEntryPassthrough=true"
                    else:
                        full_url = f"{base_url}?switchLocale=y&siteEntryPassthrough=true"
                    
                    etf_urls.append(full_url)
            
            print(f"--- Part 1 Complete: Successfully collected and modified {len(etf_urls)} URLs ---")
            
        except Exception as e:
            print(f"An error occurred during Playwright navigation: {e}")
        finally:
            await browser.close()
            
    return etf_urls

# --- PART 2: Use Skyvern to extract data and monitor the tasks ---
async def run_and_monitor_skyvern_tasks(urls_to_process):
    if not urls_to_process:
        print("No URLs were collected, cannot start Skyvern tasks.")
        return []

    print("\n--- Starting Part 2: Extracting data with Skyvern ---")
    
    skyvern = Skyvern(
        api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjQ5MDMxODcwMDQsInN1YiI6Im9fNDQwNDIyMjg1MTk5ODQxODgyIn0.AhY6mFVTeTw6goxsF4Kciqg4FPgtrxuG4vjzZ5wt2ck", # Replace with your actual API key
        base_url="http://localhost:8000"
    )

    # --- THIS IS THE FIX ---
    # The prompt is now simpler because we are navigating directly to the content page.
    # No need to instruct the AI on how to handle pop-ups that will no longer appear.
    extraction_prompt = """
    From the current ETF product page, extract the following information:
    - Basic info: ETF name, ISIN, ticker symbol, and fund size (Gesamtfondsvermögen).
    - Fund details: The expense ratio (Laufende Kosten), inception date (Auflegungsdatum), and fund currency (Fondswährung).
    - Holdings data: Find the section for 'Portfolio' or 'Bestände'. Extract ALL visible holdings, including the Name, Weight, and Sector for each holding.
    """
    
    single_etf_schema = {
        "etf_name": {"type": "string"}, "isin": {"type": "string"}, "ticker": {"type": "string"},
        "fund_size": {"type": "string"}, "expense_ratio": {"type": "string"}, "inception_date": {"type": "string"},
        "currency": {"type": "string"},
        "holdings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"}, "weight": {"type": "string"}, "sector": {"type": "string"}
                }
            }
        }
    }

    run_ids = []
    for i, url in enumerate(urls_to_process, 1):
        print(f"\n[{i}/{len(urls_to_process)}] Creating Skyvern task for: {url}")
        try:
            result = await skyvern.run_task(
                prompt=extraction_prompt, url=url, max_steps=40, data_extraction_schema=single_etf_schema
            )
            run_ids.append({'url': url, 'run_id': result.run_id})
            print(f"Task created successfully. Run ID: {result.run_id}")
        except Exception as e:
            print(f"Failed to create Skyvern task for {url}: {e}")

    final_results = []
    for task in run_ids:
        # Note: Replace with your actual API key for monitoring as well
        result_data = await monitor_test_task(task['run_id'], f"ETF Scrape ({task['url']})", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjQ5MDMxODcwMDQsInN1YiI6Im9fNDQwNDIyMjg1MTk5ODQxODgyIn0.AhY6mFVTeTw6goxsF4Kciqg4FPgtrxuG4vjzZ5wt2ck")
        if result_data and "error" not in result_data:
            final_results.append(result_data)
            
    return final_results


async def monitor_test_task(run_id, task_name, api_key):
    base_url = "http://localhost:8000"
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    
    print(f"\n=== Monitoring Task: {task_name} ===")
    print(f"Task ID: {run_id}")
    print(f"Web UI: http://localhost:8080")
    print("-" * 50)
    
    max_wait_time = 480
    poll_interval = 3
    elapsed_time = 0
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        while elapsed_time < max_wait_time:
            try:
                response = await client.get(f"{base_url}/v1/runs/{run_id}", headers=headers)
                if response.status_code == 200:
                    task_data = response.json()
                    status = task_data.get("status", "unknown")
                    print(f"\r  [{elapsed_time:3d}s] Status: {status:<10}", end="")
                    
                    if status == 'completed':
                        output = task_data.get("output", {})
                        print(f"\n✅ Task COMPLETED!")
                        return output
                    elif status == 'failed':
                        failure_reason = task_data.get("failure_reason", "Unknown")
                        print(f"\n❌ Task FAILED: {failure_reason}")
                        return {"error": failure_reason}
                    elif status in ['terminated', 'cancelled']:
                        print(f"\n⚠️ Task was {status}")
                        return {"error": f"Task {status}"}
            except Exception as e:
                print(f"\n  Monitoring error: {e}")
            
            await asyncio.sleep(poll_interval)
            elapsed_time += poll_interval
        
        print(f"\n⏰ Task timed out after {max_wait_time}s")
        return {"error": "Task timed out"}

async def main():
    """Main execution orchestrator."""
    urls = await get_etf_urls()
    results = await run_and_monitor_skyvern_tasks(urls)
    
    if results:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ishares_hybrid_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n" + "=" * 60)
        print(f"HYBRID SCRAPE COMPLETE")
        print(f"=" * 60)
        print(f"Successfully processed: {len(results)}/{len(urls)} ETFs")
        print(f"Results saved to: {filename}")
        
        for i, etf_data in enumerate(results, 1):
            holdings_count = len(etf_data.get("holdings", []))
            print(f"\n📈 ETF {i}: {etf_data.get('etf_name', 'Unknown')}")
            print(f"   ISIN: {etf_data.get('isin', 'N/A')}")
            print(f"   Fund Size: {etf_data.get('fund_size', 'N/A')}")
            print(f"   Holdings Found: {holdings_count}")

        if len(results) == len(urls) and len(results) > 0:
             print(f"\n🎉 TEST SUCCESSFUL! The hybrid approach works.")
        else:
             print(f"\n⚠️ Partial success. Check logs and the output file.")
    else:
        print(f"\n❌ Test failed. No data was extracted.")
    
    print(f"\nView full task details at: http://localhost:8080")

if __name__ == "__main__":
    # IMPORTANT: Remember to replace placeholder API keys before running
    asyncio.run(main())