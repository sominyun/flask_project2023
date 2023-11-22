from flask import Flask, render_template, request,flash,redirect,url_for,session
from database import DBhandler
import hashlib
import sys
application = Flask(__name__)
application.config["SECRET_KEY"]= "anything-you-want"
DB=DBhandler()
@application.route("/")
def hello():
    #return render_template("index.html")
    return redirect(url_for('view_list'))

@application.route("/login")
def login():
    return render_template("login.html")
# 회원가입
@application.route("/signup")
def signup():
    return render_template("signup.html")
@application.route("/signup_post",methods=['POST'])
def register_user():
    data=request.form
    pw=request.form['pw']
    pw_hash=hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.insert_user(data,pw_hash):
        return render_template("login.html")
    else:
        flash("user id already exist!")
        return render_template("signup.html")
# 로그인 하기
@application.route("/login_confirm", methods=['POST'])
def login_user():
    id_=request.form['id']
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.find_user(id_,pw_hash):
        session['id']=id_
        return redirect(url_for('view_list'))
    else:
        flash("Wrong ID or PW!")
        return render_template("login.html")
# 로그아웃
@application.route("/logout")
def logout_user():
    session.clear()
    return redirect(url_for('view_list'))

#전체상품조회
@application.route("/list")
def view_list():
    page = request.args.get("page", 0, type=int)
    per_page=int(6) 
    per_row=int (3)
    row_count=int(per_page/per_row)
    start_idx=per_page*page
    end_idx=per_page*(page+1)
    data = DB.get_items() 
    item_counts = len(data)
    data = dict(list(data.items())[start_idx:end_idx])
    tot_count = len(data)
    for i in range(row_count): 
        if (i == row_count-1) and (tot_count%per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else: 
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    return render_template(
            "list.html",
            datas=data.items(),
            row1=locals()['data_0'].items(),
            row2=locals()['data_1'].items(),
            limit=per_page,
            page=page,
            page_count=int((item_counts/per_page)+1),
            total=item_counts)

#상품상세화면

@application.route("/view_detail/<name>/")
def view_item_detail(name):
    print("###name:",name)
    data = DB.get_item_byname(str(name))
    print("####data:",data)
    return render_template("detail.html", name=name, data=data)

@application.route("/review")
def view_review():
    return render_template("review.html")
@application.route("/reg_items")
def reg_item():
    return render_template("reg_items.html")
@application.route("/reg_reviews")
def reg_review():
    return render_template("reg_reviews.html")

@application.route("/submit_item")
def reg_item_submit():
    name=request.args.get("name")
    seller=request.args.get("seller")
    addr=request.args.get("addr")
    email=request.args.get("email")
    category=request.args.get("category")
    card=request.args.get("card")
    status=request.args.get("status")
    phone=request.args.get("phone")
    print(name,addr,tel,category,park,time,site)
@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    image_file=request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data=request.form

    DB.insert_item(data['name'],data,image_file.filename)

    return render_template("submit_item_result.html", data=data, img_path="static/images/{}".format(image_file.filename))

if __name__ == "__main__":
    application.run(host='0.0.0.0')

