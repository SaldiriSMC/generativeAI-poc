import os

import wikipedia

# Create a folder to store text files
os.makedirs("wikipedia_documents_data", exist_ok=True)


def wiki_docs(name):
    """
    Get documents from Wikipedia
    """
    try:
        print(f'Topic Name: {name}')
        abc = wikipedia.WikipediaPage(name)
    except:
        try:
            try:
                try:
                    try:
                        abc = wikipedia.WikipediaPage(name.lower())
                    except:
                        abc = wikipedia.WikipediaPage(name.split(" ")[0])
                except:
                    abc = wikipedia.WikipediaPage((name.split(" ")[0]).lower())
            except:
                abc = wikipedia.WikipediaPage('All pages with titles containing ' + name.split(" ")[0].lower())
        except:
            abc = wikipedia.WikipediaPage(name.split(" ")[0] + ' (TV series)')
    try:
        abc = abc.content
        if abc:
            filename = f"wikipedia_documents_data/{name.replace(' ', '_')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(abc)
        else:
            print(f"Page '{name}' does not exist.")
    except Exception as e:
        print(f"Error: {e}")


# Example: List of relevant pages to collect
topics = [
    "ChatGPT", "Artificial Intelligence", "Machine Learning",
    "Quantum Computing", "Natural Language Processing",
    "History of the Internet", "Alan Turing", "2023 Cricket World Cup",
    "Indian Premier League", "Oppenheimer (film)",
    "J. Robert Oppenheimer", "Barbie (film)", "Taylor Swift",
    "Cristiano Ronaldo", "Lionel Messi", "Russian Invasion of Ukraine",
    "United States", "India", "Elon Musk", "Matthew Perry",
    "Lisa Marie Presley", "Avatar: The Way of Water",
    "The Last of Us (TV series)", "Andrew Tate", "Guardians of the Galaxy Vol. 3",
    "Deaths in 2023", "Barack Obama", "COVID-19 pandemic", "SpaceX",
    "Bitcoin", "Climate Change", "Black Holes", "Human Evolution",
    "Metaverse", "Augmented Reality", "Mars Exploration", "Apollo 11",
    "Nobel Prize", "Stock Market Crash", "NATO", "World War II",
    "Cold War", "United Nations", "European Union", "NASA",
    "International Space Station", "Electric Vehicles",
    "Nikola Tesla", "Tesla (unit)",
    "Renewable Energy", "Plastic Pollution",
    "Mental Health Awareness",
    "Global Warming", "Cryptocurrency", "OpenAI", "Neural Networks",
    "Blockchain", "Facebook", "Google", "Apple Inc.",
    "Amazon (company)",
    "Microsoft", "Cloud Computing", "Cybersecurity",
    "5G",
    "Internet of Things", "Big Data", "Data Science",
    "Gene Editing",
    "CRISPR", "Vaccines", "Artificial Organs", "Stem Cell Research",
    "Virtual Reality", "Robotics", "3D Printing", "Smart Cities",
    "Self-Driving Cars", "Electric Aircraft", "Space Tourism",
    "Terraforming", "Deepfakes",
    "Cyber Warfare", "Surveillance",
    "Hackers", "Encryption", "Social Media Influence", "YouTube",
    "TikTok", "Instagram", "Twitter", "Memes", "Video Games",
    "eSports", "Augmented Reality Games", "Streaming Services",
    "Netflix", "Disney+", "HBO Max", "Amazon Prime",
    "Sports Events", "FIFA World Cup", "Olympics", "Formula 1",
    "Wimbledon, London",
    "Tour de France", "Artificial Photosynthesis",
    "Fusion Energy", "Quantum Biology", "Extraterrestrial Life",
    "SETI", "Hubble Space Telescope", "James Webb Space Telescope",
    "Dark Matter", "Dark Energy", "Astrobiology", "Exoplanets",
    "Interstellar Travel", "Multiverse", "Time Travel",
    "Philosophy of Science", "Ethics of AI", "Transhumanism",
    "Futurology", "Evolutionary Psychology", "Anthropology",
    "Cultural Studies", "World History", "Ancient Civilizations",
    "Egyptian Pyramids", "Roman Empire", "Greek Mythology",
    "Chinese Dynasties", "Indian History", "African Kingdoms",
    "American Civil War", "Industrial Revolution", "Scientific Revolution",
    "Renaissance", "Medieval Europe", "World War I",
    "Holocaust", "Space Race", "Cold War Politics", "Berlin Wall",
    "Cuban Missile Crisis", "Vietnam War", "Persian Gulf War",
    "War on Terror", "Arab Spring", "Brexit", "Globalization",
    "Human Rights", "Women’s Suffrage",
    "Civil Rights Movement", "Black Lives Matter", "Me Too Movement",
    "Modern Art", "Renaissance Art", "Abstract Art", "Photography",
    "Film Industry",
    "Hollywood, Los Angeles", "Bollywood", "K-pop", "Anime",
    "Manga", "Music Genres", "Rock Music", "Pop Music", "Hip-Hop",
    "Classical Music", "Jazz", "Blues", "Electronic Music",
    "Folk Music", "Opera", "Musical Instruments", "Piano", "Guitar",
    "Violin", "Drums", "Sculpture", "Architecture",
    "Gothic Architecture", "Baroque Architecture",
    "Modern Architecture", "Sustainable Architecture", "Green Technology",
    "Environmental Conservation", "Wildlife Preservation",
    "National Parks", "Marine Life", "Ocean Conservation",
    "Coral Reefs", "Forest Conservation", "Renewable Resources",
    "Hydropower", "Wind Energy", "Solar Energy"
]
# print(len(topics))
# # Loop through and save content for each topic
# for topic in topics:
#     wiki_docs(topic)
