# Content Analytics

## When to use
User wants to track engagement metrics, measure campaign ROI, analyze content performance, or audit content strategy across platforms.

## Suggested Actors
Known good starting points. Always verify via `search-actors` for latest options.

| User Need | Suggested Actor | Why |
|---|---|---|
| Instagram post metrics | `apify/instagram-post-scraper` | Likes, comments, shares |
| Instagram reel performance | `apify/instagram-reel-scraper` | Reel analytics |
| Instagram hashtag performance | `apify/instagram-hashtag-scraper` | Branded hashtags |
| Instagram follower growth | `apify/instagram-followers-count-scraper` | Growth tracking |
| Facebook post performance | `apify/facebook-posts-scraper` | Post engagement |
| Facebook reaction analysis | `apify/facebook-likes-scraper` | Reaction types |
| Facebook Reels metrics | `apify/facebook-reels-scraper` | Reels performance |
| Facebook ad performance | `apify/facebook-ads-scraper` | Ad analytics |
| YouTube video metrics | `streamers/youtube-scraper` | Views, likes, comments |
| YouTube Shorts analytics | `streamers/youtube-shorts-scraper` | Shorts performance |
| TikTok content metrics | `clockworks/tiktok-scraper` | Video analytics |
| TikTok video details | `clockworks/tiktok-video-scraper` | Individual videos |

## Search Keywords
`instagram post scraper`, `facebook engagement`, `youtube video metrics`, `tiktok analytics`, `social media analytics`

## Platform Coverage
- **Strong**: Instagram (posts, reels, hashtags), Facebook (posts, ads, reactions)
- **Strong**: YouTube (videos, shorts), TikTok (videos, profiles)
- **Gap**: Cross-platform unified metrics (must combine manually)

## Multi-Actor Workflows
| Goal | Step 1 | Step 2 |
|---|---|---|
| Campaign performance | `apify/instagram-post-scraper` → | `apify/instagram-comment-scraper` |
| Content format comparison | `apify/instagram-post-scraper` → | `apify/instagram-reel-scraper` |
| Ad effectiveness audit | `apify/facebook-ads-scraper` → | `apify/facebook-posts-scraper` |

## Gotchas
- Engagement rates are not returned directly — calculate from likes/comments vs follower count
- Instagram post scraper needs post URLs or profile URLs, not keywords
- YouTube view counts update with delay; very recent videos show lower counts
- TikTok video metrics can fluctuate significantly within first 48 hours of posting

## After Completion
Suggest: calculate engagement rates, compare across content types (posts vs reels vs stories), identify top-performing content patterns.
