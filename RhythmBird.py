import signal
from player import Player

# So that the Program Exits on Signal Termination
ret=signal.signal(signal.SIGINT, signal.SIG_DFL)
Player()
