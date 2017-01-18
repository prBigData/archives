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

logging.basicConfig(filename="spider2.log", level=logging.DEBUG)


class Spider(object):
    """Our spider class

    Used to scrap info on vessels according to MMSI
    """

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

        # counter
        total_url = len(self.urls)
        i = 0

        # for url in url list
        for url in self.urls:
            i += 1
            logging.info("Boat : " + str(i) + "/" + str(total_url))

            # request it
            try:
                response = requests.get(url, headers=headers)
                # logging.debug(response.content)
            except Exception as e:
                logging.error("While requesting :" + url)
                logging.error(str(e))

            # if status code isn't 200, log it
            if response.status_code != 200:
                logging.warning(
                    "Response not 200 : " + str(response.status_code)
                )
                logging.info(str(response.content))

            # keep track of the response (we never know)
            self.responses.append(response)

            # parse vessel
            vessel = self.parse(response)
            logging.debug(str(vessel))

            # if export defined, export in real time vessel parsing
            if self.export and (len(vessel) > 0):

                vessels_list = list()
                # try to load previous vessel infos
                try:
                    with open(self.export, "r") as f:
                        vessels_list = json.loads(f.read())
                except Exception as e:
                    em = "While trying to read: " + self.export + "\n" + str(e)
                    logging.info(em)

                # append new vessel to list
                vessels_list.append(vessel)

                # then try to write the export file
                try:
                    with open(self.export, "w") as f:
                        f.write(json.dumps(
                            vessels_list,
                            sort_keys=False,
                            indent=4,
                            separators=(",", ": ")
                        ))
                except Exception as e:
                    em = "While exporting : " + self.export + "\n" + str(vessel)
                    em += "\n" + str(e)
                    logging.error(em)

            # then sleep until next vessel
            logging.info("Spider sleeping : " + str(self.sleep_delay))
            if self.sleep_delay:
                time.sleep(self.sleep_delay)

        return self.vessels

    def parse(self, response):
        """Parsing func"""

        vessel_info = dict()

        # html as a xpath tree
        tree = html.fromstring(response.content)

        prob = False
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
                prob = True

        if prob:
            with open("./problematic_urls.txt", "a") as f:
                logging.debug(response.content)
                f.write(str(response.url))
                f.write("\n")

        # append to list
        self.vessels.append(vessel_info)
        return vessel_info

    def treat(self, key, string):
        """Post treatment for specific keys"""

        # clean ATD ETA ATA
        if key in ["ATD", "ETA_ATA_check", "ETA_ATA"]:
            string = string.replace('\n', '')
            string = string.replace('\t', '')

        return string

    def get_responses(self):
        return self.responses

    def get_vessels(self):
        return self.vessels
