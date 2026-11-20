# Web research

Use BrowserControl to search a site and read the results. For example, ask your
agent to find the Wikipedia article about Python and identify its creator.

## Search the site

1. Open the site with `navigate_to("https://wikipedia.org")`.
2. Find the search field in the latest element map. Call `type_text` with that
   ID and the query `"Python programming language"`.
3. Submit with `press_key("Enter")`. If a results page opens, locate the
   relevant result in the returned map and use `click` with its current ID.

## Read and summarize

Use [`get_page_content()`](../tools/content.md#get_page_content) to read the
page as Markdown. Verify the answer against the page and include the source URL.
[`get_page_info()`](../tools/content.md#get_page_info) returns the current
URL and title.

Page content is capped at 30,000 characters. For a long page, scroll to the
section you need. If the relevant text belongs to a numbered element, use
[`get_text(element_id)`](../tools/content.md#get_text) to read it directly.

For work that spans several sources, see [multi-tab research](multi-tab.md).
