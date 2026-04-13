from datetime import datetime, timedelta

class DateHandler:
    def __init__(self):
        self.first_day_this_month = self.now(format="%Y-%m") + '-01'
        self.today_isoformat = self.now(format="%Y-%m-%d")
        self.first_of_prev_month = datetime.now().replace(day=1) - timedelta(days=1)
        self.prev_month_year = self.first_of_prev_month.strftime("%b%Y")
        pass
    
    def now(self, format:str = "%b%Y", **delta:timedelta) -> str:
        """
        Helper function to return the current time (or timedelta from now) in the specified format.
        
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