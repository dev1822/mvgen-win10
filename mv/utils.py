"""Utility functions."""

import re
import os
import subprocess
import logging
import unidecode

from . import commands as cs

logging.basicConfig(level=logging.INFO)


def natural_keys(text):
    return [
        int(t) if t.isdigit() else t
        for t in re.split('(\d+)', text)
    ]


def mkdir(path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def get_duration(filename, raise_error=False):
    cmd = cs.get_duration(filename)
    duration = os.popen(cmd)
    duration = duration.read().strip('\n')
    try:
        return float(duration)
    except Exception:
        if raise_error:
            raise ValueError(f'Invalid audio/video file {os.path.basename(filename)}')
        return 0.


def get_bitrate(filename):
    cmd = cs.get_bitrate(filename)
    duration = os.popen(cmd)
    duration = duration.read().strip('\n')
    try:
        return float(duration)
    except Exception:
        return 0.



def runcmd(cmd, raise_error=False, timeout=None):
    logging.debug(cmd)

    log = os.devnull
    with open(log, 'a') as stdout:
        res = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
        )

        try:
            out, err = res.communicate(timeout=timeout)
        except Exception as e:
            if raise_error:
                raise e
            out = str(e).encode('utf-8')

        if res.returncode != 0:
            logging.error(f'CMD ERROR: {cmd}')
            logging.error(out.decode('utf-8'))

            if raise_error:
                raise ValueError(out.decode('utf-8'))

    return res.returncode


def checkcmd(cmd):
    log = os.devnull
    with open(log, 'a') as stdout:
        res = subprocess.Popen(
            cmd, stdout=stdout, stderr=subprocess.STDOUT, shell=True
        )
        res.communicate()

    if res.returncode != 0:
        logging.error(cmd)

    return res.returncode


def modify_filename(filename, prefix=None, suffix=None):
    filename = unidecode.unidecode_expect_ascii(filename)

    whitelist = '. _-'
    filename = re.sub(r'[^\w' + whitelist + ']', '---', filename)

    fname, fext = os.path.splitext(filename)

    # Windows API has limit of 260 characters
    fname = fname[:75]

    if prefix is not None:
        fname = '{}_{}'.format(prefix, fname)
    if suffix is not None:
        fname = '{}_{}'.format(fname, suffix)

    filename = '{}{}'.format(fname, fext)

    # Remove consequetive dots
    pattern = re.compile(r'\.{2,}')
    filename = pattern.sub('.', filename)

    return filename

def modify_extension(filename, ext):
    fname, fext = os.path.splitext(filename)
    return '{}.{}'.format(fname, ext)


def str2sec(s):
    if not isinstance(s, str):
        return s

    if ':' not in s:
        return float(s)

    else:
        s = s.rsplit(':')
        return 60. * float(s[0]) + float(s[1])


def wslpath(path):
    path = str(path)
    cmd = cs.get_wslpath(path)
    new_path = os.popen(cmd)
    new_path = new_path.read().strip('\n')

    return new_path


def retry(times, exceptions):
    """
    Retry Decorator
    Retries the wrapped function/method `times` times if the exceptions listed
    in ``exceptions`` are thrown
    :param times: The number of times to repeat the wrapped function/method
    :type times: Int
    :param Exceptions: Lists of exceptions that trigger a retry attempt
    :type Exceptions: Tuple of Exceptions
    """
    def decorator(func):
        def newfn(*args, **kwargs):
            attempt = 0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    print(
                        'Exception thrown when attempting to run %s, attempt '
                        '%d of %d' % (func, attempt, times)
                    )
                    attempt += 1
            return func(*args, **kwargs)
        return newfn
    return decorator
