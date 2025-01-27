from flask import request
from flask_init import app
import logging
import sys
import yql

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d %(funcName)s] %(message)s', datefmt='%Y-%m-%d:%H:%M:%S', level=logging.DEBUG)

@app.route("/yql/bibleref")
def yql_bibleref():
    return yql.yqlBibleRefHandler(request)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8080', debug=True)
