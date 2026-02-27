# Lead Generation

## When to use
User wants to find B2B/B2C leads, build prospect lists, enrich contacts, or scrape profiles for sales outreach.

## Suggested Actors
Known good starting points. Always verify via `search-actors` for latest options.

| User Need | Suggested Actor | Why |
|---|---|---|
| Local businesses | `compass/crawler-google-places` | Restaurants, gyms, shops |
| Business emails from Maps | `poidata/google-maps-email-extractor` | Direct email extraction |
| Contact enrichment | `vdrmota/contact-info-scraper` | Emails, phones from URLs |
| Google search discovery | `apify/google-search-scraper` | Broad lead discovery |
| Facebook business pages | `apify/facebook-pages-scraper` | Business contacts |
| Facebook page contacts | `apify/facebook-page-contact-information` | Emails, phones, addresses |
| Facebook groups | `apify/facebook-groups-scraper` | Buying intent signals |
| Instagram profiles | `apify/instagram-profile-scraper` | Creator/business contacts |
| Instagram search | `apify/instagram-search-scraper` | Find by niche |
| TikTok user search | `clockworks/tiktok-user-search-scraper` | Find creators |
| YouTube channels | `streamers/youtube-channel-scraper` | Creator partnerships |

## Search Keywords
`google maps scraper`, `email extractor`, `contact scraper`, `lead generation`, `business scraper`

## Platform Coverage
- **Strong**: Google Maps (structured business data + emails), Facebook (pages + contacts)
- **Medium**: Instagram, TikTok (public profiles, no direct emails usually)
- **Limited**: LinkedIn (no reliable public scraping Actors)
- **Enrichment**: `vdrmota/contact-info-scraper` works on any URL with contact info

## Multi-Actor Workflows
| Goal | Step 1 | Step 2 |
|---|---|---|
| Lead enrichment | `compass/crawler-google-places` → | `vdrmota/contact-info-scraper` |
| Local business + emails | `compass/crawler-google-places` → | `poidata/google-maps-email-extractor` |
| Creator outreach list | `apify/instagram-profile-scraper` → | `vdrmota/contact-info-scraper` |

## Gotchas
- Google Maps results depend heavily on search query + location — be specific ("dentists in Prague" not "dentists")
- Email extractors find publicly listed emails only — no personal email guessing
- Facebook page contact info is only available for pages that filled in their contact details
- GDPR applies — collected contacts may not be usable for cold outreach in EU without legal basis
- Rate limits on Google Maps scraping — large queries may need pagination with `maxCrawledPlaces`

## After Completion
Suggest: deduplicate leads, enrich with additional contact info, export to CRM format (CSV), filter by location/industry.
