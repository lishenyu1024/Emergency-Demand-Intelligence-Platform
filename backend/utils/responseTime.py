import pandas as pd
import os
# 可选参数month和year，如果为空，则计算全年平均响应时间
def calculate_response_time(df: pd.DataFrame, year: int, month: int=None) -> str:
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    df['Year'] = df['tdate'].dt.year
    df['Month'] = df['tdate'].dt.month
    df = df[df['Year'] == year]
    if month is not None:
        df = df[df['Month'] == month]
    # 统一去掉时间中的秒数部分（如果有的话）
    df['disptime'] = df['disptime'].astype(str).str[:5]  # 只保留前5个字符 HH:MM
    df['enrtime'] = df['enrtime'].astype(str).str[:5]    # 只保留前5个字符 HH:MM
    
    # 统一使用不带秒数的格式解析
    df['disptime_dt'] = pd.to_datetime(df['tdate'].astype(str) + ' ' + df['disptime'], format='%Y-%m-%d %H:%M', errors='coerce')
    df['enrtime_dt'] = pd.to_datetime(df['tdate'].astype(str) + ' ' + df['enrtime'], format='%Y-%m-%d %H:%M', errors='coerce')

    response_time = []
    for index, row in df.iterrows():
        if pd.notna(row['disptime_dt']) and pd.notna(row['enrtime_dt']):
            if row['enrtime_dt'] < row['disptime_dt']:
                # Assuming enrtime is on the next day if it's earlier than disptime on the same date
                response_time.append(row['enrtime_dt'] + pd.Timedelta(days=1) - row['disptime_dt'])
            else:
                response_time.append(row['enrtime_dt'] - row['disptime_dt'])
        else:
            response_time.append(pd.NaT)

    df['response_time'] = response_time
    mean_response_time = df['response_time'].mean()
    if pd.isna(mean_response_time):
        return "N/A"
    print('mean_response_time',mean_response_time)
    return str(mean_response_time)