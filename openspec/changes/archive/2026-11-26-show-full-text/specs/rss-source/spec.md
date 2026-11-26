# Spec Delta

## ADDED Requirements

### Requirement: Body keeps the entry's full text
When the source is configured with `full_text`, the article body SHALL be the longest of the entry's `content:encoded` values and its summary, measured as plain text, after the allowlist rebuild. The body SHALL be absent when it adds nothing to the summary: its plain text is no longer than the summary and it holds no image.

#### Scenario: Full text in content:encoded
- **WHEN** an entry has a 100-character summary and a `content:encoded` of three paragraphs with 2,000 characters
- **THEN** the article body holds the three paragraphs
- **AND** the article summary is still the 100-character summary

#### Scenario: Full text in the summary
- **WHEN** an entry has no `content:encoded` and an HTML summary of 1,500 characters
- **THEN** the article summary is cut at 400 characters
- **AND** the article body holds the whole summary as markup

#### Scenario: Source without full_text
- **WHEN** a source without `full_text` reads an entry with a 2,000-character `content:encoded`
- **THEN** the article has no body

#### Scenario: Nothing beyond the summary
- **WHEN** an entry's only text is a 200-character summary
- **THEN** the article has no body

### Requirement: Body is tidied
A text with line breaks or `<br>` and no paragraph tags SHALL become one paragraph per line. A trailing WordPress footer paragraph SHALL be dropped from the body, and so SHALL the image already used as the article image.

#### Scenario: Plain-text lines become paragraphs
- **WHEN** an entry's full text is `<img src="https://c.com/a.jpg" /><br /> Primeira linha\nSegunda linha`
- **THEN** the body is `<p>` with the image, then `<p>Primeira linha</p><p>Segunda linha</p>`

#### Scenario: Cover not repeated
- **WHEN** an entry's article image is `https://cdn.example.com/a.jpg` and its full text starts with `<img src="https://cdn.example.com/a.jpg">`
- **THEN** the body contains no image with that address

### Requirement: Body markup is rebuilt through an allowlist
The body SHALL be rebuilt from parsed feed HTML, never passed through. It SHALL keep only the tags p, br, h2–h4 (h1 as h2, h5–h6 as h4), ul, ol, li, blockquote, pre, code, strong, em, b, i, sub, sup, figure, figcaption, a with `href` and img with `src` and `alt`. Script, style, iframe, object, embed, form, svg, video, audio, noscript, template, button, select and textarea SHALL be dropped with their content; other tags SHALL be dropped and their text kept. Text SHALL be escaped.

#### Scenario: Script and handlers removed
- **WHEN** the full text is `<p onclick="x()">Oi <script>alert(1)</script><iframe src="https://e.com"></iframe></p>`
- **THEN** the body is `<p>Oi </p>`

#### Scenario: Unknown tags unwrapped
- **WHEN** the full text is `<div class="x"><span style="color:red">texto</span></div>`
- **THEN** the body contains `texto` and no div, span, class or style

### Requirement: Body links and images are safe
In the body, `href` and `src` SHALL be resolved against the article URL and kept only when the result is an absolute http(s) URL; a link or image without one SHALL lose the attribute or the image. Links SHALL get `rel="noopener noreferrer"`. Images SHALL get `loading="lazy"`, `referrerpolicy="no-referrer"` and an `alt` (empty when absent). Images whose `width` or `height` is 2 or less SHALL be dropped as tracking pixels.

#### Scenario: Relative image resolved
- **WHEN** an article at `https://site.com/n/1` has `<img src="/f/a.jpg">` in its full text
- **THEN** the body has `<img src="https://site.com/f/a.jpg" alt="" loading="lazy" referrerpolicy="no-referrer">`

#### Scenario: Script link removed
- **WHEN** the full text has `<a href="javascript:alert(1)">clique</a>`
- **THEN** the body has `<a rel="noopener noreferrer">clique</a>`

#### Scenario: Tracking pixel dropped
- **WHEN** the full text has `<img src="https://t.com/p.gif" width="1" height="1">`
- **THEN** the body has no image

## MODIFIED Requirements

### Requirement: Comments-only summary is empty
A summary whose plain text is only the word "Comments" (any case), as aggregators such as Hacker News and Lobsters send, SHALL yield an empty summary. The link statistics that hnrss.org sends ("Article URL: …", "Comments URL: …", "Points: …", "# Comments: …") SHALL be removed from the summary, keeping any other text.

#### Scenario: Aggregator entry
- **WHEN** an entry's summary is `<a href="https://news.example/item?id=1">Comments</a>`
- **THEN** the article summary is empty

#### Scenario: hnrss link entry
- **WHEN** an entry's summary is `<p>Article URL: <a href="https://a.com">https://a.com</a></p><p>Comments URL: <a href="https://news.ycombinator.com/item?id=1">https://news.ycombinator.com/item?id=1</a></p><p>Points: 294</p><p># Comments: 160</p>`
- **THEN** the article summary is empty

#### Scenario: hnrss text entry
- **WHEN** an entry's summary is `<p>Como vocês testam isso?</p><hr><p>Comments URL: <a href="https://news.ycombinator.com/item?id=2">https://news.ycombinator.com/item?id=2</a></p><p>Points: 12</p><p># Comments: 3</p>`
- **THEN** the article summary is `Como vocês testam isso?`
