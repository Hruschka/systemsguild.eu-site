---
title: Culture at Work
permalink: /culture-at-work/
wp_id: 374
---
# **The blog accompanying our book [“Happy to Work Here”](https://www.amazon.com/dp/B08VHP27WP)**

![Culture at Work]({{ '/assets/uploads/2021/05/linkedIn-banner-photo.jpeg' | relative_url }})

{% assign post = site.posts.first %}
## [{{ post.title }}]({{ post.url | relative_url }})

{{ post.content }}

{% include post-meta.html page=post %}

## All Culture Killers

{% include post-list.html posts=site.posts %}
