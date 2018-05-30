import argparse
from client import Client


def create_parser():
    parser_ = argparse.ArgumentParser()
    parser_.add_argument('-addr', type=str, help='Server name or address')
    parser_.add_argument('-port', type=int, help='Port to connect')
    return parser_


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()
    parameters = namespace.__dict__ if namespace else {}
    client = Client(**parameters)
    client.start()
