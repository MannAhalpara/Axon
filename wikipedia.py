import requests

def get_wikipedia_summary(title):
    if not title:
        return "Error: Title cannot be empty."

    # Wikipedia search API to help match the correct page title
    search_url = "https://en.wikipedia.org/w/api.php"
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": title,
        "format": "json"
    }

    search_response = requests.get(search_url, params=search_params)
    if search_response.status_code != 200:
        return f"Error: Search request failed with status code {search_response.status_code}"

    search_data = search_response.json()
    search_results = search_data.get("query", {}).get("search", [])

    if not search_results:
        return f"No results found for '{title}'."

    # Use the first matched title
    page_title = search_results[0]['title']

    # Now fetch the summary
    summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title.replace(' ', '_')}"
    summary_response = requests.get(summary_url)

    if summary_response.status_code == 200:
        summary_data = summary_response.json()
        return summary_data.get("extract", "No summary available.")
    else:
        return f"Error: Failed to fetch summary. Status code {summary_response.status_code}"

