tunnel_downloader
=================

Downloads music files from popular service https://tunnel.ru.

Download and install to /usr/local/bin Geckodriver from https://github.com/mozilla/geckodriver/releases

    $ sudo apt-get install xvfb
    $ tunnel_downloader.py [-h] [-d OUTPUT_DIR] [-e ENVIRONMENT] [-m] [-p PACKAGES]
                           -u URL [-w WORKERS]
                     
* -h, --help - help and exit
* -d, --output_dir - output dir (default=./music)
* -m, --mix - download all in output directory
* -u, --url - tunnel page url
* -w, --workers - number of threads (default=cpu_count())
* -e , --environment - virtual environment directory (default='venv')
* -p, --packages - packages directory
