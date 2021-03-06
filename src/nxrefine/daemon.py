"""Generic linux daemon base class for python 3.x."""

import sys
import os
import psutil
import time
import signal
import logging

class NXDaemon:
    """A generic daemon class.

    Usage: subclass the daemon class and override the run() method."""

    def __init__(self, pid_name, pid_file):
        self.pid_name = pid_name
        self.pid_file = pid_file

    def daemonize(self):
        """Deamonize class. UNIX double fork mechanism."""
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as err:
            print.write('fork #1 failed: {0}\n'.format(err))
            sys.exit(1)
    
        # decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as err:
            print('fork #2 failed: {0}\n'.format(err))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        pid = str(os.getpid())
        with open(self.pid_file, 'w+') as f:
            f.write(pid + '\n')

    def get_pid(self):
        """Determine the pid stored in pid_file"""
        try:
            with open(self.pid_file,'r') as pf:
                return int(pf.read().strip())
        except Exception:
            return None

    def is_running(self):
        pid = self.get_pid()
        if pid and psutil.pid_exists(pid):
            return psutil.Process(pid).is_running()
        else:
            return False            
    
    def start(self):
        """Start the daemon."""

        # Check for a pid_file to see if the daemon already runs
        pid = self.get_pid()
        if pid and psutil.pid_exists(pid):
            proc = psutil.Process(pid)
            if proc.name() == self.pid_name and proc.is_running():
                sys.exit(0)

        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """Stop the daemon."""
        pid = self.get_pid()

        if os.path.exists(self.pid_file):
            os.remove(self.pid_file)

        if pid is None:
            return
        elif psutil.pid_exists(pid):
            parent = psutil.Process(pid)
            if parent.name() == self.pid_name:
                procs = parent.children(recursive=True)
                procs.append(parent)
                for p in procs:
                    p.terminate()
                gone, alive = psutil.wait_procs(procs, timeout=3)
                if alive:
                    for p in alive:
                        p.kill()
                gone, alive = psutil.wait_procs(alive, timeout=3)
                if alive:
                    for p in alive:
                        message = "Process {0} survived SIGKILL"
                        sys.stderr.write(message.format(p))


    def restart(self):
        """Restart the daemon."""
        self.stop()
        self.start()

    def run(self):
        """Run the process started by the daemon.

        It will be called after the process has been daemonized by
        start() or restart(). This should be overridden by a subclass
        """
