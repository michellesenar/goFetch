# goFetch
scrapy project to crawl Helen Woodward shelter's adoptable dogs

### run at top level

#### fetching all dogs
`scrapy crawl fetch -o all_dogs.csv`

#### fetching labs
`scrapy crawl fetch -a breeds=lab -o labs.csv`

#### fetching labs or terriers
`scrapy crawl fetch -a breeds=lab,terrier -o lab_terrier.csv`
