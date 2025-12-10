from flask import Flask, jsonify, request, send_file, render_template, redirect, url_for, flash
import os
import pandas as pd
import io
from models import db, Contact, ContactMethod

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'addressbook.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-key-for-homework' # Flash 消息需要密钥

db.init_app(app)

with app.app_context():
    db.create_all()

# --- 页面路由 ---

@app.route('/')
def index():
    # 查询所有联系人，渲染 index.html
    contacts = Contact.query.order_by(Contact.is_bookmarked.desc(), Contact.id.desc()).all()
    return render_template('index.html', contacts=contacts)

@app.route('/add', methods=['GET', 'POST'])
def add_contact():
    if request.method == 'POST':
        name = request.form.get('name')
        is_bookmarked = True if request.form.get('is_bookmarked') else False
        
        # 1. 创建联系人
        new_contact = Contact(name=name, is_bookmarked=is_bookmarked)
        db.session.add(new_contact)
        db.session.commit() # 获取ID
        
        # 2. 处理多重联系方式 (Arrays)
        types = request.form.getlist('types[]')
        values = request.form.getlist('values[]')
        
        for t, v in zip(types, values):
            if v.strip():
                method = ContactMethod(method_type=t, value=v, contact_id=new_contact.id)
                db.session.add(method)
        
        db.session.commit()
        flash('Contact added successfully!', 'success')
        return redirect(url_for('index'))
        
    return render_template('edit.html', contact=None)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_contact(id):
    contact = Contact.query.get_or_404(id)
    
    if request.method == 'POST':
        contact.name = request.form.get('name')
        contact.is_bookmarked = True if request.form.get('is_bookmarked') else False
        
        # 简单粗暴的处理方式：先删除所有旧的联系方式，再添加新的
        # 这在作业场景下是允许的，且能避免复杂的更新逻辑
        ContactMethod.query.filter_by(contact_id=contact.id).delete()
        
        types = request.form.getlist('types[]')
        values = request.form.getlist('values[]')
        for t, v in zip(types, values):
            if v.strip():
                method = ContactMethod(method_type=t, value=v, contact_id=contact.id)
                db.session.add(method)
                
        db.session.commit()
        flash('Contact updated!', 'success')
        return redirect(url_for('index'))
        
    return render_template('edit.html', contact=contact)

@app.route('/delete/<int:id>')
def delete_contact(id):
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    flash('Contact deleted.', 'warning')
    return redirect(url_for('index'))

@app.route('/bookmark/<int:id>', methods=['POST'])
def toggle_bookmark(id):
    contact = Contact.query.get_or_404(id)
    contact.is_bookmarked = not contact.is_bookmarked
    db.session.commit()
    return jsonify({'status': 'success', 'is_bookmarked': contact.is_bookmarked})

# --- 功能路由 (保留之前的) ---

@app.route('/export')
def export_excel():
    contacts = Contact.query.all()
    data_list = []
    for c in contacts:
        if not c.methods:
            data_list.append({'Name': c.name, 'Is Bookmarked': c.is_bookmarked, 'Type': '', 'Value': ''})
        else:
            for m in c.methods:
                data_list.append({'Name': c.name, 'Is Bookmarked': c.is_bookmarked, 'Type': m.method_type, 'Value': m.value})
    
    df = pd.DataFrame(data_list)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', download_name='address_book.xlsx', as_attachment=True)

@app.route('/import', methods=['POST'])
def import_excel():
    file = request.files.get('file')
    if not file:
        flash('No file uploaded', 'danger')
        return redirect(url_for('index'))
        
    try:
        df = pd.read_excel(file).fillna('')
        count = 0
        for _, row in df.iterrows():
            name = str(row.get('Name', '')).strip()
            if not name: continue
            
            contact = Contact.query.filter_by(name=name).first()
            if not contact:
                contact = Contact(name=name, is_bookmarked=str(row.get('Is Bookmarked')).lower() in ['true', '1'])
                db.session.add(contact)
                db.session.commit()
                count += 1
            
            m_type = str(row.get('Type', ''))
            m_value = str(row.get('Value', ''))
            if m_type and m_value:
                 if not ContactMethod.query.filter_by(contact_id=contact.id, value=m_value).first():
                     db.session.add(ContactMethod(contact=contact, method_type=m_type, value=m_value))
        
        db.session.commit()
        flash(f'Imported {count} new contacts successfully.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
