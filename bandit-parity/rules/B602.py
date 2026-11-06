import subprocess
from subprocess import Popen as pop

# ruleid: B602
pop("ls", shell=True)
# ruleid: B602
subprocess.call("ls", shell="False")
# ruleid: B602
subprocess.run("ls", shell=flag)
# ruleid: B602
subprocess.check_call("ls", shell=[True])
subprocess.check_output(
    "ls",
    # ruleid: B602
    shell=True,
)
# ok: B602
subprocess.run("ls", shell=False)
# ok: B602
subprocess.run("ls", shell=None)
# ok: B602
subprocess.run("ls", shell=0)
# ok: B602
subprocess.run("ls", shell=[])
# ok: B602
subprocess.run("ls", shell={})
# ok: B602
subprocess.run("ls")
# ok: B602
Popen("ls", shell=True)
# ok: B602
subprocess.call("ls", shell=True)  # nosec
# ok: B602
subprocess.call("ls", shell=True)  # nosec B602
# ok: B602
subprocess.call("ls", shell=True)  # nosec subprocess_popen_with_shell_equals_true
# ruleid: B602
subprocess.call("#nosec", shell=True)
# ruleid: B602
subprocess.call("ls", shell=True)  # nosec B607
subprocess.call("ls",  # nosec
                # ok: B602
                shell=True)
subprocess.call("ls",
                # ok: B602
                shell=True)  # nosec
