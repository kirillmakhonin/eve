"""
Main package logic
"""

import os
import logging
import time
import subprocess
import datetime

PROC_DIRECTORY = '/proc'
LOGGER = logging.getLogger(__name__)


def get_process_args(pid):
    """
    Get string with process args by process id (PID)
    
    :param pid: process id
    :type pid: int
    :raises Exception: if cannot gather process args from /proc directory
    :return: process args
    :rtype: str
    """
    if not os.path.exists(PROC_DIRECTORY):
        raise Exception('Cannot find directory {}'.format(PROC_DIRECTORY))
    try:
        path = os.path.join(PROC_DIRECTORY, str(pid), 'cmdline')
        with open(path, 'r') as file:
            return file.read()
    except Exception as args_read_exception:
        LOGGER.error('Cannot read {} process\'es args: {}'.format(pid, args_read_exception))
        return ''

def get_active_processes():
    """
    Get list of active processes
    
    :raises Exception: if cannot access /proc directory
    :return: dict of process id => process args
    :rtype: dict[int, str]
    """
    if not os.path.exists(PROC_DIRECTORY):
        raise Exception('Cannot find directory {}'.format(PROC_DIRECTORY))
    processes = [
        int(d) for d in os.listdir(PROC_DIRECTORY) 
        if d.isnumeric() 
        and os.path.isdir(os.path.join(PROC_DIRECTORY, d))
        and int(d) != os.getpid()]
    return {
        pid: get_process_args(pid)
        for pid in processes
    }
    
def get_filtered(filter_expression=None):
    """
    Get active processes dict and filter by process args
    
    :param filter_expression: substrict that should be in process args
    :type filter_expression: typing.Optional[str]
    :return: filtered result of get_active_processes function
    :rtype: dict[int, str]
    """
    process_info = get_active_processes()
    if filter_expression:
        process_info = {k:v for (k, v) in process_info.items() if filter_expression in v}
    return process_info

def monitor_process_state(timeout, filter_expression=None):
    """
    Generator that produces yield with filtered process information
    
    :param timeout: sleep between data events
    :type timeout: int
    :param filter_expression: substrict that should be in process args
    :type filter_expression: typing.Optional[str]
    :return: filtered result of get_active_processes function
    :rtype: dict[int, str]
    """
    while True:
        data = get_filtered(filter_expression)
        yield data
        time.sleep(timeout)

def handle_process_start(pid, args, command):
    """
    Perform action of process start
    
    :param pid: process id
    :type pid: int
    :param args: process args
    :type args: str
    :param command: command to start
    :type command: str
    """
    LOGGER.info('Process started {}. ARGS = {}'.format(pid, args))
    cmd = command.format(
        pid=pid,
        args=args,
        time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    )
    LOGGER.debug('Starting command {}'.format(cmd))
    subprocess.Popen(cmd, shell=True)

def handle_process_finish(pid):
    """
    Perform action of process finish
    
    :param pid: process id
    :type pid: int
    """
    LOGGER.info('Process finished {}'.format(pid))

def observe(filter_expression, timeout, command):
    """
    Start process lookup loop and handle updates
    
    :param filter_expression: substrict that should be in process args
    :type filter_expression: typing.Optional[str]
    :param timeout: sleep between data events
    :type timeout: int
    :param command: command to start
    :type command: str
    """

    REGISTERED_PROCESSES = {}

    for processes in monitor_process_state(timeout, filter_expression):
        old_state = set(REGISTERED_PROCESSES)
        new_state = set(processes.keys())

        for pid in (new_state - old_state):
            handle_process_start(pid, processes[pid], command)
        
        for pid in (old_state - new_state):
            handle_process_finish(pid)

        REGISTERED_PROCESSES = processes.keys()
