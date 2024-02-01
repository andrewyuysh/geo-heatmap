"""
Fingerprint: a set of criteria to narrow down coordinate records
includes proximity (to target location), time-of-day, time duration, itinerary (location1 -> location2, travel method)

e.g.: within 50m of gym for at least 45 minutes, occurring between 5am-12pm, from within 50m of home, traveling by car
"""
import datetime
import pandas as pd
import myutils

def get_sessions(
        df: pd.DataFrame,
        target_loc,
        target_radius,
        time_start=None,
        time_end=None,
        time_min_duration_minutes=0
    ):
    df['dist_target'] = myutils.distance(df['lat'], df['long'], target_loc[0], target_loc[1])
    df['near_target'] = df['dist_target'] <= target_radius
    df['session'] = df['near_target'].ne(df['near_target'].shift()).cumsum().where(df['near_target'])
    # TODO: loc + timestamps -> unknown location between the timestamps
    # assuming at least part of the unknown belongs to the session,
    # could include one extra row before and after each session
    # but hard to implement
    df['time_et'] = df['time'].dt.tz_localize('UTC').dt.tz_convert('America/New_York')
    session_times = df.groupby('session')['time_et'].agg(['count', 'first', 'last'])
    
    if time_start and time_end:
        time_start = pd.Timestamp(time_start).time()
        time_end = pd.Timestamp(time_end).time()
        # filter for start and end time
        session_times['start_time_et'] = session_times['first'].dt.time
        session_times['end_time_et'] = session_times['last'].dt.time
        session_times = session_times[(session_times['start_time_et'] >= time_start) & (session_times['end_time_et'] < time_end)]

    session_times['time_at_target'] = session_times['last'] - session_times['first']
    result_df = session_times[['first', 'last', 'time_at_target']].reset_index(drop=True)
    result_df = result_df.rename(columns={'first': 'start_time', 'last': 'end_time'})
    # filter for duration
    result_df = result_df[result_df['time_at_target'] > datetime.timedelta(minutes=time_min_duration_minutes)]
    return result_df