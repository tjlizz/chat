from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os
import json
import datetime
import random

# 初始化Flask应用
app = Flask(__name__, static_folder='static')

# 数据库设置
DATABASE = "chat_messages.db"

def get_db_connection():
    """创建数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库表结构"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# 确保应用启动时初始化数据库
init_db()

# 提供前端静态文件
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    """接收用户消息并返回回复"""
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': 'Invalid request'}), 400
    
    user_message = data['message']
    
    # 将用户消息保存到数据库
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        'INSERT INTO messages (sender, content, timestamp) VALUES (?, ?, ?)',
        ('user', user_message, now)
    )
    conn.commit()
    
    # 获取应答消息
    reply = get_reply(user_message)
    
    # 将系统回复保存到数据库
    cursor.execute(
        'INSERT INTO messages (sender, content, timestamp) VALUES (?, ?, ?)',
        ('system', reply, now)
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'reply': reply
    })

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """获取消息历史"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM messages ORDER BY timestamp')
    messages = cursor.fetchall()
    
    message_list = []
    for message in messages:
        message_list.append({
            'id': message['id'],
            'sender': message['sender'],
            'content': message['content'],
            'timestamp': message['timestamp']
        })
    
    conn.close()
    
    return jsonify({
        'success': True,
        'messages': message_list
    })

def get_reply(message):
    """根据用户消息生成回复"""
    # 这里可以接入更复杂的逻辑或AI服务
    # 目前使用简单的随机回复
    
    # 如果消息是询问下载或购买
    if any(word in message.lower() for word in ['下载', '购买', '获取', '使用', '怎么得到']):
        return random.choice([
            "您可以点击素材卡片上的下载按钮直接获取该资源。",
            "这个素材是免费的，您可以直接下载使用。",
            "该素材需要高级会员才能下载，您可以考虑升级您的账户。",
            "您可以使用积分兑换此素材，或者直接购买。",
            "这个资源提供免费试用版，完整版需要付费购买。"
        ])
    
    # 如果消息是询问素材类型
    elif any(word in message.lower() for word in ['类型', '格式', '文件', '规格']):
        return random.choice([
            "我们提供多种格式的素材，包括JPG、PNG、SVG、AI、PSD等。",
            "该素材提供多种分辨率，最高可达4K。",
            "这个模板兼容Photoshop、Illustrator和Sketch。",
            "我们的素材支持商业用途，附带授权许可证。",
            "这个字体包含完整的中英文字符和多种字重。"
        ])
    
    # 如果消息是询问推荐
    elif any(word in message.lower() for word in ['推荐', '建议', '最好', '哪个好']):
        return random.choice([
            "根据您的需求，我推荐"现代简约UI套件"，它很适合您的项目。",
            "我们最受欢迎的素材是"创意营销模板包"，很多专业设计师都在使用。",
            "如果您是做网页设计，"响应式网站模板集"会是一个很好的选择。",
            "对于初学者，我建议从"基础设计元素库"开始，它包含了设计所需的基本元素。",
            "考虑到您的项目类型，"企业品牌标识套件"可能更适合您。"
        ])
    
    # 默认回复
    else:
        return random.choice([
            "我们有超过10000个精选素材，您可以尝试使用搜索功能查找更多。",
            "请问您需要哪方面的设计素材？我可以帮您筛选最合适的资源。",
            "您好，需要我为您的项目推荐一些相关素材吗？",
            "我们每周都会更新新的设计资源，欢迎定期查看。",
            "除了素材下载，我们还提供定制设计服务，需要了解更多信息吗？",
            "我可以帮您找到符合您预算和需求的最佳素材选择。"
        ])

if __name__ == '__main__':
    # 创建static目录
    os.makedirs('static', exist_ok=True)
    
    # 将前端HTML保存到static目录
    with open('static/index.html', 'w', encoding='utf-8') as f:
        f.write('''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>设计资源库 - 寻找灵感的最佳去处</title>
    <!-- 这里是HTML内容，实际使用时替换为完整的前端代码 -->
</head>
<body>
    <!-- 前端代码 -->
</body>
</html>
        ''')
    
    # 运行Flask应用
    app.run(debug=True, host='0.0.0.0', port=5000)