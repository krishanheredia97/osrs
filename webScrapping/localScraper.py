from bs4 import BeautifulSoup
import re

def parse_osrs_wiki_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    content = []

    for element in soup.find_all(['h2', 'h3', 'p', 'ul']):
        if element.name in ['h2', 'h3']:
            headline = element.find('span', class_='mw-headline')
            if headline:
                content.append((element.name, headline.text.strip(), headline.get('id', '')))
        elif element.name == 'p':
            content.append(('p', element.text.strip()))
        elif element.name == 'ul':
            list_items = []
            for li in element.find_all('li'):
                item_content = []
                for child in li.children:
                    if child.name == 'a':
                        item_content.append(('link', child.get('title', child.text)))
                    elif child.name == 'code':
                        item_content.append(('code', child.text))
                    elif child.name == 'i':
                        item_content.append(('i', child.text))
                    elif isinstance(child, str) and child.strip():
                        item_content.append(('text', child.strip()))
                list_items.append(item_content)
            content.append(('ul', list_items))

    return content

def save_to_markdown(content, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            for item in content:
                if item[0] == 'h2':
                    file.write(f"## {item[1]} {{#{item[2]}}}\n\n")
                elif item[0] == 'h3':
                    file.write(f"### {item[1]} {{#{item[2]}}}\n\n")
                elif item[0] == 'p':
                    file.write(f"{item[1]}\n\n")
                elif item[0] == 'ul':
                    for list_item in item[1]:
                        file.write("- ")
                        for part in list_item:
                            if part[0] == 'link':
                                file.write(f"[{part[1]}] ")
                            elif part[0] == 'code':
                                file.write(f"`{part[1]}` ")
                            elif part[0] == 'i':
                                file.write(f"*{part[1]}* ")
                            else:
                                file.write(f"{part[1]} ")
                        file.write("\n")
                    file.write("\n")

        print(f"Content successfully saved to {filename}")

    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")

def main():
    try:
        with open('html.txt', 'r', encoding='utf-8') as file:
            html_content = file.read()
    except IOError as e:
        print(f"An error occurred while reading the file: {e}")
        return

    filename = "Merchanting.md"

    content = parse_osrs_wiki_content(html_content)

    if content:
        save_to_markdown(content, filename)
    else:
        print("Failed to parse content. Please check the HTML and try again.")

if __name__ == "__main__":
    main()