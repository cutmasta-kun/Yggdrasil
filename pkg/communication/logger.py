#logger.py
import os
import sys
import logging
import argparse

def getLogger():
    # Stellen Sie den Logger ein
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG if os.getenv('DEBUG') == 'true' else logging.INFO)

    # Stellen Sie den Handler für den Logger ein
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def main(message):
    logger = getLogger()
    logger.info(message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log a message.")
    parser.add_argument('message', type=str, help='The message to log.')

    args = parser.parse_args()
    main(args.message)
