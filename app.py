from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"  # セッション管理・フラッシュメッセージ用

DATABASE = 'cafe_app.db'

def get_db_connection():
    """SQLite データベースへの接続を返す"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # 結果を dict 形式で扱えるようにする
    return conn

# 商品登録画面の表示（GET）
@app.route('/add_product', methods=['GET'])
def add_product_form():
    return render_template('add_product.html')

# 商品登録処理（POST）
@app.route('/add_product', methods=['POST'])
def add_product():
    # フォームから入力データを取得
    name = request.form.get('name')
    description = request.form.get('description')
    category = request.form.get('category')
    unit_price = request.form.get('unit_price')

    # 必須項目のチェック（ここでは「商品名」と「単価」を必須としています）
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
    conn = get_db_connection()
    sql = '''
        INSERT INTO Product (Name, Description, Category, UnitPrice)
        VALUES (?, ?, ?, ?)
    '''
    conn.execute(sql, (name, description, category, unit_price))
    conn.commit()
    conn.close()

    flash('商品が正常に登録されました。')
    return redirect(url_for('add_product_form'))

if __name__ == '__main__':
    app.run(debug=True)

# http://127.0.0.1:5000/add_product にアクセス