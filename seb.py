from flask import Flask, request, make_response, jsonify
from flask_mail import Mail, Message
import datetime
import functions_SEB
from keys import mail_pwd

app = Flask(__name__)

mail = Mail(app)
app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_SSL=False,
    MAIL_USE_TLS=True,
    MAIL_USERNAME = 'mailvulgaris@gmail.com',
    MAIL_PASSWORD = mail_pwd
)
mail = Mail(app)

# ###################### Decorators #########################################
@app.route('/')
def index():
    return 'Webhooks for SharedExpensesBot'

@app.route('/webhook', methods=['POST'])
def webhook():
    # Get request parameters
    req = request.get_json(silent=True, force=True)
    action = req.get('result').get('action')

    # CommonBalanceBot - welcome
    if action == "commonbalancebot-welcome":
        req_for_uid = functions_SEB.check_for_logs(req)["payload"]
        ourspeech = functions_SEB.welcome_response(req_for_uid)["payload"]
        res = functions_SEB.commonbalancebot_speech(ourspeech, action, req['result']['contexts'])

    # CommonBalanceBot - create log
    elif action == "commonbalancebot-create_log":
        ourspeech = functions_SEB.create_log(req)["payload"]
        res = functions_SEB.commonbalancebot_speech(ourspeech, action, req['result']['contexts'])

    # CommonBalanceBot - switch log button clicked
    elif action == "commonbalancebot-switch_log_button":
        req_for_uid = functions_SEB.check_for_logs(req)["payload"]
        ourspeech = functions_SEB.switch_log_response(req_for_uid)["payload"]
        res = functions_SEB.commonbalancebot_speech(ourspeech, action, req['result']['contexts'])

    # CommonBalanceBot - switch log
    elif action == "commonbalancebot-switch_log":
        ourspeech = functions_SEB.switch_log(req)["payload"]
        res = functions_SEB.commonbalancebot_speech(ourspeech, action, req['result']['contexts'])

    # CommonBalanceBot - delete log
    elif action == "commonbalancebot-delete_log":
        req_for_uid = functions_SEB.check_for_logs(req)["payload"]
        ourspeech = functions_SEB.delete_log_response(req_for_uid, req['result']['contexts'])
        res = functions_SEB.commonbalancebot_speech(ourspeech["payload"], action, ourspeech["contexts"])

    # CommonBalanceBot - delete log - deletion confirmed
    elif action == "commonbalancebot-delete_log-do_it":
        ourspeech = functions_SEB.delete_log(req)["payload"]
        res = functions_SEB.commonbalancebot_speech(ourspeech, action, req['result']['contexts'])

    # CommonBalanceBot - add new user
    elif action == "commonbalancebot-add_user":
        ourspeech = functions_SEB.add_user(req)["payload"]
        res = functions_SEB.commonbalancebot_speech(ourspeech, action, req['result']['contexts'])

    # CommonBalanceBot - remove user
    elif action == "commonbalancebot-delete_user":
        ourspeech = functions_SEB.delete_user(req)["payload"]
        res = functions_SEB.commonbalancebot_speech(ourspeech, action, req['result']['contexts'])

    # CommonBalanceBot - add new payment OR modify existing payment
    elif action == "commonbalancebot-add_payment":
        result = functions_SEB.add_payment(req)
        if result["status"] != "error":
            functions_SEB.update_balance(req)
            ourspeech = functions_SEB.balance(req)["payload"]
        else:
            ourspeech = result["payload"]
        res = functions_SEB.commonbalancebot_speech(ourspeech, action, req['result']['contexts'])

    # CommonBalanceBot - delete payment
    elif action == "commonbalancebot-delete_payment":
        ourspeech = functions_SEB.delete_payment(req)["payload"]
        functions_SEB.update_balance(req)
        res = functions_SEB.commonbalancebot_speech(ourspeech, action, req['result']['contexts'])

    # CommonBalanceBot - modify payment (display payment to be modified)
    elif action == "commonbalancebot-modify_payment":
        ourspeech = functions_SEB.display_payment2modify(req)["payload"]
        res = functions_SEB.commonbalancebot_speech(ourspeech, action, req['result']['contexts'])

    # CommonBalanceBot - show balance
    elif action == "commonbalancebot-balance":
        functions_SEB.update_balance(req)
        user = req.get('result').get('parameters').get('user')
        if user == "":
            user = "all"
        ourspeech = functions_SEB.balance(req, user)["payload"]
        res = functions_SEB.commonbalancebot_speech(ourspeech, action, req['result']['contexts'])

    # CommonBalanceBot - show statement
    elif action == "commonbalancebot-statement":
        ourspeech = functions_SEB.statement(req)["payload"]
        res = functions_SEB.commonbalancebot_speech(ourspeech, action, req['result']['contexts'])

    # CommonBalanceBot - get json
    elif action == "commonbalancebot-getjson":
        ourspeech = 'hello'
        #print(str(req))
        res = functions_SEB.commonbalancebot_speech2(ourspeech, action, req['result']['contexts'])

    # CommonBalanceBot - taking user back to conversation
    elif action == "commonbalancebot-besidethepoint":
        ourspeech = functions_SEB.besidethepoint()["payload"]
        res = functions_SEB.commonbalancebot_speech(ourspeech, action, req['result']['contexts'])

    # CommonBalanceBot - sending statement to email
    elif action == "commonbalancebot-statement_to_email":
        print("Sending email!")
        email = req.get("result").get("parameters").get("email")
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        statement2mail = functions_SEB.statement(req)["payload"]["rich_messages"][0]["speech"].replace("\n","<br>")
        msg = Message("SharedExpensesBot: Statement as of {}".format(current_datetime), sender="mailvulgaris@gmail.com", recipients=[email])
        msg.html = "{}<br><br>Thanks for using SharedExpensesBot!<br>Iurii Dziuban - March 2018 / <a href='https://iuriid.github.io/'>iuriid.github.io</a>".format(statement2mail)
        mail.send(msg)

        ourspeech = {"speech": "Statemen was successfully sent to your email", "rich_messages": [{"platform": "telegram", "type": 0, "speech": "Statemen was successfully sent to your email"}]}
        res = functions_SEB.commonbalancebot_speech(ourspeech, action, req['result']['contexts'])

    # CommonBalanceBot - display FAQ
    elif action == "commonbalancebot-faq":
        ourspeech = functions_SEB.faq()["payload"]
        res = functions_SEB.commonbalancebot_speech(ourspeech, action, req['result']['contexts'])

    else:
        # If the request is not of our actions throw an error
        res = {
            'speech': 'Something wrong happened',
            'displayText': 'Something wrong happened'
        }

    return make_response(jsonify(res))
# ###################### Decorators END ##############################

if __name__ == '__main__':
    #port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0')#, port=port)