from datetime import datetime, timedelta, timezone
import re
from models.database import collection as Telemetry
#Extracts single date
def extract_date(query):
    date_patterns = [
        (r"\b\d{4}-\d{2}-\d{2}\b", "%Y-%m-%d"),  
        (r"\b\d{2}/\d{2}/\d{4}\b", "%d/%m/%Y"),  
        (r"\b(\d{1,2})\s([A-Za-z]{3,9})\s(\d{4})\b", None) 
    ]

    for pattern, date_format in date_patterns:
        match = re.search(pattern, query)
        if match:
            if date_format:
                return datetime.strptime(match.group(0), date_format).strftime("%Y-%m-%d")
            else:
                day, month_name, year = match.groups()
                try:
                    month_number = datetime.strptime(month_name.capitalize(), "%b").month
                except ValueError:
                    month_number = datetime.strptime(month_name.capitalize(), "%B").month
                return f"{year}-{month_number:02d}-{int(day):02d}"

#Extracts date range
def extract_date_range(query):
    date_matches = re.findall(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b|\b\d{1,2} [A-Za-z]+ \d{4}\b", query)
    extracted_dates = [extract_date(date) for date in date_matches if extract_date(date)]

    if not extracted_dates:
        return None, None, "No valid date."

    start_date = extracted_dates[0]
    end_date = extracted_dates[1] if len(extracted_dates) > 1 else start_date

    today = datetime.today().strftime("%Y-%m-%d")
    five_years_ago = (datetime.today() - timedelta(days=5 * 365)).strftime("%Y-%m-%d")

    if start_date > today or end_date > today:
        return None, None, "Cannot hanlde for future dates."

    if start_date < five_years_ago:
        return None, None, "Date is too old"

    if start_date > end_date:
        return None, None, "Start date cannot be after the end date."

    return start_date, end_date, None  

# Extracts valid dates along with hour start and hour end

def extract_all_dates(query):
    date_matches = re.findall(r"\b\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2})?\b|\b\d{2}/\d{2}/\d{4}\b|\b\d{1,2} [A-Za-z]+ \d{4}\b", query)
    
    extracted_dates = [extract_date(date) for date in date_matches if extract_date(date)]

    if not extracted_dates:
        return None, None, None, None, "Could not extract valid dates."

    today = datetime.today().strftime("%Y-%m-%d")
    five_years_ago = (datetime.today() - timedelta(days=5 * 365)).strftime("%Y-%m-%d")

    valid_dates = []
    hour_start = None
    hour_end = None

    for date in extracted_dates:
        if date > today:
            return None, None, None, None, "Cannot query for future dates."
        if date < five_years_ago:
            return None, None, None, None, "Date is too old"
        valid_dates.append(date)

    time_range_match = re.search(r"(\d{1,2}):(\d{2})\s*(?:to|-|–|until)\s*(\d{1,2}):(\d{2})", query)
    if time_range_match:
        start_hour = int(time_range_match.group(1))
        end_hour = int(time_range_match.group(3))
        hour_start = start_hour
        hour_end = end_hour
    else:
        # Look for a single time in the format HH:MM (i.e 5:00)
        time_match = re.search(r"(\d{1,2}):(\d{2})", query)
        if time_match:
            start_hour = int(time_match.group(1))
            hour_start = start_hour
            hour_end = (start_hour + 1) % 24  # Default the end hour to 1 hour after the start
        elif re.search(r"at\s+\d{1,2}\s*(?:am|pm)", query, re.IGNORECASE):
            # Look for times in "at 5pm" format
            am_pm_match = re.search(r"at\s+(\d{1,2})\s*(am|pm)", query, re.IGNORECASE)
            if am_pm_match:
                hour = int(am_pm_match.group(1))
                am_pm = am_pm_match.group(2).lower()
                if am_pm == "pm" and hour < 12:
                    hour += 12  # Convert PM hour to 24-hour format
                if am_pm == "am" and hour == 12:
                    hour = 0  # Convert 12 AM to 0
                hour_start = hour
                hour_end = (hour + 1) % 24  # Default the end hour to 1 hour after the start

        else:
            time_until_match = re.search(r"(\d{1,2})\s*(am|pm)?\s*(?:until)\s*(\d{1,2})\s*(am|pm)?", query, re.IGNORECASE)
            if time_until_match:
                start_hour = int(time_until_match.group(1))
                end_hour = int(time_until_match.group(3))
                start_am_pm = time_until_match.group(2)
                end_am_pm = time_until_match.group(4)

                if start_am_pm:
                    if start_am_pm.lower() == "pm" and start_hour < 12:
                        start_hour += 12
                    if start_am_pm.lower() == "am" and start_hour == 12:
                        start_hour = 0

                if end_am_pm:
                    if end_am_pm.lower() == "pm" and end_hour < 12:
                        end_hour += 12
                    if end_am_pm.lower() == "am" and end_hour == 12:
                        end_hour = 0
                else:
                    if start_am_pm and start_hour < 12 and end_hour < 12:
                        end_hour += 12

                hour_start = start_hour
                hour_end = end_hour

    mongo_dates = [
        datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        for date in valid_dates
    ]

    return valid_dates, mongo_dates, hour_start, hour_end, None

#Generates a Mongo date filter query.
def get_date_range(start_date, end_date=None):
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)
        else:
            end_dt = start_dt.replace(hour=23, minute=59, second=59, microsecond=999999)

        return {"$gte": start_dt, "$lte": end_dt}

    except ValueError:
        return None

#Converts date format to correct if needed
def convert_date_format(date_string, input_format, output_format="%Y-%m-%d"):

    try:
        return datetime.strptime(date_string, input_format).strftime(output_format)
    except ValueError:
        return None
    
def get_date_range(asset_id: str = None):
    query = {}
    if asset_id:
        query["metadata.asset_id"] = asset_id

    oldest_doc = Telemetry.find(query).sort("timestamp", 1).limit(1)
    newest_doc = Telemetry.find(query).sort("timestamp", -1).limit(1)

    oldest = list(oldest_doc)
    newest = list(newest_doc)

    if not oldest or not newest:
        return None, None

    return oldest[0]["timestamp"].date(), newest[0]["timestamp"].date()

today_str = datetime.utcnow().strftime("%d %B %Y")


