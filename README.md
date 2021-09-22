# DramaticaAnnotationTool

This is a study project for Helsinki University course. I have a long term goal building a dramatic arc anlyzing AI by using [BERT][1] and top-down causal framework by combining the works of [Mark Riedl][2], [George F. R. Ellis][3] and [Dramatica Writing Theory][4]. Part of that project is to annotate characters of stories (from project [Gutenberg][5]) with Dramatica archetypes and then produce a bottom-up causal micro state sequence by using BERT to annotate [character-event pairs of Dramatica][6]. This can be done similarly as has been done at RocStories dataset whitepapers for sentiment analysis ([BERT produces character-sentiment pairs][7]). My hypothesis is that this micro state sequence can be used with data mining and STRIPS style algorithms using the fractal theme models of Dramatica to produce macro states and ultimately predict some important Dramatica based features of stories.

However, this project will focus on the first part, which is annotating the characters per story and then hopefully if I have time to develop also annotation tool for possible character-event pairs from paragraphs of the story.

## Features

 * The user gets an anonymous annotation token (which maybe can be registered; maybe also add Are You A Robot feature and possibility to register; considering GDPR related problems here)
 * The user can browse random annotation tasks (either character archetype annotation or paragraph character-event annotation)
 * The user can navigate to a specific book and paragraph and annotate there
 * The admin can use console script to upload new books and to automatically extract a set of probable characters
 * A user can suggest new characters
 * The system will query things to be annotated for the users by limits of "enough annotations" and "priorities"
 * High priority paragraphs or characters can be set by the admin; these will get more annotations from users
 * Admin can classify reliability of registered users (through command line scripts perhaps)

[1]: https://arxiv.org/abs/1810.04805 
[2]: https://mark-riedl.medium.com/an-introduction-to-ai-story-generation-7f99a450f615 
[3]: https://www.youtube.com/watch?v=nEhTkF3eG8Q 
[4]: https://dramatica.com/theory/book 
[5]: https://www.gutenberg.org/ 
[6]: https://dramatica.com/theory/book/characters 
[7]: https://arxiv.org/pdf/2006.05489.pdf?fbclid=IwAR3sJCFRes5Gf4XKV7BqyjWAbeM5pZ0FcQZpzhyXTX3wzxmDdrEoy40l5cI 

## Testing

To init the database with real books, you can run the scripts at `admin_tools` (work in progress). The `download-100.sh` script will download top 100 eBooks from project Gutenberg and `extract-characters.sh` is a simple script for extracting candidate tokens that might be important characters in the story. I will also create a title extraction script and paragraph extraction scripts.

For now it is perhaps best used so that first download the books and then upload them to the `static/books` directory:
```
cd admin_tools
./download-100.sh
cp gutenberg/* ../static/books/
```

To run the app:
```
sudo service postgresql start
flask run
```

Follow the link and try the "/books" section