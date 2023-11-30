from flask import Flask, render_template, request,flash,redirect,url_for,session, jsonify
from database import DBhandler
import hashlib
import sys
import math
application = Flask(__name__)
application.config["SECRET_KEY"]= "anything-you-want"
DB=DBhandler() #database.py에 들어가면 클래스있음 (DB. 이용)
@application.route("/")
def hello():
    #return render_template("index.html")
    return redirect(url_for('view_list'))

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
@application.route("/login")
def login():
    return render_template("login.html")
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
#상품등록하기
@application.route("/reg_items")
def reg_item():
    return render_template("reg_items.html")
#
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
#상품등록완료화면
@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    image_file=request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data=request.form
    DB.insert_item(data['name'],data,image_file.filename)
    return render_template("submit_item_result.html", data=data, img_path="static/images/{}".format(image_file.filename))
#전체상품조회
@application.route("/list")
def view_list():
    page = request.args.get("page", 0, type=int)
    category = request.args.get("category", "all")
    per_page=int(6) 
    per_row=int (3)
    row_count=int(per_page/per_row)
    start_idx=per_page*page
    end_idx=per_page*(page+1)
    if category=="all":
        data = DB.get_items() #전체상품조회 그대로
    else:
        data = DB.get_items_bycategory(category)
    data = dict(sorted(data.items(), key=lambda x: x[1]['phone'], reverse=True)) #정렬
    #key값으로 정렬하려면 x[0] 이용 즉,key=lambda x: x[0]
    #다른 속성으로도 정렬가능 (x[1][‘속성값’] )
    item_counts = len(data)
    if item_counts<=per_page:
        data = dict(list(data.items())[:item_counts])
    else:
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
            page_count=int(math.ceil(item_counts/per_page)), #import math 추가
            total=item_counts,
            category=category)

#상품상세화면
@application.route("/view_detail/<name>/")
def view_item_detail(name):
    print("###name:",name)
    data = DB.get_item_byname(str(name))
    print("####data:",data)
    return render_template("view_item_detail.html", name=name, data=data)

#리뷰등록하기
@application.route("/reg_review_init/<name>/")
def reg_review_init(name):
    return render_template("reg_reviews.html", name=name)
#리뷰등록완료화면
@application.route("/reg_review", methods=['POST'])
def reg_review():
    image_file2=request.files["file"]
    image_file2.save("static/images/{}".format(image_file2.filename))
    data=request.form
    DB.reg_review(data['name'],data,image_file2.filename) 
    return render_template("submit_review_result.html",data=data,img_path="static/images/{}".format(image_file2.filename))

#리뷰전체조회
@application.route("/review")
def view_review():
    page = request.args.get("page", 0, type=int)
    per_page=6 # item count to display per page
    per_row=3# item count to display per row
    row_count=int(per_page/per_row)
    start_idx=per_page*page
    end_idx=per_page*(page+1)
    data = DB.get_reviews() #read the table
    item_counts = len(data)
    data = dict(list(data.items())[start_idx:end_idx])
    tot_count = len(data)
    for i in range(row_count):#last row
        if (i == row_count-1) and (tot_count%per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else: 
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    return render_template(
        "review.html",
        datas=data.items(),
        row1=locals()['data_0'].items(),
        row2=locals()['data_1'].items(),
        limit=per_page,
        page=page,
        page_count=int((item_counts/per_page)+1),
        total=item_counts)
#리뷰상세화면
@application.route("/view_review_detail/<name>/")
def view_review_detail(name):
    print("###name:",name)
    data = DB.get_review_byname(str(name))
    print("####data:",data)
    return render_template("view_review_detail.html", name=name, data=data)
#하트
@application.route('/show_heart/<name>/', methods=['GET'])
def show_heart(name):
    my_heart = DB.get_heart_byname(session['id'],name)
    return jsonify({'my_heart': my_heart})
@application.route('/like/<name>/', methods=['POST'])
def like(name):
    my_heart = DB.update_heart(session['id'],'Y',name)
    return jsonify({'msg': '좋아요 완료!'})
@application.route('/unlike/<name>/', methods=['POST'])
def unlike(name):
    my_heart = DB.update_heart(session['id'],'N',name)
    return jsonify({'msg': '안좋아요 완료!'})
if __name__ == "__main__":
    application.run(host='0.0.0.0')