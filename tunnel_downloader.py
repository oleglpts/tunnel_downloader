#!/usr/bin/python3

import os
import sys
import site
import json
import argparse
from multiprocessing import cpu_count


if __name__ == '__main__':

    # Arguments parse

    parser = argparse.ArgumentParser(prog='test_download')
    parser.add_argument('-d', '--output_dir', help='output_dir', default='./mp3')
    parser.add_argument('-e', '--environment', help='virtual environment', default='venv')
    parser.add_argument('-p', '--packages', help='packages dir', default='lib/python3.5/site-packages')
    parser.add_argument('-u', '--url', help='page URL', required=True)
    parser.add_argument('-w', '--workers', help='workers count', default=cpu_count())
    args = parser.parse_args()

    # Activate virtual environment

    if args.environment != "":
        env_path = args.environment if args.environment[0:1] == "/" else os.getcwd() + "/" + args.environment
        env_activation = env_path + '/' + 'bin/activate_this.py'
        site.addsitedir(env_path + '/' + args.packages)
        sys.path.append(os.getcwd())
        try:
            exec(open(env_activation).read())
        except NotADirectoryError as e:
            print('Virtual environment activation error')
            exit(1)

    # Start downloading

    from concurrent.futures import ThreadPoolExecutor
    from helpers import logger, http_request, download_file
    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)
    logger.info('start downloading from %s' % args.url)
    resp = http_request('get', args.url, exit_on_error=True, verify=False)
    response = [
        json.loads(
            '{"' + tag.split('</audio>')[0].replace(' =', '":').replace(
                '" ', '", "').split(', "preload')[0].replace('=', '": ') + '}')
        for tag in resp.text.split('<audio source-type = ""  in_favorite = ""  ')[1:]
    ]
    pool = ThreadPoolExecutor(max_workers=int(args.workers))

    # Download cycle

    with pool:
        for mp3 in response:
            pool.submit(download_file, mp3, args)

    # Stop download

    logger.info('stop downloading from %s' % args.url)
