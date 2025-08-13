import json
import os
import time

from il_supermarket_scarper.scrapper_runner import MainScrapperRunner


class Scrapper:
    def __init__(self):
        self.osherad_folder = '../databases/osherad_data'
        self.yohananof_folder = '../databases/yohananof_data'
        self.osherad_scan_count = 0
        self.yohananof_scan_count = 0

    def run_scraper_for_osher_ad(self):
        while True:
            try:
                print("Starting Osher Ad scraper...")
                scraper = MainScrapperRunner(enabled_scrapers=["OSHER_AD"], dump_folder_name=self.osherad_folder,
                                             lookup_in_db=True)
                scraper.run(limit=None, files_types=None, when_date="latest", suppress_exception=False)
                self.osherad_scan_count += 1
                print(f"Osher Ad scraper scan {self.osherad_scan_count} completed successfully. sleeping for 2 hours.")
                time.sleep(7200)  # Sleep for 2 hours before the next run
            except Exception as e:
                print(f"Error in Osher Ad scraper: {e}")
                break

    def run_scraper_for_yohananof(self):
        while True:
            try:
                print("Starting yohananof scraper...")
                scraper = MainScrapperRunner(enabled_scrapers=["YOHANANOF"], dump_folder_name=self.yohananof_folder,
                                             lookup_in_db=True)
                scraper.run(limit=None, files_types=None, when_date="latest", suppress_exception=False)
                self.yohananof_scan_count += 1
                print(
                    f"yohananof scraper scan {self.yohananof_scan_count} completed successfully. sleeping for 2 hours.")
                # Extract liked supermarkets from general_settings.json
                liked_supermarkets = self.extract_liked_supermarkets("yohananof")
                if liked_supermarkets != "failed":
                    for supermarket in liked_supermarkets:
                        print(f"extracting data for Liked supermarket: {supermarket}")
                        full_prices_path = self.extract_full_prices(supermarket, self.yohananof_folder,
                                                                    supermarket_name="yohananof")
                        if full_prices_path != "failed":
                            print(f"Full prices extracted for {supermarket}: {full_prices_path}")

                            # -----------------------continue from here-----------------------
                        else:
                            print(f"Failed to extract full prices for {supermarket}, skipping.")
                            pass

                time.sleep(7200)  # Sleep for 2 hours before the next run
            except Exception as e:
                print(f"Error in yohananof scraper: {e}")
            break

    def extract_liked_supermarkets(self, supermarket_name_in_liked):
        """ extracts liked supermarkets from the ../databases/general_settingsjson database """
        try:
            with open('../databases/general_settings.json', 'r') as file:
                general_settings = json.load(file)
            liked_supermarkets = general_settings.get("liked", [])
            if not liked_supermarkets:
                print("No liked supermarkets found in general_settings.json")
                return "failed"
            # Filter liked supermarkets based on the provided name
            if supermarket_name_in_liked in liked_supermarkets.keys():
                liked_supermarkets = liked_supermarkets[supermarket_name_in_liked]
                return liked_supermarkets
            else:
                print(f"No liked supermarkets found for {supermarket_name_in_liked} in general_settings.json")
                return "failed"
        except Exception as e:
            print(f"Error reading general_settings.json: {e}")
            return "failed"

    def extract_full_prices(self, supermarket, data_folder, supermarket_name):
        print(f"Extracting prices and promotions for supermarket:{supermarket_name}, StoreId: {supermarket['StoreId']}")
        try:
            folder_name = f"{data_folder}/{supermarket_name.capitalize()}"
            # check if the folder exists, if not stop and fail
            if not os.path.exists(folder_name):
                print(f"Folder {folder_name} does not exist. Skipping extraction for {supermarket_name}.")
                return "failed"
            # find the file that has the following rules in its name:
            # file pattern is like "pricefull123421342134-{supermarket['StoreId']}-timestamp.xml" example: PriceFull7290803800003-052-202508130010.xml
            # contains "pricefull"
            # the StoreId of the supermarket
            # most updated timestamp.
            files = [f.lower() for f in os.listdir(folder_name) if
                     f.startswith("pricefull") and str(supermarket['StoreId']) in f and f.endswith(".xml")]
            # now choose the most updated file by his timestamp
            if not files:
                print(f"No pricefull files found for StoreId {supermarket['StoreId']} in {folder_name}.")
                return "failed"
            # Extract the timestamp from the file name and find the most recent one
            most_updated_file = max(files, key=lambda f: int(f.split('-')[-1].split('.')[0]))
            print(f"Most updated file found: {most_updated_file}")
            # return the most updated file path
            most_updated_file_path = os.path.join(folder_name, most_updated_file)
            return most_updated_file_path

        except Exception as e:
            print(f"Error extracting prices and promos: {e}")
            return "failed"



if __name__ == '__main__':
    try:
        scrap = Scrapper()
        scrap.run_scraper_for_osher_ad()
        scrap.run_scraper_for_yohananof()
    except Exception as e:
        print(f"scraper failed: {e}")
