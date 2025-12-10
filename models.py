# models.py
from flask_sqlalchemy import SQLAlchemy

# 初始化数据库实例
db = SQLAlchemy()

class Contact(db.Model):
    """联系人主表"""
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # 【核心需求 1.1】收藏联系人 (Bookmark)
    # 使用布尔值标记，默认不收藏
    is_bookmarked = db.Column(db.Boolean, default=False)
    
    # 建立与联系方式的关系
    # cascade='all, delete-orphan' 确保删除联系人时，其联系方式一并删除，防止脏数据
    methods = db.relationship('ContactMethod', backref='contact', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        """序列化方法，方便后续转JSON或Excel"""
        return {
            'id': self.id,
            'name': self.name,
            'is_bookmarked': self.is_bookmarked,
            'methods': [m.to_dict() for m in self.methods]
        }

class ContactMethod(db.Model):
    """【核心需求 1.2】多重联系方式表"""
    __tablename__ = 'contact_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 类型：如 'Phone', 'Email', 'WeChat', 'Address'
    method_type = db.Column(db.String(50), nullable=False) 
    
    # 具体值：如 '13800138000', 'student@example.com'
    value = db.Column(db.String(200), nullable=False)
    
    # 外键关联
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=False)

    def to_dict(self):
        return {'type': self.method_type, 'value': self.value}
