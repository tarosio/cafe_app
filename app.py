from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション用の秘密鍵
DATABASE = 'cafe_app.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ホーム画面
@app.route('/home')
def home():
    if 'user_id' not in session:
        flash('ログインしてください。')
        return redirect(url_for('login'))
    return render_template('home.html')

# ログイン画面と処理
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('ユーザー名とパスワードを入力してください。')
            return redirect(url_for('login'))
        try:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM User WHERE Username = ?', (username,)).fetchone()
            conn.close()
            if user and check_password_hash(user['Password'], password):
                session['user_id'] = user['ID']
                session['username'] = user['Username']
                session['role'] = user['Role']
                flash('ログインしました！')
                return redirect(url_for('home'))  # ログイン後はホームへ
            else:
                flash('ユーザー名またはパスワードが間違っています。')
                return redirect(url_for('login'))
        except Exception as e:
            flash(f"エラーが発生しました: {str(e)}")
            return redirect(url_for('login'))
    return render_template('login.html')

# ログアウト処理
@app.route('/logout')
def logout():
    session.clear()
    flash('ログアウトしました。')
    return redirect(url_for('login'))

# ユーザー登録
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        
        if not username or not password:
            flash('ユーザー名とパスワードを入力してください。')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO User (Username, Password, Role) VALUES (?, ?, ?)', 
                         (username, hashed_password, role))
            conn.commit()
            conn.close()
            flash('登録が完了しました。ログインしてください。')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'登録時にエラーが発生しました: {str(e)}')
            return redirect(url_for('register'))
    return render_template('register.html')

# 商品追加画面（GET/POST）
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session:
        flash('ログインしてください。')
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        unit_price = request.form.get('unit_price')

        if not name or not unit_price:
            flash('商品名と単価は必須です。')
            return redirect(url_for('add_product'))

        try:
            unit_price = float(unit_price)
        except ValueError:
            flash('単価は数値で入力してください。')
            return redirect(url_for('add_product'))

        try:
            conn = get_db_connection()
            conn.execute(''' 
                INSERT INTO Product (Name, Description, Category, UnitPrice) 
                VALUES (?, ?, ?, ?) 
            ''', (name, description, category, unit_price))
            conn.commit()
            conn.close()
            flash('商品が正常に登録されました。')
            return redirect(url_for('add_product'))
        except Exception as e:
            flash(f"商品登録時にエラーが発生しました: {str(e)}")
            return redirect(url_for('add_product_form'))
    return render_template('add_product.html')

# 商品一覧画面
@app.route('/product')
def product():
    if 'user_id' not in session:
        flash('ログインしてください。')
        return redirect(url_for('login'))
    return render_template('product.html')

# 取引追加画面（GET/POST）
@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if 'user_id' not in session:
        flash('ログインしてください。')
        return redirect(url_for('login'))
    if request.method == 'POST':
        # ここに取引追加処理を実装（仮実装）
        flash('取引が追加されました。（仮）')
        return redirect(url_for('add_transaction_form'))
    return render_template('add_transaction.html')

# 取引一覧画面
@app.route('/transaction')
def transaction():
    if 'user_id' not in session:
        flash('ログインしてください。')
        return redirect(url_for('login'))
    return render_template('transaction.html')

# 在庫一覧画面
@app.route('/stock_list')
def stock_list():
    if 'user_id' not in session:
        flash('ログインしてください。')
        return redirect(url_for('login'))
    try:
        conn = get_db_connection()
        products = conn.execute('SELECT * FROM Product').fetchall()
        conn.close()
        return render_template('stock_list.html', products=products)
    except Exception as e:
        flash(f"在庫取得時にエラーが発生しました: {str(e)}")
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
