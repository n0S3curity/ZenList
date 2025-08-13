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
                time.sleep(7200)  # Sleep for 2 hours before the next run
            except Exception as e:
                print(f"Error in yohananof scraper: {e}")
            break


if __name__ == '__main__':
    try:
        scrap = Scrapper()
        scrap.run_scraper_for_osher_ad()
        scrap.run_scraper_for_yohananof()
    except Exception as e:
        print(f"scraper failed: {e}")
