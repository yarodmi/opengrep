import subprocess
import subprocess as sp
from subprocess import Popen as pop

# ruleid: B602
subprocess.Popen("/bin/ls", shell=True)
# ruleid: B602
pop("/bin/ls *", shell=True)
# ruleid: B602
sp.run("ls", shell="False")
# ruleid: B602
subprocess.call("ls", shell=1)
# ruleid: B602
subprocess.check_call("ls", shell=[True])
# ruleid: B602
subprocess.check_output("ls", shell={"enabled": True})
# ruleid: B602
subprocess.call("ls", shell=setting)
subprocess.check_output(
    "ls",
    # ruleid: B602
    shell=True,
)

# ok: B602
subprocess.Popen("ls", shell=False)
# ok: B602
subprocess.call("ls", shell=0)
# ok: B602
subprocess.call("ls", shell=[])
# ok: B602
subprocess.call("ls", shell={})
# ok: B602
subprocess.call("ls", shell=None)
# ok: B602
subprocess.call("ls")
# ok: B602
subprocess.getoutput("ls", shell=True)
# ok: B602
subprocess.Popen(args="ls", shell=True)

def Popen(*args, **kwargs):
    pass

# ok: B602
Popen("ls", shell=True)

# ok: B602
subprocess.call("ls", shell=True)  # nosec
# ok: B602
subprocess.call("ls", shell=True)  # nosec B602
# ok: B602
subprocess.call("ls", shell=True)  # nosec subprocess_popen_with_shell_equals_true
# ruleid: B602
subprocess.call("#nosec", shell=True)  # nosec B607
# ok: B602
subprocess.call("ls",  # nosec
                shell=True)
subprocess.call("ls",
                # ok: B602
                shell=True)  # nosec

def independent_calls():
    # ok: B602
    subprocess.call("ls", shell=True)  # nosec
    # ruleid: B602
    subprocess.call("pwd", shell=True)
    # ok: B602
    subprocess.call("ls",  # nosec
                    shell=True)
    # ruleid: B602
    subprocess.call("pwd", shell=True)
    setting = False
    # ruleid: B602
    subprocess.call("ls", shell=setting)
