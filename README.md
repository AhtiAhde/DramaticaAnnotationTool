# DramaticaAnnotationTool

This is a study project for Helsinki University course. I have a long term goal building a dramatic arc anlyzing AI by using [BERT][1] and top-down causal framework by combining the works of [Mark Riedl][2], [George F. R. Ellis][3] and [Dramatica Writing Theory][4]. Part of that project is to annotate characters of stories (from project [Gutenberg][5]) with Dramatica archetypes and then produce a bottom-up causal micro state sequence by using BERT to annotate [character-event pairs of Dramatica][6]. This can be done similarly as has been done at RocStories dataset whitepapers for sentiment analysis ([BERT produces character-sentiment pairs][7]). My hypothesis is that this micro state sequence can be used with data mining and STRIPS style algorithms using the fractal theme models of Dramatica to produce macro states and ultimately predict some important Dramatica based features of stories.

However, this project will focus on the first part, which is annotating the characters per story and then hopefully if I have time to develop also annotation tool for possible character-event pairs from paragraphs of the story.

## Current Version

Currently the admin panel and book import features are disabled from Heroku as there is no proper filesystem and S3 buckets must be used instead (or something similar). For this reason only the books section is enabled on the web UI. You can see a list of books and automatically detected characters for each book. No annotation enabled yet.

## Full Feature Set

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

## Local Testing

To init the database with real books, you can run the scripts at `admin_tools` (work in progress). The `download-100.sh` script will download top 100 eBooks from project Gutenberg and `extract-characters.sh` is a simple script for extracting candidate tokens that might be important characters in the story. I will also create a title extraction script and paragraph extraction scripts.

For now it is perhaps best used so that first download the books and then upload them to the `static/books` directory:
```
./admin-tools/download-100.sh
```
Or you can also upload only a few books by Project Gutenberg id's by using:
```
./admin-tools/download-id.sh :id_here:
```
Heroku Hobby tier only allows 10,000 database rows and one book has ~2,000 paragraph database rows in average. Heroku also lacks file system and for that reason instead of using S3 buckets I upload the data as psql dump import (I will add S3 support later after the course).

I run the book imports locally with `MASTER_MODE=enabled` enabled (at `.env`) and at Heroku `MASTER_MODE=enabled` (or just empty). I have been using these commands to move the local paragraphs to the Heroku environment:
```
pg_dump postgres -O -x > import.psql
heroku psql < import.psql
```


Set environment variables for the local testing `.env`:
```
DATABASE_URL=postgresql:///postgres
SECRET_KEY=123334445645665
ADMIN_USER=some user name
ADMIN_PASSWORD=some pass word
MASTER_MODE=enabled
```

To run the app:
```
sudo service postgresql start
flask run
```

Follow the link in console and try the "/admin" and "/books" section

## Notion about usability

While the software should also be visually functional in usability sense, for annotation tools we are also pushed against "effort vs value produced" per user. This means that part of the usability is the problem of having high frequency of relevant paragraphs. I will implement Adaptive Fractal Analysis algorithm for building the priorities for paragraphs on separate course.

## TODO's

* Promises and Payoffs should have "same as MICE start / end", which would disable the text box and copy the content of MICE description as value of the PPP annotation.
* Mark to the paragraphs if they have dialogue or not. Also add word count and char count.
* Create Dramatica module (writing tool)
* Add previous and next paragraphs features to the annotation view
* Make list of all Gutenberg books that have movies made of them (maybe later add movie annotation tool; timeline based; notes that can then be turned to proper annotations)

## TODO's for initial release

* Windowing should match BERT's token limit (512). A window has max size of 512 words / tokens. We might want to choose a bit lower limit to avoid problems (like 450). Of course this can also be done in preprocessing step and we could just prefer best usability.
* Also the methods for further analysis might depend on constant token amount in learning data (I believe paragraphs might contain useful data structures for MAUI like learners). I believe no matter what we must give more context to the user, so the final solution will be a mesh up of specific length utterances divided for paragraphs anyway.
* It seems like back tracking which characters are acted on in a section of text is important; some automation might be good idea for this (assuming narrator voice tells about protagonist / active voice character; pronouns should refer to mentioned characters in specific manners, for example "you" refers to active character in scene, while "he/her" might refer to other important characters); annotation of characters per pronoun might be useful.

## TODO's for social features

* The dramatic arcs ought to be shared. However, deleting or editing a shared dramatic arc would be problematic. Instead the social features will be based on social negotiations about the correct format.
* Community Proposal will be a social global suggestion, a bit like Reddit or Stackoverflow posts.
* When a user has annotated overlapping paragraphs with another user a Community Proposal suggestion is made
* When a user has annotated paragraphs that belong to Community Proposal, they are suggested to import or merge their contributions
* A Community Proposal could be a collection of voted components of which one is chose as the official or "primary" (I think "secondaries" etc. different interpretations would be beneficial)