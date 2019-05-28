import os
import sys
import json
import shutil
import string
import random
import urllib3
import logging
import requests
import traceback


def get_logger(logger_name, logging_format, file_name):
    """

    Get logger with path 'file name'. If permission error, create log in /tmp

    :param logger_name: logger name
    :type logger_name: str
    :param logging_format: log format
    :type logging_format: str
    :param file_name: log file name
    :type file_name: str
    :return: logger
    :rtype: logging.Logger

    """
    path, prepared = '', True
    for cat in file_name.split('/')[1:-1]:
        path += '/%s' % cat
        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except PermissionError:
                prepared = False
                break
    if not prepared:
        file_name = '/tmp/%s' % file_name.split('/')[-1]
    logging.basicConfig(level=logging.INFO, format=logging_format)
    log = logging.getLogger(logger_name)
    handler = logging.FileHandler(file_name, encoding='utf8')
    handler.setFormatter(logging.Formatter(logging_format))
    log.addHandler(handler)
    log.setLevel(level=logging.INFO)
    logging.getLogger("requests").setLevel(logging.ERROR)
    urllib3.disable_warnings()
    return log


def error_handler(log, error, message, sys_exit=False, debug_info=False):
    """

    Error handler

    :param log: logger
    :type log: logging.Logger
    :param error: current exception
    :type error: Exception or None
    :param message: custom message
    :type message: str
    :param sys_exit: if True, sys.exit(1)
    :type sys_exit: bool
    :param debug_info: if True, output traceback
    :type debug_info: bool

    """
    if debug_info:
        et, ev, tb = sys.exc_info()
        log.error(
            '%s error: %s\n%s\n--->\n--->\n' % (message, error, ''.join(traceback.format_exception(et, ev, tb))))
    else:
        log.error('%s error: %s' % (message, error))
    if sys_exit:
        log.error('Error termination')
        exit(1)


def http_request(method, url, exit_on_error=False, debug_info=False, **kwargs):
    """

    Request http(s)

    :param method: request method
    :type method: str
    :param url: request url
    :type url: str
    :param exit_on_error: if True - exit on exception
    :type exit_on_error: bool
    :param debug_info: if True - traceback on exception
    :type debug_info: bool
    :param kwargs: key arguments
    :return: response
    :rtype: request.Response

    """
    resp = None
    try:
        resp = requests.request(method, url, **kwargs)
        if resp.status_code != 200:
            logger.error('request error: %s (%s)' % (resp.text if len(resp.text) <= 80 else 'long response',
                                                     resp.reason))
    except Exception as exc:
        error_handler(logger, exc, 'request', sys_exit=exit_on_error, debug_info=debug_info)
    return resp


def download_file(event, args):
    """

    Download event

    :param event:
    :param args:
    :param auth:

    """
    # logger.info(str(event))
    resp = http_request('get', event['src'], exit_on_error=True, verify=False, stream=True)
    z_file = '%s/%s.mp3' % (args.output_dir, event['title'])
    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)
    with open(z_file, 'wb') as f:
        shutil.copyfileobj(resp.raw, f)
    logger.info('stored file  %s.mp3 to %s' % (event['title'], args.output_dir))


logger = get_logger(
    'tunnel_downloader',
    '%(levelname)-10s|%(asctime)s|%(process)d|%(thread)d| %(name)s --- %(message)s (%(filename)s:%(lineno)d)',
    './%s.log' % 'tunnel_downloader'
)
