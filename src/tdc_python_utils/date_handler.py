from datetime import datetime

class DateHandler:
    def __init__(self):
        self.first_day_this_month = self.now(format="%Y-%m") + '-01'
        self.today_isoformat = self.now(format="%Y-%m-%d")
        pass
    
    def now(self, format:str = "%b%Y") -> str:
        """
        Helper function to return the current time in the specified format
        
        Params
        ------
        format: str (default = "%b%Y")
            Any suitable stftime format string, see: https://strftime.org/

        Returns
        -------
        The current datetime object in the specified format as a string
        """
        return (datetime.now()).strftime(format)