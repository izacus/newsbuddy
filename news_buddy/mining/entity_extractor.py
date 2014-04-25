import json
import logging
import requests
import settings

logger = logging.getLogger("entityextractor")


class EntityExtractor():

    def __init__(self):
        if settings.NER_SERVICE_URL is not None:
            self.tag_url = settings.NER_SERVICE_URL + "/tag"

    def tag(self, text):
        if settings.NER_SERVICE_URL is None: return None

        response = requests.post(self.tag_url, data=json.dumps({"text": text}))
        if response.status_code != requests.codes.ok:
            logger.warning("Failed to access NER service: [%d] %s" % (response.status_code, response.content, ))
            return None

        # Process tags now
        last_tag = None
        last_entity = ""

        tags = set()

        for word in response.json():
            tag = word[u"tag"] if u"tag" in word else None
            if tag != last_tag and last_tag is not None:
                tags.add((last_entity.strip(), last_tag))
                last_entity = ""

            if tag is not None:
                last_entity += " " + word[u"word"]

            last_tag = tag

        if len(tags) == 0:
            return None

        return list(tags)
