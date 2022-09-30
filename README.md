# NLP_Assignment_1
## Assignment description
* Collect sufficient data in both Chinese and English
* Clean data
* Calculate the entropy of characters or tokens
## Environment
    python 3.8 + ubuntu 18.4
    request    
    bs4
## Data
[baiduwangpan](https://pan.baidu.com/s/1c3FuHOqSfun5uCQWcYWvxg?pwd=tysb)

pwd =  tysb
## Usage
### web_crawler
web_crawl.py for baike, wiki and novel. try:

    python web_crawl.py --N 2000 --home_url "http://baike.baidu.com/view/"
    
crawl_novel.py for novels in both Chainese and Enlish. try:

    python crawl_novel.py --language zh  
    
### calculate entropy
try

    python calculate_entropy --entropy_type characters --language zh



 
