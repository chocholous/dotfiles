# Brand Monitoring

## When to use
User wants to track reviews, ratings, sentiment, brand mentions, or customer feedback across platforms.

## Suggested Actors
Known good starting points. Always verify via `search-actors` for latest options.

| User Need | Suggested Actor | Why |
|---|---|---|
| Google Maps reviews | `compass/Google-Maps-Reviews-Scraper` | Dedicated review scraping |
| Google Maps business data | `compass/crawler-google-places` | Business reviews + ratings |
| Booking.com reviews | `voyager/booking-reviews-scraper` | Hotel review details |
| TripAdvisor reviews | `maxcopell/tripadvisor-reviews` | Attraction/restaurant reviews |
| Facebook reviews | `apify/facebook-reviews-scraper` | Page reviews |
| Facebook comment monitoring | `apify/facebook-comments-scraper` | Post comments |
| Instagram comment sentiment | `apify/instagram-comment-scraper` | Comment analysis |
| Instagram hashtag monitoring | `apify/instagram-hashtag-scraper` | Brand hashtag tracking |
| Instagram brand tags | `apify/instagram-tagged-scraper` | Who tags the brand |
| YouTube comment sentiment | `streamers/youtube-comments-scraper` | Video comments |
| TikTok comment analysis | `clockworks/tiktok-comments-scraper` | TikTok sentiment |

## Search Keywords
`reviews scraper`, `brand mentions`, `sentiment analysis`, `google maps reviews`, `social media monitoring`

## Platform Coverage
- **Strong**: Google Maps, Booking.com, TripAdvisor (structured review data)
- **Strong**: Instagram, Facebook (mentions, tags, comments)
- **Limited**: Twitter/X (Actors change frequently — always search for latest)
- **Gap**: Yelp (limited Actor availability)

## Multi-Actor Workflows
| Goal | Step 1 | Step 2 |
|---|---|---|
| Review aggregation | `compass/Google-Maps-Reviews-Scraper` → | `voyager/booking-reviews-scraper` |
| Brand mention audit | `apify/instagram-hashtag-scraper` → | `apify/instagram-tagged-scraper` |
| Competitor review comparison | Review scraper for own brand → | Same scraper for competitor |

## Gotchas
- Google Maps reviews are sorted by relevance by default — specify sort order if you need newest
- Review scrapers return text but no built-in sentiment — agent must analyze sentiment from text
- Instagram hashtag monitoring catches public posts only; stories mentioning the brand are invisible
- Booking.com review scraping needs exact hotel URLs, not search queries

## After Completion
Suggest: sentiment analysis on collected reviews, compare ratings across platforms, set up recurring monitoring with scheduled runs.
