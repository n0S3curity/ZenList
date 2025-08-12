from il_supermarket_scarper.scrapper_runner import MainScrapperRunner


def run_scraper_for_osher_ad():
    scraper = MainScrapperRunner(enabled_scrapers=["OSHER_AD"], dump_folder_name='../databases/osherad_data',
                                 lookup_in_db=True)
    scraper.run(limit=None, files_types=None, when_date="latest", suppress_exception=False)


def run_scraper_for_yohananof():
    scraper = MainScrapperRunner(enabled_scrapers=["YOHANANOF"], dump_folder_name='../databases/yohananof_data',
                                 lookup_in_db=True)
    scraper.run(limit=None, files_types=None, when_date="latest", suppress_exception=False)


if __name__ == '__main__':
    try:

        run_scraper_for_osher_ad()
        run_scraper_for_yohananof()
    except Exception as e:
        print(f"scraper failed: {e}")
