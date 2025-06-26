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

    # Handle holidays
    if (not is_leap_year(today.year) and day_of_year > 364):
        return ("Holiday Day", None, None, None, day_of_year)

    if is_leap_year(today.year) and day_of_year == 366:
        return ("Leap Holiday", None, None, None, day_of_year)

    # Custom calendar within 364 days
    custom_day_index = day_of_year - 1  # 0-based
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
        for week in range(4):
            for day in WEEKDAYS:
                day_text = f"Day {day_counter:03d}: {day}, Week {week+1}"
                if today_info and ordinal(month) == today_info[0] and day == today_info[2] and (week+1) == today_info[3]:
                    day_text = f"⬅️ **{day_text} ← Today**"
                month_days.append(day_text)
                day_counter += 1
        calendar_data.append((month_label, month_days))

    holidays = [f"Day {day_counter:03d}: Holiday Day"]
    if today_info and today_info[0] == "Holiday Day":
        holidays[0] = f"⬅️ **{holidays[0]} ← Today**"
    day_counter += 1

    if is_leap_year(year):
        holidays.append(f"Day {day_counter:03d}: Leap Holiday")

    return calendar_data, holidays

# Streamlit App
st.set_page_config(page_title="13-Month Calendar", layout="wide")

# Get accurate now time
now = datetime.now(tz)
custom_today = get_custom_date(now)

# Top Section: Big Time and % of day
col1, col2 = st.columns([2, 2])
with col1:
    current_time = now.strftime('%I:%M:%S %p')
    current_day = f"Day {custom_today[1]}" if custom_today[1] else ""
    st.markdown(f"<h1 style='text-align: center;'>🕒 {current_time} | {current_day}</h1>", unsafe_allow_html=True)

    seconds_today = now.hour * 3600 + now.minute * 60 + now.second
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
year = st.number_input("Select Year", value=now.year, step=1)
calendar, holidays = generate_calendar(year, custom_today if year == now.year else None)

for month_label, days in calendar:
    with st.expander(month_label):
        for d in days:
            st.markdown(d)

st.subheader("🎉 Holidays")
for h in holidays:
    st.markdown(h)
