from scrapers.demokracija_scraper import DemokracijaScraper
from scrapers.monitor_scraper import MonitorScraper
from scrapers.siol_scraper import SiolScraper
from scrapers.finance_parser import FinanceScraper
from scrapers.mladina_scraper import MladinaScraper
from scrapers.val202_scraper import VAL202Scraper
from scrapers.vecer_scraper import VecerScraper
from scrapers.tfhrs_scraper import TwentyFourHrsScraper
from scrapers.rtv_scraper import RTVScraper
from scrapers.delo_scraper import DeloScraper
from scrapers.dnevnik_scraper import DnevnikScraper
from scrapers.zurnal_scraper import ZurnalScraper

scrapers = [DeloScraper(), VAL202Scraper(), MonitorScraper(), DemokracijaScraper(), SiolScraper(), VecerScraper(), FinanceScraper(), MladinaScraper(), TwentyFourHrsScraper(), RTVScraper(), ZurnalScraper(), DeloScraper(), DnevnikScraper()]
