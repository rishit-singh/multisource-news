import os
import sys
import json

from news import NewsManager
from dotenv import load_dotenv

load_dotenv()

manager = NewsManager(os.getenv("NEWS_KEY"))

manager.GetArticlesByTopic(sys.argv[1])

print(json.dumps(manager.Articles[0], indent=2))

sys.stdout.write(manager.Articles[0]) 


