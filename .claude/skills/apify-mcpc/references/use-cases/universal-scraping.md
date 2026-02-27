# Universal Scraping

## When to use
User wants general-purpose web scraping that doesn't fit a specific use case, or wants to scrape a platform/site not covered by other use-case files.

## Suggested Actors
Known good starting points. Always verify via `search-actors` for latest options.

| User Need | Suggested Actor | Why |
|---|---|---|
| Any website content | `apify/website-content-crawler` | AI-ready content extraction |
| Quick web search/URL fetch | `apify-slash-rag-web-browser` | One-off queries (via tools-call) |
| Google search results | `apify/google-search-scraper` | SERP scraping |
| Contact info from URLs | `vdrmota/contact-info-scraper` | Email/phone extraction |
| Instagram (comprehensive) | `apify/instagram-scraper` | Full IG data |
| Facebook (comprehensive) | `apify/facebook-pages-scraper` | Full FB page data |
| TikTok (comprehensive) | `clockworks/tiktok-scraper` | Full TT data |
| YouTube (comprehensive) | `streamers/youtube-scraper` | Full YT data |
| Google Maps | `compass/crawler-google-places` | Business data |

## Search Keywords
`web scraper`, `website crawler`, `data extraction`, `[platform name] scraper`, `[data type] extractor`

## Platform Coverage
- **Strong**: All major social platforms (Instagram, Facebook, TikTok, YouTube)
- **Strong**: Google (Search, Maps, Trends), review sites (Booking, TripAdvisor)
- **Medium**: E-commerce (Amazon, eBay — search for platform-specific Actors)
- **Expanding**: Apify Store has thousands of Actors — if not listed here, use `search-actors`

## Multi-Actor Workflows
| Goal | Step 1 | Step 2 |
|---|---|---|
| Website audit | `apify/website-content-crawler` → | `vdrmota/contact-info-scraper` |
| Search + scrape | `apify/google-search-scraper` → | `apify/website-content-crawler` |
| Data + contact enrichment | Any platform scraper → | `vdrmota/contact-info-scraper` |

## Gotchas
- `website-content-crawler` extracts text content, not structured data — for structured data, find a dedicated Actor
- `rag-web-browser` is for quick lookups, not bulk scraping — use proper Actors for scale
- When no specialized Actor exists, `website-content-crawler` with good `startUrls` is the fallback
- Always check if a specialized Actor exists before using generic ones — specialized Actors handle pagination, anti-bot measures, and output formatting better

## After Completion
Suggest: check if a more specialized Actor exists for follow-up tasks, enrich data with contact scraper, export in preferred format.
