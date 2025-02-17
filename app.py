from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Flaskアプリケーションのインスタンス化
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッションやフラッシュメッセージ用の秘密鍵

DATABASE = 'cafe_app.db'

# データベース接続を取得するための関数
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ログインページの表示（GET）
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

# ログイン処理（POST）
@app.route('/login', methods=['POST'])
def login_post():
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
            return redirect(url_for('stock_list'))  # ここをstock_listに変更
        else:
            flash('ユーザー名またはパスワードが間違っています。')
            return redirect(url_for('login'))
    except Exception as e:
        flash(f"エラーが発生しました: {str(e)}")
        return redirect(url_for('login'))

# ログアウト処理
@app.route('/logout')
def logout():
    session.clear()  # セッションの情報をクリア
    flash('ログアウトしました。')
    return redirect(url_for('login'))

# 在庫一覧画面の表示（GET）
@app.route('/stock_list', methods=['GET'])
def stock_list():
    if 'user_id' not in session:
        flash('ログインしてください。')
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        # 商品情報と在庫情報を取得するクエリを修正
        products = conn.execute('SELECT * FROM Product').fetchall()
        conn.close()
        return render_template('stock_list.html', products=products)  # stock_list.htmlに渡す
    except Exception as e:
        flash(f"在庫取得時にエラーが発生しました: {str(e)}")
        return redirect(url_for('login'))

# 商品登録画面の表示（GET）
@app.route('/add_product', methods=['GET'])
def add_product_form():
    if 'user_id' not in session:
        flash('ログインしてください。')
        return redirect(url_for('login'))
    return render_template('add_product.html')

# 商品登録処理（POST）
@app.route('/add_product', methods=['POST'])
def add_product():
    if 'user_id' not in session:
        flash('ログインしてください。')
        return redirect(url_for('login'))

    # フォームから入力データを取得
    name = request.form.get('name')
    description = request.form.get('description')
    category = request.form.get('category')
    unit_price = request.form.get('unit_price')

    # 必須項目のチェック
    if not name or not unit_price:
        flash('商品名と単価は必須です。')
        return redirect(url_for('add_product_form'))

    # 単価を float に変換（変換できなければエラー）
    try:
        unit_price = float(unit_price)
    except ValueError:
        flash('単価は数値で入力してください。')
        return redirect(url_for('add_product_form'))

    # データベースに登録する
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO Product (Name, Description, Category, UnitPrice)
            VALUES (?, ?, ?, ?)
        ''', (name, description, category, unit_price))
        conn.commit()
        conn.close()
        flash('商品が正常に登録されました。')
        return redirect(url_for('add_product_form'))
    except Exception as e:
        flash(f"商品登録時にエラーが発生しました: {str(e)}")
        return redirect(url_for('add_product_form'))

# 商品一覧画面の表示（GET）
@app.route('/products', methods=['GET'])
def product_list():
    if 'user_id' not in session:
        flash('ログインしてください。')
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        products = conn.execute('SELECT * FROM Product').fetchall()
        conn.close()
        return render_template('products.html', products=products)
    except Exception as e:
        flash(f"商品取得時にエラーが発生しました: {str(e)}")
        return redirect(url_for('login'))

# ユーザー登録画面の表示（GET）
@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')  # ユーザー登録フォームを表示

# ユーザー登録処理（POST）
@app.route('/register', methods=['POST'])
def register_post():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')  # 追加

    # 入力チェック
    if not username or not password or not role:
        flash('すべての項目を入力してください。')
        return redirect(url_for('register'))

    # パスワードをハッシュ化
    hashed_password = generate_password_hash(password)

    # データベースに登録
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO User (Username, Password, Role, AccountCreatedAt)
            VALUES (?, ?, ?, datetime('now'))
        ''', (username, hashed_password, role))
        conn.commit()
        conn.close()
        flash('ユーザー登録が完了しました！')
        return redirect(url_for('login'))  # ログインページへ遷移
    except Exception as e:
        flash(f"ユーザー登録時にエラーが発生しました: {str(e)}")
        return redirect(url_for('register'))

if __name__ == '__main__':
    app.run(debug=True)
