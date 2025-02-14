from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

# Flaskアプリケーションのインスタンス化
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッションやフラッシュメッセージ用の秘密鍵

DATABASE = 'cafe_app.db'

# データベース接続を取得するための関数
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
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
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO Product (Name, Description, Category, UnitPrice)
        VALUES (?, ?, ?, ?)
    ''', (name, description, category, unit_price))
    conn.commit()
    conn.close()

    flash('商品が正常に登録されました。')
    return redirect(url_for('add_product_form'))

# 商品一覧画面の表示（GET）
@app.route('/products', methods=['GET'])
def product_list():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM Product').fetchall()
    conn.close()
    return render_template('products.html', products=products)

# 入出庫登録画面の表示（GET）
@app.route('/add_transaction', methods=['GET'])
def add_transaction_form():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM Product').fetchall()
    users = conn.execute('SELECT * FROM User').fetchall()
    conn.close()
    return render_template('add_transaction.html', products=products, users=users)

# 入出庫登録処理（POST）
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    product_id = request.form.get('product_id')
    user_id = request.form.get('user_id')
    quantity = request.form.get('quantity')
    movement_type = request.form.get('movement_type')
    notes = request.form.get('notes')

    # 必須項目のチェック
    if not product_id or not user_id or not quantity or not movement_type:
        flash('すべての必須項目を入力してください。')
        return redirect(url_for('add_transaction_form'))

    # 数量を整数に変換
    try:
        quantity = int(quantity)
    except ValueError:
        flash('数量は整数で入力してください。')
        return redirect(url_for('add_transaction_form'))

    # データベースに登録する（StockMovementテーブルに変更）
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO StockMovement (ProductID, "UserID", Quantity, MovementType, MovementDate, Notes)
        VALUES (?, ?, ?, ?, datetime('now'), ?)
    ''', (product_id, user_id, quantity, movement_type, notes))
    conn.commit()
    conn.close()

    flash('入出庫が正常に登録されました。')
    return redirect(url_for('add_transaction_form'))

@app.route('/transaction', methods=['GET'])
def transaction_list():
    conn = get_db_connection()  # インデントを追加
    transaction = conn.execute('''
        SELECT StockMovement.ID, Product.Name, User.Username, StockMovement.Quantity, StockMovement.MovementType, StockMovement.MovementDate, StockMovement.Notes
        FROM StockMovement
        JOIN Product ON StockMovement.ProductID = Product.ID
        JOIN User ON StockMovement.UserID = User.ID
        ORDER BY StockMovement.MovementDate DESC
    ''').fetchall()
    conn.close()
    return render_template('transaction.html', transaction=transaction)

@app.route('/stock', methods=['GET'])
def stock_list():
    conn = get_db_connection()

    # 商品ごとの最新の入出庫履歴を取得し、在庫数と最終更新時間を計算する
    query = '''
        SELECT Product.ID, Product.Name, Product.Category, Product.UnitPrice,
        COALESCE(SUM(CASE WHEN StockMovement.MovementType = '入庫' THEN StockMovement.Quantity
        WHEN StockMovement.MovementType = '出庫' THEN -StockMovement.Quantity
        ELSE 0 END), 0) AS CurrentStock,
        MAX(StockMovement.MovementDate) AS LastUpdated
        FROM Product
        LEFT JOIN StockMovement ON Product.ID = StockMovement.ProductID
        GROUP BY Product.ID
    '''
    products = conn.execute(query).fetchall()
    conn.close()

    return render_template('stock_list.html', products=products)

# 商品編集画面の表示（GET）
@app.route('/edit_product/<int:product_id>', methods=['GET'])
def edit_product_form(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM Product WHERE ID = ?', (product_id,)).fetchone()
    conn.close()

    if product is None:
        flash('商品が見つかりませんでした。')
        return redirect(url_for('product_list'))

    return render_template('edit_product.html', product=product)

# 商品編集処理（POST）
@app.route('/edit_product/<int:product_id>', methods=['POST'])
def edit_product(product_id):
    name = request.form.get('name')
    description = request.form.get('description')
    category = request.form.get('category')
    unit_price = request.form.get('unit_price')

    # 必須項目のチェック
    if not name or not unit_price:
        flash('商品名と単価は必須です。')
        return redirect(url_for('edit_product_form', product_id=product_id))

    # 単価を float に変換（変換できなければエラー）
    try:
        unit_price = float(unit_price)
    except ValueError:
        flash('単価は数値で入力してください。')
        return redirect(url_for('edit_product_form', product_id=product_id))

    # データベースの更新
    conn = get_db_connection()
    conn.execute('''
        UPDATE Product
        SET Name = ?, Description = ?, Category = ?, UnitPrice = ?
        WHERE ID = ?
    ''', (name, description, category, unit_price, product_id))
    conn.commit()
    conn.close()

    flash('商品情報が更新されました。')
    return redirect(url_for('product_list'))

@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    # データベースから商品を削除
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()

    # 商品削除後、商品一覧ページにリダイレクト
    return redirect(url_for('products'))


if __name__ == '__main__':
    app.run(debug=True)
