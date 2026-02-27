# Audience Analysis

## When to use
User wants to understand audience demographics, follower behavior, engagement quality, or audience composition across social platforms.

## Suggested Actors
Known good starting points. Always verify via `search-actors` for latest options.

| User Need | Suggested Actor | Why |
|---|---|---|
| Facebook follower lists | `apify/facebook-followers-following-scraper` | Follower/following data |
| Facebook engagement | `apify/facebook-likes-scraper` | Reaction type analysis |
| Facebook comments | `apify/facebook-comments-scraper` | Comment sentiment |
| Instagram profile demographics | `apify/instagram-profile-scraper` | Bio, follower counts |
| Instagram follower tracking | `apify/instagram-followers-count-scraper` | Growth over time |
| Instagram comment sentiment | `apify/instagram-comment-scraper` | Engagement quality |
| Instagram geo-tagged audience | `apify/instagram-search-scraper` | Location-based |
| YouTube viewer feedback | `streamers/youtube-comments-scraper` | Comment analysis |
| YouTube channel subscribers | `streamers/youtube-channel-scraper` | Channel metrics |
| TikTok follower demographics | `clockworks/tiktok-followers-scraper` | Follower lists |
| TikTok profile analysis | `clockworks/tiktok-profile-scraper` | Profile demographics |

## Search Keywords
`facebook followers`, `instagram audience`, `tiktok followers`, `youtube subscribers`, `social media demographics`

## Platform Coverage
- **Strong**: Instagram, Facebook, TikTok (direct follower/engagement data)
- **Limited**: YouTube (no direct follower list, only channel metrics and comments)
- **Gap**: LinkedIn (no public scraping Actors available)

## Multi-Actor Workflows
| Goal | Step 1 | Step 2 |
|---|---|---|
| Audience quality audit | `apify/instagram-profile-scraper` → | `apify/instagram-comment-scraper` |
| Cross-platform comparison | Platform-specific profile scraper → | Compare metrics manually |
| Engagement deep-dive | `apify/facebook-posts-scraper` → | `apify/facebook-comments-scraper` |

## Gotchas
- Follower lists on Instagram are rate-limited — expect partial results for large accounts
- Facebook follower scraping requires public pages; private profiles return nothing
- "Audience demographics" is inferred from public data (bios, locations), not platform analytics
- TikTok follower counts update with delay — don't compare snapshots taken minutes apart

## After Completion
Suggest: segment by engagement rate, compare audience overlap across platforms, track growth over time with scheduled runs.
