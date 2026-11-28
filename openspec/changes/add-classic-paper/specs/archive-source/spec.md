## ADDED Requirements

### Requirement: One archived post per day
The archive source SHALL be configured with a feed location, a source name and the number of archive pages. Fetching SHALL read one page of the feed's archive, adding `paged=<n>` to the location's query, and return one article from it, marked evergreen. The page and the post SHALL be chosen from the current date alone, so that fetches on the same date return the same post and consecutive dates return different posts until every page has been used.

#### Scenario: Same day, same post
- **WHEN** the archive source is fetched twice on the same date
- **THEN** both fetches return the same post, marked evergreen

#### Scenario: Next day, next post
- **WHEN** the archive source is fetched on two consecutive dates with 108 pages
- **THEN** the two posts come from different pages

### Requirement: Archive failures are source failures
When the chosen archive page cannot be fetched or has no valid entry, fetching SHALL raise the source error naming the feed location, as the RSS source does.

#### Scenario: Missing page
- **WHEN** the chosen page answers HTTP 404
- **THEN** fetching raises the source error and the other sources still publish
