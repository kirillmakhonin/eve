import os
import logging
import time
import subprocess
import datetime

PROC_DIRECTORY = '/proc'
LOGGER = logging.getLogger(__name__)


def get_process_args(pid):
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
    process_info = get_active_processes()
    if filter_expression:
        process_info = {k:v for (k, v) in process_info.items() if filter_expression in v}
    return process_info

def monitor_process_state(timeout, filter_expression=None):
    while True:
        data = get_filtered(filter_expression)
        yield data
        time.sleep(timeout)

def handle_process_start(pid, args, command):
    LOGGER.info('Process started {}. ARGS = {}'.format(pid, args))
    cmd = command.format(
        pid=pid,
        args=args,
        time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    )
    LOGGER.debug('Starting command {}'.format(cmd))
    subprocess.Popen(cmd, shell=True)

def handle_process_finish(pid):
    LOGGER.info('Process finished {}'.format(pid))

def observe(filter_expression, timeout, command):
    REGISTERED_PROCESSES = {}

    for processes in monitor_process_state(timeout, filter_expression):
        old_state = set(REGISTERED_PROCESSES)
        new_state = set(processes.keys())

        for pid in (new_state - old_state):
            handle_process_start(pid, processes[pid], command)
        
        for pid in (old_state - new_state):
            handle_process_finish(pid)

        REGISTERED_PROCESSES = processes.keys()
