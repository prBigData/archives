import requests
from lxml import html
import json
import logging
import time


# paths to the info in the doc
X_PATHS = {
    'IMO': '//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/div[1]/div[1]/b/text()',
    'MMSI': '//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/div[1]/div[2]/b/text()',
    'Call_Sign': '//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/div[1]/div[3]/b/text()',
    'Flag': '//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/div[1]/div[4]/b/text()',
    'AIS_Vessel_Type': '//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/div[1]/div[5]/b/text()',
    'Gross_Tonage': '//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/div[2]/div[1]/b/text()',
    'Deadweight': '//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/div[2]/div[2]/b/text()',
    'LOxBE': '//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/div[2]/div[3]/b/text()',
    'Year_Built': '//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/div[2]/div[4]/b/text()',
    'Status': '//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/div[2]/div[5]/b/text()',
    'DEPARTURE': '//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/@title',
    'ARRIVAL': '//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/@title',
    'ATD': '//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/text()[2]',
    'ETA_ATA_check': '//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[2]/div[1]/b/span/text()',
    'ETA_ATA': '//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[2]/div[1]/span/text()'
}

logging.basicConfig(filename="mmsi_log.log", level=logging.INFO)


class Spider(object):
    """Our spider class"""

    urls = list()
    responses = list()
    export = None
    vessels = list()
    sleep_delay = None

    def __init__(self, urls, sleep_delay=None, export=None):
        super(Spider, self).__init__()
        self.urls = urls
        self.export = export
        self.sleep_delay = sleep_delay

    def scrap(self):
        """makes the requests, stores the responses, parse it
        returns the scrapped vessels info"""

        # requests headers to avoid 403
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
        }

        # request
        total_url = len(self.urls)
        i = 0
        for url in self.urls:
            i += 1
            logging.info("Boat : " + str(i) + "/" + str(total_url))
            try:
                response = requests.get(url, headers=headers)
                #logging.debug(response.content)
            except Exception as e:
                logging.error("While requesting :" + url)
                logging.error(str(e))

            if response.status_code != 200:
                logging.warning(
                    "Response not 200 : " + str(response.status_code)
                )
                logging.warning(str(response.content))

            self.responses.append(response)
            self.parse(response)
            logging.info("Spider sleeping : " + str(self.sleep_delay))
            time.sleep(self.sleep_delay)

        # if export, try export
        if self.export:
            try:
                with open(self.export, "w") as f:
                    f.write(json.dumps(
                        self.vessels,
                        sort_keys=False,
                        indent=4,
                        separators=(",", ": ")
                    ))
            except Exception as e:
                logging.error("While exporting : " + str(e))

        return self.vessels

    def parse(self, response):
        """Parsing func"""

        vessel_info = dict()
        tree = html.fromstring(response.content)

        for key, value in X_PATHS.iteritems():
            try:
                # if successful parsing, add to the info dict
                vessel_info.update({
                    key: self.treat(key, tree.xpath(value)[0])
                })
            except Exception as e:
                # else log which attribute has been missed
                logging.warning(
                    "\nWhile trying to extract :" + str(key) + "\n" + str(e)
                )
                logging.warning(tree.xpath(value))
                logging.debug(response.content)
                logging.info(str(response.url))

        # append to list
        self.vessels.append(vessel_info)

    def treat(self, key, string):
        """Post treatment for specific keys"""

        # clean ATD ETA ATA
        if key in ["ATD", "ETA_ATA_check", "ETA_ATA"]:
            string = string.replace('\n', '')
            string = string.replace('\t', '')

        return string


# Parsing clues, using Xpath :
# response.xpath('//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/div[1]').extract_first()
# IMO : response.xpath('//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/div[1]/div[1]/b/text()').extract_first()
# MMSI : 2
# Call Sign : 3
# Flag : 4
# AIS Vessel Type : 5

# response.xpath('//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/div[2]').extract_first()
# Gross tonage : response.xpath('//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/div[2]/div[1]/b/text()').extract_first()
# Deadweight : 2
# Length Overall x Breadth Extreme: 3
# Year built : 4
# Status : 5

# Departure and Arrival
# response.xpath('//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]').extract_first()
# DEPARTURE :
# response.xpath('//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/@title').extract_first()

# ARRIVAL :
# response.xpath('//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/@title').extract_first()

# ATD / ATA / ETA : response.xpath('//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]').extract_first()

# ATD info response.xpath('//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/text()[2]').extract_first()

# ATA / ETA info :
# response.xpath('//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[2]/div[1]/span/text()').extract_first()

# choose whether ATA / ETA :
# response.xpath('//main/div[1]/div[1]/div[1]/div[5]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[2]/div[1]/b/span/text()').extract_first()




