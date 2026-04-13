from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class DateFunctions:
    def __init__(self):
        self.first_of_month = self.now(format="%Y-%m") + '-01'
        self.today_isoformat = self.now(format="%Y-%m-%d")
        self.first_of_prev_month = self.now_relative(format="%Y-%m-%d", months=1, day=1)
        self.prev_month_year = self.now_relative(format="%b%Y", months=1)
        pass

    @staticmethod
    def now(format:str = "%b%Y", **delta:timedelta) -> str:
        """
        Helper function to return the current time (or timedelta from now) in the specified format.
        Positive values return a time in the past.
        
        Params
        ------
        format: str (default = "%b%Y")
            Any suitable stftime format string, see: https://strftime.org/

        delta: datetime.timedelta 
            days, seconds, microseconds, milliseconds, hours, minutes, weeks

        Returns
        -------
        The current datetime object in the specified format as a string
        """
        td = timedelta(**delta) if delta else timedelta(days=0)
        return (datetime.now() - td).strftime(format)
    
    @staticmethod
    def now_relative(format:str = "%b%Y", **delta:relativedelta) -> str:
        """
        Return the relativedelta from now, in the specified format.
        Positive values return a time in the past.
        Plural deltas (e.g. months=1) calculates the datetime 1 month ago.
        Singular deltas (e.g month=1) will set the month to January.
        
        Params
        ------
        format: str (default = "%b%Y")
            Any suitable stftime format string, see: https://strftime.org/

        delta: dateutil.relativedelta

        Returns
        -------
        The current datetime object in the specified format as a string
        """
        td = relativedelta(**delta) if delta else relativedelta(days=0)
        return (datetime.now() - td).strftime(format)
