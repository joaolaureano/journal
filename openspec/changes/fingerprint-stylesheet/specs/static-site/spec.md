# Spec Delta

## MODIFIED Requirements

### Requirement: Site is self-contained and portable
Publishing SHALL write the stylesheet as `style.css` and as `style.<hash>.css`, `<hash>` being the first 10 hex digits of its SHA-256, and every page SHALL link `style.<hash>.css`, so a changed stylesheet is a new file that no cache holds. Pages SHALL use only relative links to other pages and to the stylesheet, declare `pt-BR` and include no scripts, so the site works from disk and from any static host.

#### Scenario: Pages use relative links
- **WHEN** a site is published
- **THEN** `style.css` and `style.<hash>.css` exist and every page references the latter with a relative path
- **AND** no page contains a `<script>` element or an absolute link to another page of the site

#### Scenario: Changed stylesheet, new file
- **WHEN** the stylesheet's content changes between two publications
- **THEN** the second publication's pages link a stylesheet file with a different name

### Requirement: News and articles tabs
Both list pages SHALL show, between the edition date and the section index, a navigation labelled "Notícias" and "Artigos" linking to `index.html` and `artigos.html` of the same folder, with `aria-current="page"` on the page's own tab.

#### Scenario: Tabs on the articles page
- **WHEN** an edition is published
- **THEN** its `artigos.html` has a link to `index.html` and a link to `artigos.html` marked `aria-current="page"`

#### Scenario: Tabs below the edition date
- **WHEN** an edition with sections is published
- **THEN** in its `index.html` the tabs come after "Edição de" and before the section index
