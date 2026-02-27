# Trend Analysis

## When to use
User wants to discover emerging trends, track viral content, identify trending topics, or inform content strategy.

## Suggested Actors
Known good starting points. Always verify via `search-actors` for latest options.

| User Need | Suggested Actor | Why |
|---|---|---|
| Search trends | `apify/google-trends-scraper` | Google Trends data |
| Instagram hashtag content | `apify/instagram-hashtag-scraper` | Hashtag trends |
| Instagram hashtag metrics | `apify/instagram-hashtag-analytics-scraper` | Performance stats |
| Instagram trending discovery | `apify/instagram-search-scraper` | Search trends |
| Instagram visual trends | `apify/instagram-post-scraper` | Post analysis |
| Facebook product trends | `apify/facebook-marketplace-scraper` | Marketplace activity |
| Facebook community trends | `apify/facebook-groups-scraper` | Group discussions |
| YouTube Shorts trends | `streamers/youtube-shorts-scraper` | Short-form video trends |
| YouTube hashtag videos | `streamers/youtube-video-scraper-by-hashtag` | Hashtag content |
| TikTok hashtag content | `clockworks/tiktok-hashtag-scraper` | Hashtag trends |
| TikTok trending sounds | `clockworks/tiktok-sound-scraper` | Audio trends |
| TikTok trending content | `clockworks/tiktok-trends-scraper` | Viral content |
| TikTok discover page | `clockworks/tiktok-discover-scraper` | Discover trends |

## Search Keywords
`google trends`, `trending hashtags`, `tiktok trends`, `viral content`, `social media trends`

## Platform Coverage
- **Strong**: Google Trends (search interest), TikTok (trends, sounds, discover), Instagram (hashtags)
- **Medium**: YouTube (shorts, hashtag videos), Facebook (marketplace, groups)
- **Gap**: Twitter/X trends (Actors change frequently — search for latest)

## Multi-Actor Workflows
| Goal | Step 1 | Step 2 |
|---|---|---|
| Cross-platform trend validation | `apify/google-trends-scraper` → | `apify/instagram-hashtag-analytics-scraper` |
| Content opportunity finding | `clockworks/tiktok-trends-scraper` → | `clockworks/tiktok-hashtag-scraper` |
| Seasonal trend tracking | `apify/google-trends-scraper` → | Platform-specific content scraper |

## Gotchas
- Google Trends data has 24-48h delay for real-time trends; use "past 7 days" for freshest data
- TikTok trends are extremely volatile — what's trending now may not be in 2 hours
- Instagram hashtag stats show cumulative posts, not recent velocity — combine with hashtag content scraper
- Trending sounds on TikTok require specific sound URLs, not search queries

## After Completion
Suggest: compare trend across platforms, identify content opportunities, track trend velocity over time, create content calendar based on findings.
