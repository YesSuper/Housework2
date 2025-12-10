import unittest
import sys
import os

# 将项目根目录加入路径，以便能导入 app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, Contact

class AddressBookTestCase(unittest.TestCase):
    def setUp(self):
        """每个测试前运行：配置测试数据库"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # 使用内存数据库，不污染真实数据
        app.config['WTF_CSRF_ENABLED'] = False # 测试时关闭 CSRF 检查
        
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        """每个测试后运行：清理"""
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_home_page(self):
        """测试1: 首页能否正常访问"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        # 检查页面里有没有我们在 base.html 里写的标题
        self.assertIn(b'XP Address Book', response.data)

    def test_add_contact(self):
        """测试2: 添加联系人逻辑是否生效"""
        # 模拟 POST 请求提交表单
        response = self.app.post('/add', data={
            'name': 'Test User',
            'is_bookmarked': 'on',
            'types[]': ['Phone'],
            'values[]': ['123456']
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证数据库是否真的存进去了
        contact = Contact.query.first()
        self.assertIsNotNone(contact)
        self.assertEqual(contact.name, 'Test User')
        self.assertTrue(contact.is_bookmarked)
        self.assertEqual(contact.methods[0].value, '123456')

if __name__ == '__main__':
    unittest.main()
