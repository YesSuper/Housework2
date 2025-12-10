# app.py
from flask import Flask, jsonify, request
from models import db, Contact, ContactMethod
import os

app = Flask(__name__)

# 配置 SQLite 数据库 (无需安装任何服务，文件型数据库)
# 务实选择：开发速度最快，完全满足作业需求
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'addressbook.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 绑定数据库
db.init_app(app)

# 在应用启动前创建数据库表
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return "Address Book Backend is Running! (XP Assignment)"

# 测试用：添加联系人的简单接口（验证模型是否工作）
@app.route('/test_add', methods=['GET'])
def test_add():
    # 模拟添加一个带有多重联系方式的联系人
    new_contact = Contact(name="Zhang San", is_bookmarked=True)
    phone = ContactMethod(method_type="Phone", value="123456789", contact=new_contact)
    email = ContactMethod(method_type="Email", value="zhang@test.com", contact=new_contact)
    
    db.session.add(new_contact)
    db.session.commit()
    return jsonify({"message": "Test contact added successfully", "contact": new_contact.to_dict()})

if __name__ == '__main__':
    app.run(debug=True, port=5000)