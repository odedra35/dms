
import threading
from typing import Optional, Union

from dateutil import parser
from datetime import datetime, timedelta

from dms.app.domains.domains import check_ssl_and_status_bulk, update_user_domains_db


SCHEDULERS: dict[str, "ScheduledURLCheck"] = {}


def clear_user_scheduler(user: str) -> str:
    """Removes a user scheduler."""

    print(f"Removing user ({user}) scheduler.")
    try:
        SCHEDULERS[user].stop()
    except KeyError:
        return f"User({user}) didn't have any scheduled urls check."
    finally:
        print(f"SCHEDULERS: {SCHEDULERS}")
    return f"Successfully removed user({user}) scheduled url check."


def add_user_scheduler(user: str, urls: Union[str, list], limit: int, hours: Optional[int], fixed: str) -> str:
    """Add new Scheduler for user.

    :return: string error message (if there is error)
    """
    clear_user_scheduler(user)
    # Remove duplicated urls
    if not isinstance(urls, list):
        urls = list(set(urls.splitlines()))

    print(f"Adding scheduler - \nUser: {user}\nUrls: {urls}\nLimit: {limit}\nRate: {hours}\nHour: {fixed}")
    if hours and fixed:
        return "Can't schedule both Hourly and in a Fixed time Url checks. Pick One option."
    urls = [urls] if not isinstance(urls, list) else urls

    SCHEDULERS[user] = ScheduledURLCheck(user, urls, limit, hours, fixed)
    SCHEDULERS[user].start()
    print(f"SCHEDULERS: {SCHEDULERS}")
    return f"Added new routine - Check {urls} every {hours if hours else fixed} {'hours' if hours else 'oclock'}"



class ScheduledURLCheck(threading.Thread):
    """Tool for performing domain scans periodically."""

    def __init__(self, user:str, urls:list[str], limit:int, hours: int = 0, fixed: str = ""):
        super().__init__()

        self.__user = user
        self.__urls = urls
        self.__urls_limit = limit

        self.__hours = ""
        if hours:
            self.__hours = hours  # static

        self.__fixed = fixed  # dynamic

        self.__next_scan_time: str = ""
        self.__request_and_ssl_result: list = []
        self.__err_msg: str = ""

        self.__exit_event = threading.Event()


    @property
    def results(self) -> list:
        return self.__request_and_ssl_result

    @property
    def err(self) -> str:
        return self.__err_msg

    @property
    def next_check_time(self) -> str:
        return self.__next_scan_time


    def run(self) -> None:
        """Performs monitoring functionality."""

        while not self.__exit_event.is_set():

            # Calc wait time till next scan event
            sleep_time_sec = self.__get_sleep_time()

            if self.__exit_event.is_set():
                print("Exiting!")
                break

            # Wait till next scan event
            print(f"Next scan in {sleep_time_sec=} seconds, Alive? {self.is_alive()}")
            self.__exit_event.wait(sleep_time_sec)

            # Perform scan event
            self.__request_and_ssl_result = check_ssl_and_status_bulk(self.__urls, self.__urls_limit)
            self.__err_msg = update_user_domains_db(self.__user, self.__request_and_ssl_result)


    def stop(self) -> None:
        """Stop monitoring."""
        print("Stopping Liveness Monitor.")
        while not self.__exit_event.is_set():
            self.__exit_event.set()
            self.join()


    def __get_sleep_time(self) -> float:
        """Calculates next interval sleep time according to option given."""

        # Default is fixed rate scan
        if self.__hours:
            return self.__calculate_diff_given_time_interval()

        # URL is once every named hour
        elif self.__fixed:
            return self.__calculate_diff_from_named_hour()

        # No option selected
        else :
            print("Scan time interval or fixed time was not set. stopping.")
            self.stop()
        return 0


    def __calculate_diff_from_named_hour(self) -> float:
        """Calculate time diff in seconds till next named hour like '19:00'"""

        diff = (parser.parse(self.__fixed) - datetime.now()).total_seconds()

        print(f"now: {datetime.now()}")
        print(f"diff: {diff}")

        seconds_till_scan = diff if diff > 0 else 86400 + diff

        self.__next_scan_time = datetime.now() + timedelta(seconds=seconds_till_scan)
        print(f"scheduled scan: {self.__next_scan_time}")
        print(f"seconds till scan: {seconds_till_scan}")
        return seconds_till_scan


    def __calculate_diff_given_time_interval(self) -> float:
        """Calculate time diff in seconds till next scan, given 1 hour(s) intervals."""

        seconds_till_scan = int(self.__hours) * 3600 #
        self.__next_scan_time = datetime.now() + timedelta(seconds=seconds_till_scan)
        print(f"scheduled scan: {self.__next_scan_time}")
        print(f"seconds till scan: {seconds_till_scan}")
        return seconds_till_scan

    def __repr__(self):
        return f"[{self.__user} | {self.__urls} | {self.__next_scan_time} | {self.__hours} | {self.__fixed} | {self.is_alive()}]"
