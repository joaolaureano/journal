# Proposal

## Why

Pages link `style.css?v=<hash>`, but the CloudFront distribution uses the managed CachingOptimized policy, whose cache key ignores query strings, and `style.css` is served with a one-year immutable cache. Edge locations therefore keep serving an old stylesheet whatever the `?v=` says: the news and articles tabs show up unstyled in the published site. Separately, the tabs sit above the edition date, and they belong below it, right above the section index.

## What Changes

- Publishing writes the stylesheet a second time as `style.<hash>.css`, named after the start of its SHA-256, and pages link that file. A changed stylesheet is a new key, so no cache, CDN or browser, can serve an old one. `style.css` keeps being written for pages published before this change.
- The tabs move below "Edição de …" and above the section index.
- One-off: invalidate `/style.css` in CloudFront so older pages get the current stylesheet.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `static-site`: the stylesheet link names a fingerprinted file; the tabs' position.

## Impact

- `adapters/static_site.py`, `templates/base.html`, `templates/index.html`, `templates/style.css`, tests.
- No infrastructure change: the distribution and its cache policy stay as they are.
