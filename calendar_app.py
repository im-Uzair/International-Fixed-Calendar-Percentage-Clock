import streamlit as st
from datetime import datetime, timedelta
from math import floor
from streamlit_autorefresh import st_autorefresh
import pytz

# Auto-refresh every second
st_autorefresh(interval=1000, limit=None, key="refresh")

# Set timezone
tz = pytz.timezone("Asia/Kolkata")
now = datetime.now(tz)

# Constants
WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
SECONDS_IN_DAY = 86400

# Helpers
def is_leap_year(year):
    return (year % 4 == 0 and (year % 100 != 0)) or (year % 400 == 0)

def ordinal(n):
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}{['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]}"

def get_custom_date(today):
    day_of_year = today.timetuple().tm_yday  # 1–366
    year = today.year # Added for clarity in the new logic

    # Corrected holiday logic:
    if is_leap_year(year):
        if day_of_year == 366:
            return ("Leap Holiday", None, None, None, day_of_year)
        if day_of_year == 365:  # Day 365 of a leap year is "Holiday Day"
            return ("Holiday Day", None, None, None, day_of_year)
        # Otherwise (day_of_year <= 364), it's a custom calendar day
    else:  # Non-leap year
        if day_of_year == 365:  # Day 365 of a non-leap year is "Holiday Day"
            return ("Holiday Day", None, None, None, day_of_year)
        # Otherwise (day_of_year <= 364), it's a custom calendar day

    # If we reach here, day_of_year is within 1-364 range for both leap/non-leap
    custom_day_index = day_of_year - 1  # 0-based for 0-363 range
    month = (custom_day_index // 28) + 1
    day_in_month = (custom_day_index % 28) + 1
    weekday = WEEKDAYS[custom_day_index % 7]
    week = ((day_in_month - 1) // 7) + 1

    return (ordinal(month), day_in_month, weekday, week, day_of_year)

def generate_calendar(year, today_info=None):
    calendar_data = []
    day_counter = 1

    for month in range(1, 14):
        month_label = f"{ordinal(month)} Month"
        month_days = []
        for week_idx in range(4): # Renamed week to week_idx to avoid conflict if needed
            for day_name in WEEKDAYS: # Renamed day to day_name
                day_text = f"Day {day_counter:03d}: {day_name}, Week {week_idx+1}"
                # Check against today_info which has (ordinal_month, day_in_month, weekday_name, week_num, day_of_year_std)
                if today_info and \
                   today_info[0] == ordinal(month) and \
                   today_info[2] == day_name and \
                   today_info[3] == (week_idx+1):
                    day_text = f"⬅️ **{day_text} ← Today**"
                month_days.append(day_text)
                day_counter += 1
        calendar_data.append((month_label, month_days))

    holidays = [f"Day {day_counter:03d}: Holiday Day"] # day_counter is 365 here
    if today_info and today_info[0] == "Holiday Day":
        holidays[0] = f"⬅️ **{holidays[0]} ← Today**"
    day_counter += 1 # day_counter is 366 here

    if is_leap_year(year):
        leap_holiday_text = f"Day {day_counter:03d}: Leap Holiday"
        if today_info and today_info[0] == "Leap Holiday":
            leap_holiday_text = f"⬅️ **{leap_holiday_text} ← Today**"
        holidays.append(leap_holiday_text)

    return calendar_data, holidays

# Streamlit App
st.set_page_config(page_title="13-Month Calendar", layout="wide")

# Get accurate now time
# Note: now is defined globally at the top, but if the app runs for a long time,
# this 'now' for custom_today might become stale if not re-evaluated within refresh cycle.
# However, st_autorefresh causes rerun from top, so 'now' is recalculated.
# The 'now' inside generate_calendar (for year == now.year check) also uses the global 'now'.
# This should be fine due to autorefresh.
_now = datetime.now(tz) # Use a temporary _now for this specific call
custom_today = get_custom_date(_now)


# Top Section: Big Time and % of day
col1, col2 = st.columns([2, 2])
with col1:
    # Use _now for consistency in this rendering pass
    current_time = _now.strftime('%I:%M:%S %p')
    current_day = f"Day {custom_today[1]}" if custom_today[1] else "" # custom_today[1] is day_in_month
    st.markdown(f"<h1 style='text-align: center;'>🕒 {current_time} | {current_day}</h1>", unsafe_allow_html=True)

    seconds_today = _now.hour * 3600 + _now.minute * 60 + _now.second
    percent_day = (seconds_today / SECONDS_IN_DAY) * 100
    st.markdown(f"<h2 style='text-align: center;'>📊 {percent_day:.2f}% of the day passed</h2>", unsafe_allow_html=True)

with col2:
    st.markdown("<h1 style='text-align: center;'>📅 Today's Date</h1>", unsafe_allow_html=True)

    if custom_today[0] == "Holiday Day":
        st.markdown(f"<h3 style='text-align: center;'>🎉 Holiday Day (Day {custom_today[4]})</h3>", unsafe_allow_html=True)
    elif custom_today[0] == "Leap Holiday":
        st.markdown(f"<h3 style='text-align: center;'>🎉 Leap Holiday (Day {custom_today[4]})</h3>", unsafe_allow_html=True)
    else:
        st.markdown(
            f"<h4 style='text-align: center;'>📌 {custom_today[2]}, {custom_today[0]} Month, Day {custom_today[1]}, Week {custom_today[3]}</h4>",
            unsafe_allow_html=True
        )

# Calendar Section
st.subheader("📘 Full Calendar")
# Use _now.year for default year to match custom_today's context
year_input_default = _now.year
year = st.number_input("Select Year", value=year_input_default, step=1)

# Pass custom_today if selected year is the year of _now
# The global 'now' is used in generate_calendar for the check 'year == now.year'.
# This could be inconsistent if _now is very different from global now (e.g.跨日)
# For consistency, it's better if generate_calendar also knows about the 'current reference now'
# Or, more simply, ensure custom_today_for_calendar is derived from the same 'now' as the default year.
# The current logic: generate_calendar(year, custom_today if year == _now.year else None)
# And custom_today is from _now. This is consistent.
# The global `now` variable at the top is also updated on each refresh.
# The only potential confusion is `now` vs `_now`.
# Let's ensure `generate_calendar` uses `_now` for its `now.year` comparison too, or pass it.
# For simplicity, the existing `custom_today if year == _now.year else None` is fine.
# The `generate_calendar` function itself doesn't use `now.year` directly, it only uses `today_info` which is already conditioned.

calendar, holidays_list = generate_calendar(year, custom_today if year == _now.year else None)


for month_label, days_in_month in calendar: # Renamed for clarity
    with st.expander(month_label):
        for d_text in days_in_month: # Renamed for clarity
            st.markdown(d_text)

st.subheader("🎉 Holidays")
for h_text in holidays_list: # Renamed for clarity
    st.markdown(h_text)
