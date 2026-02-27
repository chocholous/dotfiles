# Market Research

## When to use
User wants to analyze market conditions, geographic opportunities, pricing, consumer behavior, or validate product/market fit.

## Suggested Actors
Known good starting points. Always verify via `search-actors` for latest options.

| User Need | Suggested Actor | Why |
|---|---|---|
| Market density analysis | `compass/crawler-google-places` | Business count by location |
| Geospatial business data | `compass/google-maps-extractor` | Detailed business mapping |
| Regional interest trends | `apify/google-trends-scraper` | Search trend data |
| Consumer pricing | `apify/facebook-marketplace-scraper` | Market pricing signals |
| Event market analysis | `apify/facebook-events-scraper` | Event activity |
| Community needs | `apify/facebook-groups-scraper` | Consumer discussions |
| Market landscape | `apify/facebook-pages-scraper` | Business page data |
| Niche market sizing | `apify/instagram-hashtag-analytics-scraper` | Hashtag volume |
| Niche content activity | `apify/instagram-hashtag-scraper` | Content trends |
| Hospitality market | `voyager/booking-scraper` | Hotel data + pricing |
| Tourism market | `maxcopell/tripadvisor-reviews` | Review-based insights |

## Search Keywords
`google maps business`, `google trends`, `market research`, `price comparison`, `facebook marketplace`

## Platform Coverage
- **Strong**: Google Maps (business data), Google Trends (search interest), Facebook Marketplace (pricing)
- **Medium**: Instagram (niche sizing via hashtags), Booking.com (hospitality pricing)
- **Limited**: Amazon (separate product Actors needed — search for "amazon scraper")

## Multi-Actor Workflows
| Goal | Step 1 | Step 2 |
|---|---|---|
| Market saturation analysis | `compass/crawler-google-places` → | `apify/google-trends-scraper` |
| Hospitality benchmarking | `voyager/booking-scraper` → | `voyager/booking-reviews-scraper` |
| Niche validation | `apify/instagram-hashtag-analytics-scraper` → | `apify/instagram-hashtag-scraper` |

## Gotchas
- Google Trends returns relative interest (0-100 scale), not absolute search volumes
- Google Maps business counts vary by zoom level and search radius — normalize queries
- Facebook Marketplace data is location-dependent — always specify geographic area
- Booking.com pricing changes daily — snapshot is point-in-time, not historical

## After Completion
Suggest: visualize geographic data on map, compare pricing across regions, validate findings with Google Trends, estimate market size.
