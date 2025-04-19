import requests
import json
import datetime
import logging
import os


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("weather_log.txt"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置信息
class Config:
    # OpenWeatherMap API配置
    WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "YOUR_OPENWEATHERMAP_API_KEY")  # 替换为你的OpenWeatherMap API密钥
    CITY_NAME = "Zhenjiang"  # 镇江的城市名称
    COUNTRY_CODE = "CN"  # 中国的国家代码
    LANG = "zh_cn"  # 返回数据的语言，中文
    SERVERCHAN_KEY = os.environ.get("SERVERCHAN_KEY", "YOUR_SERVERCHAN_KEY")  # Server酱的SendKey
    
    # Server酱配置

# 获取天气数据
def get_weather():
    try:
        # 获取当前天气
        current_url = f"https://api.openweathermap.org/data/2.5/weather?q={Config.CITY_NAME},{Config.COUNTRY_CODE}&appid={Config.WEATHER_API_KEY}&units=metric&lang={Config.LANG}"
        current_response = requests.get(current_url)
        current_data = current_response.json()
        
        # 获取5天预报（包含未来3天）
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={Config.CITY_NAME},{Config.COUNTRY_CODE}&appid={Config.WEATHER_API_KEY}&units=metric&lang={Config.LANG}"
        forecast_response = requests.get(forecast_url)
        forecast_data = forecast_response.json()
        
        if current_response.status_code == 200 and forecast_response.status_code == 200:
            # 处理当前天气数据
            weather_now = {
                "temp": str(round(current_data.get("main", {}).get("temp", 0))),
                "feelsLike": str(round(current_data.get("main", {}).get("feels_like", 0))),
                "text": current_data.get("weather", [{}])[0].get("description", "未知"),
                "windDir": get_wind_direction(current_data.get("wind", {}).get("deg", 0)),
                "windScale": get_wind_scale(current_data.get("wind", {}).get("speed", 0)),
                "humidity": str(current_data.get("main", {}).get("humidity", 0))
            }
            
            # 处理天气预报数据
            daily_forecasts = process_forecast_data(forecast_data)
            
            return {
                "now": weather_now,
                "daily": daily_forecasts
            }
        else:
            error_msg = f"获取天气数据失败: 当前天气状态码 {current_response.status_code}, 预报天气状态码 {forecast_response.status_code}"
            logger.error(error_msg)
            return None
    except Exception as e:
        logger.error(f"获取天气数据异常: {str(e)}")
        return None

# 处理风向数据
def get_wind_direction(degrees):
    directions = ["北风", "东北风", "东风", "东南风", "南风", "西南风", "西风", "西北风", "北风"]
    index = round(degrees / 45)
    return directions[index % 8]

# 处理风力等级
def get_wind_scale(speed):
    # 根据风速（米/秒）计算风力等级（简化版）
    if speed < 0.3:
        return "0"
    elif speed < 1.6:
        return "1"
    elif speed < 3.4:
        return "2"
    elif speed < 5.5:
        return "3"
    elif speed < 8.0:
        return "4"
    elif speed < 10.8:
        return "5"
    elif speed < 13.9:
        return "6"
    elif speed < 17.2:
        return "7"
    elif speed < 20.8:
        return "8"
    elif speed < 24.5:
        return "9"
    elif speed < 28.5:
        return "10"
    elif speed < 32.7:
        return "11"
    else:
        return "12+"

# 处理天气预报数据
def process_forecast_data(forecast_data):
    if not forecast_data or "list" not in forecast_data:
        return []
    
    # 获取预报列表
    forecast_list = forecast_data.get("list", [])
    
    # 按天分组预报数据
    daily_data = {}
    for item in forecast_list:
        # 获取日期（不含时间）
        # 转换UTC时间为北京时间（UTC+8）
        utc_time = datetime.datetime.strptime(item.get("dt_txt"), "%Y-%m-%d %H:%M:%S")
        beijing_time = utc_time + datetime.timedelta(hours=8)
        date = beijing_time.strftime("%Y-%m-%d")
        if not date:
            continue
            
        if date not in daily_data:
            daily_data[date] = {
                "temps": [],
                "weather": [],
                "wind_speed": [],
                "wind_deg": []
            }
        
        # 收集温度数据
        daily_data[date]["temps"].append(item.get("main", {}).get("temp", 0))
        
        # 收集天气描述
        if item.get("weather") and len(item.get("weather")) > 0:
            daily_data[date]["weather"].append(item.get("weather")[0].get("description", ""))
        
        # 收集风速和风向
        daily_data[date]["wind_speed"].append(item.get("wind", {}).get("speed", 0))
        daily_data[date]["wind_deg"].append(item.get("wind", {}).get("deg", 0))
    
    # 转换为和风天气格式的数据结构
    result = []
    for date, data in daily_data.items():
        if len(data["temps"]) == 0:
            continue
            
        # 计算最高和最低温度
        temp_max = str(round(max(data["temps"])))
        temp_min = str(round(min(data["temps"])))
        
        # 获取白天和夜间的天气描述（简化处理）
        text_day = data["weather"][0] if data["weather"] else "未知"
        text_night = data["weather"][-1] if data["weather"] else "未知"
        
        # 计算平均风向和风速
        avg_wind_deg = sum(data["wind_deg"]) / len(data["wind_deg"]) if data["wind_deg"] else 0
        avg_wind_speed = sum(data["wind_speed"]) / len(data["wind_speed"]) if data["wind_speed"] else 0
        
        result.append({
            "fxDate": date,
            "tempMax": temp_max,
            "tempMin": temp_min,
            "textDay": text_day,
            "textNight": text_night,
            "windDirDay": get_wind_direction(avg_wind_deg),
            "windScaleDay": get_wind_scale(avg_wind_speed)
        })
    
    # 只返回未来3天的数据
    return result[:3]

# 发送邮件通知
    # 发送Server酱通知

# 生成天气消息
def generate_weather_message(weather_data):
    if not weather_data:
        return "无法获取天气数据"
    
    now = weather_data.get("now", {})
    daily = weather_data.get("daily", [])
    
    # 获取北京时间（UTC+8）
    today = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime("%Y年%m月%d日")
    
    message = f"【镇江天气预报】{today}\n\n"
    
    # 当前天气
    if now:
        message += f"当前天气: {now.get('text', '未知')}\n"
        message += f"当前温度: {now.get('temp', '未知')}°C\n"
        message += f"体感温度: {now.get('feelsLike', '未知')}°C\n"
        message += f"风向: {now.get('windDir', '未知')}\n"
        message += f"风力: {now.get('windScale', '未知')}级\n"
        message += f"湿度: {now.get('humidity', '未知')}%\n\n"
    
    # 未来预报
    if daily:
        message += "未来天气预报:\n"
        for day in daily:
            date = day.get("fxDate", "")
            if date:
                date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
                date_str = date_obj.strftime("%m月%d日")
                day_of_week = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date_obj.weekday()]
                
                message += f"\n{date_str} {day_of_week}\n"
                message += f"天气: {day.get('textDay', '未知')}转{day.get('textNight', '未知')}\n"
                message += f"温度: {day.get('tempMin', '未知')}°C ~ {day.get('tempMax', '未知')}°C\n"
                message += f"风向: {day.get('windDirDay', '未知')}\n"
                message += f"风力: {day.get('windScaleDay', '未知')}级\n"
    
    return message

# 主函数
def main():
    logger.info("开始获取天气数据")
    weather_data = get_weather()
    
    if weather_data:
        message = generate_weather_message(weather_data)
        logger.info("生成天气消息成功")
        
        logger.info("开始发送Server酱通知")
        def send_serverchan_notification(message):
            try:
                url = f"https://sctapi.ftqq.com/{Config.SERVERCHAN_KEY}.send"
                data = {
                    "title": "镇江天气预报",
                    "desp": message
                }
                response = requests.post(url, data=data)
                if response.status_code == 200:
                    return True
                logger.error(f"Server酱通知失败: {response.text}")
                return False
            except Exception as e:
                logger.error(f"发送Server酱通知异常: {str(e)}")
                return False

        if send_serverchan_notification(message):
            logger.info("天气通知发送成功")
        else:
            logger.error("天气通知发送失败")
    else:
        logger.error("无法获取天气数据，取消发送通知")

if __name__ == "__main__":
    main()
