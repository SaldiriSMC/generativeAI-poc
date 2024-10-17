import wikipedia


def wiki_docs(name):
    """
    Get documents from Wikipedia
    """
    abc = wikipedia.summary(name)
    print(abc)


wiki_docs('AI')
