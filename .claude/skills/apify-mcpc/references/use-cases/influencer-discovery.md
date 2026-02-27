# Influencer Discovery

## When to use
User wants to find influencers, evaluate them for brand partnerships, verify authenticity, or track collaboration performance.

## Suggested Actors
Known good starting points. Always verify via `search-actors` for latest options.

| User Need | Suggested Actor | Why |
|---|---|---|
| Instagram profiles | `apify/instagram-profile-scraper` | Bio, followers, engagement |
| Find by hashtag | `apify/instagram-hashtag-scraper` | Discover by niche hashtags |
| Find by keyword | `apify/instagram-search-scraper` | Search by niche/keyword |
| Brand tag network | `apify/instagram-tagged-scraper` | Who already tags brands |
| Reel engagement | `apify/instagram-reel-scraper` | Reel performance metrics |
| Facebook content creators | `apify/facebook-posts-scraper` | Post performance |
| Facebook niche groups | `apify/facebook-groups-scraper` | Find influencers in groups |
| YouTube creators | `streamers/youtube-channel-scraper` | Channel metrics |
| TikTok influencers | `clockworks/tiktok-scraper` | Comprehensive TikTok data |
| TikTok user search | `clockworks/tiktok-user-search-scraper` | Find users by keywords |
| ~~TikTok live streamers~~ | ~~`clockworks/tiktok-live-scraper`~~ | **DEPRECATED** — use `search-actors` for alternatives |

## Search Keywords
`instagram influencer`, `tiktok creator`, `youtube channel`, `social media profile`, `influencer scraper`

## Platform Coverage
- **Strong**: Instagram (profiles, hashtags, search), TikTok (profiles, search, trends)
- **Medium**: YouTube (channel data, no direct influencer search)
- **Limited**: Facebook (page-level data, not personal profiles)
- **Gap**: LinkedIn influencers (no public scraping)

## Multi-Actor Workflows
| Goal | Step 1 | Step 2 |
|---|---|---|
| Influencer vetting | `apify/instagram-profile-scraper` → | `apify/instagram-comment-scraper` |
| Niche discovery | `apify/instagram-hashtag-scraper` → | `apify/instagram-profile-scraper` |
| Cross-platform audit | Instagram profile scraper → | TikTok profile scraper |

## Gotchas
- Follower count alone is misleading — check engagement rate (comments/likes vs followers)
- Instagram search scraper finds public accounts only; many influencers have creator/business accounts (still public)
- Fake follower detection requires comment analysis, not just follower counts
- TikTok user search returns different results than hashtag search — try both approaches

## After Completion
Suggest: filter by engagement rate thresholds, verify authenticity via comment quality analysis, create shortlist with contact info.
