from tools.resource_tools import find_relevant_youtube_resource, scrape_and_find_relevant_section


def test_pipeline():
    # YouTube
    youtube_result = find_relevant_youtube_resource("how to solder an LED")
    print("YouTube:", youtube_result)

    # Article
    article_result = scrape_and_find_relevant_section(
        "https://en.wikipedia.org/wiki/Soldering",
        "how to solder an LED"
    )
    print("Article:", article_result)

if __name__ == "__main__":
    test_pipeline()