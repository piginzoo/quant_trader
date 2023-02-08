import atexit
import logging
import os
import traceback
from threading import current_thread

from flask import Flask, render_template, request
from werkzeug.routing import BaseConverter

from quant_trader.utils import utils, CONF
from quant_trader.server import broker
from quant_trader.server.controller import controller_api, controller_query
from quant_trader.server.scheduler import scheduler

logger = logging.getLogger(__name__)


class RegexConverter(BaseConverter):
    def __init__(self, map, *args):
        self.map = map
        self.regex = args[0]


app = Flask(__name__, root_path=os.path.join(os.getcwd(), "web_root"))
# app.jinja_env.globals.update(zip=zip)
# app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))
# app.jinja_env.auto_reload = True
# app.config['JSON_AS_ASCII'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.url_map.converters['regex'] = RegexConverter
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

logger = logging.getLogger(__name__)


@app.errorhandler(500)
def internal_server_error_500(e):
    print("异常发生：")
    traceback.print_exc()
    logger.error("====================================异常堆栈为====================================", exc_info=True)
    logger.info("==================================================================================")


# 每个URL请求之前，打印请求日志
@app.before_request
def before_request():
    if request.headers.get("X-Real-Ip"):
        logger.info("ip:%r,access:%r start-%r", request.headers.get("X-Real-Ip"), request.path, request.method)
    else:
        logger.info("local ip:%r,access:%r,start", request.remote_addr, request.path)


@app.after_request
def process_response(response):
    if request.headers.get("X-Real-Ip"):
        logger.info("ip:%r,access:%r end", request.headers.get("X-Real-Ip"), request.path)
    else:
        logger.info("local ip:%r,access:%r,end", request.remote_addr, request.path)
    return response


@app.route("/")
def index():
    return "无效的访问",403


@app.route('/favicon.ico')
def get_favicon():
    return app.send_static_file('favicon.ico')


@app.errorhandler(404)
def miss(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def error(e):
    return "服务器发生异常", 500
    # return render_template('500.html'), 500


@app.route('/<regex(".*.html"):url>')
def html_request(url):
    return render_template(url)


def startup(app):
    utils.init_logger(file=True)
    logger.debug('启动：子进程:%s,父进程:%s,线程:%r', os.getpid(), os.getppid(), current_thread())

    # 注册所有蓝图
    regist_blueprint(app)
    logger.info("注册完所有路由：\n %r", app.url_map)

    __broker = broker.get("qmt")
    __scheduler = scheduler.start_scheduler(__broker)
    logger.debug("启动了调度器Scheduler")

    # Shut down the scheduler when exiting the app
    atexit.register(shutdown, __scheduler)
    logger.info("服务器启动完成。")

    app.run(host='0.0.0.0',
            port=CONF['broker_server']['port'],
            use_reloader=False)  # use_reloader false是防止scheduler启动多次
    logger.info("系统启动完成，端口：%d", CONF['broker_server']['port'])


def shutdown(__scheduler):
    __scheduler.shutdown()
    logger.info("调度器已关闭")


def regist_blueprint(app):
    app.register_blueprint(controller_api.app)
    # app.register_blueprint(controller_callback.app)
    app.register_blueprint(controller_query.app)


logger.info("开始启动服务器...")
startup(app)
