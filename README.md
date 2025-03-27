# 每日天气通知系统

这是一个基于GitHub Actions的自动化天气通知系统，可以定时获取指定城市的天气信息，并通过多种方式（如邮件、Server酱、Telegram机器人等）发送通知。

## 功能特点

- 自动获取当前天气和未来3天的天气预报
- 支持多种通知方式（邮件、Server酱、Telegram机器人等）
- 使用GitHub Actions实现定时自动运行
- 支持手动触发运行
- 详细的日志记录

## 安装步骤

1. 克隆或下载本仓库到本地
   ```
   git clone https://github.com/yourusername/weather-notification.git
   cd weather-notification
   ```

2. 安装依赖
   ```
   pip install requests
   ```

## 配置说明

### 1. OpenWeatherMap API配置

1. 注册[OpenWeatherMap开发者账号](https://openweathermap.org/)
2. 创建应用并获取API Key
3. 在GitHub仓库设置中添加Secret：`WEATHER_API_KEY`

### 2. 通知方式配置

可以选择以下任一通知方式：

#### 2.1 邮件通知

1. 在GitHub仓库设置中添加以下Secrets：
   - `EMAIL_HOST`：SMTP服务器地址
   - `EMAIL_PORT`：SMTP服务器端口
   - `EMAIL_USER`：发件人邮箱地址
   - `EMAIL_PASSWORD`：发件人邮箱密码或授权码
   - `EMAIL_RECEIVER`：收件人邮箱地址

#### 2.2 Server酱通知

1. 注册[Server酱](https://sct.ftqq.com/)账号
2. 获取SendKey
3. 在GitHub仓库设置中添加Secret：`SERVERCHAN_KEY`

#### 2.3 Telegram机器人通知

1. 创建Telegram机器人，获取Bot Token
2. 获取Chat ID
3. 在GitHub仓库设置中添加Secrets：
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

### 3. 修改城市配置

在`weather_notification.py`文件中修改`CITY_NAME`和`COUNTRY_CODE`为你所在城市的名称和国家代码：

```python
CITY_NAME = "Zhenjiang"  # 默认为镇江，修改为你所在城市的名称（英文）
COUNTRY_CODE = "CN"  # 中国的国家代码
```

城市名称需要使用英文，国家代码使用两位字母代码（如中国为CN）。

## 使用方法

### 本地运行

1. 在`weather_notification.py`中填入你的API密钥和选择的通知方式配置
2. 运行脚本
   ```
   python weather_notification.py
   ```

### GitHub Actions自动运行

1. Fork本仓库
2. 在仓库的Settings -> Secrets and variables -> Actions中添加以下Secrets：
   - `WEATHER_API_KEY`：OpenWeatherMap API密钥
   - 根据你选择的通知方式，添加相应的Secrets（参见上方通知方式配置）
3. GitHub Actions将按照配置的时间（默认每天早上7点）自动运行

### 手动触发运行

1. 在GitHub仓库页面，点击Actions标签
2. 选择"Daily Weather Notification"工作流
3. 点击"Run workflow"按钮

## 日志

脚本运行时会生成`weather_log.txt`日志文件，记录运行情况和错误信息。

## 自定义

- 修改通知时间：编辑`.github/workflows/weather_notification.yml`文件中的cron表达式
- 修改通知内容格式：编辑`generate_weather_message`函数
- 修改通知接收人：根据选择的通知方式，编辑相应的接收人配置

## 许可证

MIT
