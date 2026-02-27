# Competitor Intelligence

## When to use
User wants to analyze competitor strategies, content, pricing, ads, market positioning, or benchmark against competitors.

## Suggested Actors
Known good starting points. Always verify via `search-actors` for latest options.

| User Need | Suggested Actor | Why |
|---|---|---|
| Competitor business data | `compass/crawler-google-places` | Location, ratings, hours |
| Competitor contact discovery | `poidata/google-maps-email-extractor` | Email extraction |
| Competitor review analysis | `compass/Google-Maps-Reviews-Scraper` | Review comparison |
| Competitor ad strategies | `apify/facebook-ads-scraper` | Ad creative + targeting |
| Competitor page metrics | `apify/facebook-pages-scraper` | Page performance |
| Competitor content | `apify/facebook-posts-scraper` | Post strategies |
| Instagram profile metrics | `apify/instagram-profile-scraper` | Follower comparison |
| Instagram content monitoring | `apify/instagram-post-scraper` | Post tracking |
| Instagram growth tracking | `apify/instagram-followers-count-scraper` | Follower trends |
| YouTube competitor analysis | `streamers/youtube-channel-scraper` | Channel metrics |
| TikTok competitor data | `clockworks/tiktok-profile-scraper` | Profile comparison |
| Hotel benchmarking | `voyager/booking-scraper` | Hotel data + pricing |

## Search Keywords
`competitor analysis`, `facebook ads`, `instagram profile`, `business intelligence`, `price comparison`

## Platform Coverage
- **Strong**: Facebook (ads, pages, posts), Instagram (profiles, content), Google Maps (business data)
- **Medium**: YouTube, TikTok (profiles and content metrics)
- **Limited**: LinkedIn (no public scraping), Amazon (separate Actors needed)

## Multi-Actor Workflows
| Goal | Step 1 | Step 2 |
|---|---|---|
| Ad strategy analysis | `apify/facebook-ads-scraper` → | `apify/facebook-pages-scraper` |
| Content benchmarking | `apify/instagram-profile-scraper` → | `apify/instagram-post-scraper` |
| Local competitor audit | `compass/crawler-google-places` → | `compass/Google-Maps-Reviews-Scraper` |

## Gotchas
- Facebook Ad Library scraping returns only active ads — historical ads are not available
- Comparing follower counts across platforms is misleading (different user bases)
- Google Maps data varies by region — search queries must include location context
- Some Actors return cached data — check `modifiedAt` (via `fetch-actor-details` with `metadata` flag) for freshness

## After Completion
Suggest: compare metrics in a table, track changes over time with recurring scrapes, deep-dive into competitor content strategy.
