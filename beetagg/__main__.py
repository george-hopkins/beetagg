import argparse
import sys
from . import detect
from .parser import parse, resolve


def main(args=None):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--raw', action='store_true')
    arg_parser.add_argument('--resolve', type=int, nargs='?', const=True, default=False)
    arg_parser.add_argument('image', type=str)
    args = arg_parser.parse_args(args or sys.argv[1:])

    result = detect(args.image)
    if not result:
        print('No code found', file=sys.stderr)
        return 1

    if args.resolve:
        resolved = resolve(result, None if args.resolve is True else args.resolve)
        if isinstance(resolved, str):
            print(resolved)
        else:
            if args.raw:
                print(resolved.xml)
            else:
                print(resolved.title)
                for pattern in resolved.patterns:
                    print('[{}] {} ({})'.format(pattern.number, pattern.title, pattern.mime_type))
    elif args.raw:
        sys.stdout.buffer.write(result)
    else:
        _, _, top, bottom = parse(result)
        print(top)
        print(bottom)
    return 0


if __name__ == '__main__':
    sys.exit(main())
