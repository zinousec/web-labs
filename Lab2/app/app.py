from flask import Flask, render_template, request, make_response

app = Flask(__name__)
application = app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/headers')
def headers():
    return render_template("headers.html")
    
@app.route('/args')
def args():
    return render_template("args.html")

@app.route('/cookies')
def cookies():
    resp = make_response(render_template("cookies.html"))
    if 'q' in request.cookies: 
        resp.set_cookie('q', 'qq', expires = 0)
    else:
        resp.set_cookie('q', 'qq')

    return resp

@app.route('/form', methods = ['GET', 'POST'])
def form():
    return render_template("form.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

@app.route('/calc', methods = ['GET', 'POST'])
def calc():
    errormsg = None
    res = None
    if request.method == 'POST': 
        try: 
            op1 = int(request.form.get('operand1'))
            op2 = int(request.form.get('operand2'))
            operator = request.form.get('operator')
            if operator == '+':
                res = op1 + op2
            elif operator == '-':
                res = op1 - op2
            elif operator == '*':
                res = op1 * op2
            elif operator == '/':
                res = op1 / op2
        except ZeroDivisionError: 
            errormsg = "На ноль делить нельзя"
        except ValueError: 
            errormsg = "Вводите только числа"
    return render_template('calc.html', res=res, errormsg=errormsg)


@app.route('/phone', methods = ['GET', 'POST'])
def phone():
    errormsg = []
    true_phone = False
    if request.method == 'POST': 
        true_phone = True
        n_phone = request.form.get('n_phone')
        n_phone = n_phone.replace('(','')
        n_phone = n_phone.replace(')','')
        n_phone = n_phone.replace('.','')
        n_phone = n_phone.replace('-','')
        n_phone = n_phone.replace(' ','')
        for simvol in n_phone:
            if (simvol != '+'):
                try:
                    int(simvol)
                except ValueError:
                    errormsg.append("Недопустимый ввод. В номере телефона встречаются недопустимые символы.")
                    true_phone = False

        if (len(n_phone) > 0):
            if (n_phone[0] == '8'):
                if (len(n_phone) != 11):
                    errormsg.append("Недопустимый ввод. Неверное количество цифр.")
                    true_phone = False
            elif (n_phone[0] == '+' and n_phone[1] == '7'):
                if (len(n_phone) != 12):
                    errormsg.append("Недопустимый ввод. Неверное количество цифр.")
                    true_phone = False
            elif (len(n_phone) != 10):
                    errormsg.append("Недопустимый ввод. Неверное количество цифр.")
                    true_phone = False
        else:
            errormsg.append("Введите номер телефона")
            true_phone = False
    return render_template("phone.html", true_phone=true_phone, errormsg=errormsg)
