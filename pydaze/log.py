import datetime
import sys


def println(*args):
    pre = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    print(pre + ' ' + ' '.join([str(i) for i in args]))


def panicln(*args):
    println(*args)
    raise Exception(' '.join(str(e) for e in args))


def fatalln(*args):
    println(*args)
    println('exit status 1')
    sys.exit(1)
