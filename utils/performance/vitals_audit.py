"""
Core Web Vitals & Performance Audit Utility for Kirki eCommerce
Queries Navigation Timing API and PerformanceObserver to audit LCP, CLS, DOMContentLoaded, and Page Load Time.
"""

from selenium.webdriver.remote.webdriver import WebDriver


def audit_page_vitals(browser: WebDriver, url: str) -> dict:
    """
    Navigates to URL and extracts Core Web Vitals performance metrics from Chrome Performance API.
    
    Returns dict:
        {
            "url": str,
            "dom_content_loaded_ms": float,
            "page_load_time_ms": float,
            "lcp_ms": float,
            "cls": float,
            "transfer_size_kb": float
        }
    """
    browser.get(url)
    browser.implicitly_wait(3)

    # Inject PerformanceObserver script to extract LCP and CLS
    script = """
    return (function() {
        let timing = performance.timing;
        let navEntries = performance.getEntriesByType("navigation");
        let nav = navEntries.length > 0 ? navEntries[0] : null;

        let domContentLoaded = nav ? nav.domContentLoadedEventEnd : (timing.domContentLoadedEventEnd - timing.navigationStart);
        let loadTime = nav ? nav.loadEventEnd : (timing.loadEventEnd - timing.navigationStart);
        let transferSize = nav ? (nav.transferSize / 1024.0) : 0.0;

        // Extract LCP metric if available
        let lcpEntries = performance.getEntriesByType("largest-contentful-paint");
        let lcp = lcpEntries.length > 0 ? lcpEntries[lcpEntries.length - 1].startTime : loadTime;

        // Extract CLS metric if available
        let layoutShiftEntries = performance.getEntriesByType("layout-shift");
        let cls = 0.0;
        for (let entry of layoutShiftEntries) {
            if (!entry.hadRecentInput) {
                cls += entry.value;
            }
        }

        return {
            dom_content_loaded_ms: Math.round(domContentLoaded),
            page_load_time_ms: Math.round(loadTime),
            lcp_ms: Math.round(lcp),
            cls: Math.round(cls * 1000) / 1000,
            transfer_size_kb: Math.round(transferSize * 10) / 10
        };
    })();
    """

    metrics = browser.execute_script(script)
    metrics["url"] = url
    return metrics
