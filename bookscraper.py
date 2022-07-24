#!/usr/bin/env python3 

from bs4 import BeautifulSoup
import requests
from ebooklib import epub


book_author = "AUTHOR_HERE"

# Book details
book_name = "BOOK_TITLE_HERE"
book_url = "https://START_URL_HERE"


# Ending (to test stop condition)
# Put the last chapter you want to scrape here to double check the ending condition.
# book_url = "END_URL_HERE"

def end_condition(next_chapter_name):
    return next_chapter_name == 'Prologue' or next_chapter_name is None

# !!! These next few functions will vary based on which thing you're scraping !!!
# -------------------------------------------------------------------------------
def get_next_chapter(soup):
    next_chapter_url = soup.find(class_="nav-next").find(href=True).attrs['href']
    next_chapter_name = soup.find(class_="nav-next").find(href=True).find("h4").contents[0]
    return (next_chapter_url, next_chapter_name)

def get_chapter_title(soup):
    return soup.find(class_="entry-title").contents[0]

def get_chapter_contents(soup):
    for p in soup.find(class_="entry-content").findAll("p"):
        chapter_contents.append(p.prettify())
    chapter_contents = "\n".join(chapter_contents)
    return chapter_contents
# -------------------------------------------------------------------------------

def get_all_chapters(start_url):
    print("Retrieving chapters...")
    chapters = []
    current_url = start_url

    while True:
        print(current_url)
        page = requests.get(current_url)
        soup = BeautifulSoup(page.text, 'html.parser')

        chapters.append((current_url, soup))

        next_chapter_element = soup.find(class_="nav-next")
        next_chapter_url = None

        if next_chapter_element is None:
            next_chapter_name = None
        else:
            next_chapter_url, next_chapter_name = get_next_chapter(soup)

        if end_condition(next_chapter_name):
            break
        else:
            current_url = next_chapter_url
    print("\n")
    return chapters


def run():
    print(f"Creating epub book: {book_name}. Starting from: {book_url}.")

    chapters = get_all_chapters(book_url)

    book = epub.EpubBook()
    book.set_identifier(book_name.strip(' '))
    book.set_title(book_name)
    book.set_language('en')

    book.add_author(book_author)

    for i, (page, soup) in enumerate(chapters):
        # page = requests.get(url)
        # soup = BeautifulSoup(page.text, 'html.parser')

        chapter_title = get_chapter_title(soup)
        chapter_contents = []

        print(f"Processing chapter: \"{chapter_title}\"...")

        chapter_contents = get_chapter_contents(soup)

        chapter_text = f"<h1>{chapter_title}</h1>\n" + chapter_contents

        epub_chapter = epub.EpubHtml(title=chapter_title,
                                     file_name=f"part_{str(i).zfill(3)}.html",
                                     uid=f"part_{str(i).zfill(3)}",
                                     media_type="application/xhtml+xml")
        epub_chapter.set_content(chapter_text)
        book.add_item(epub_chapter)
        book.toc.append(epub_chapter)
        book.spine.append(epub_chapter)

    print("Writing to epub...")
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    epub.write_epub(f'{book_name}.epub', book)
    print("Done!")


if __name__ == "__main__":
    run()



