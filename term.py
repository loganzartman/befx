write_buffer: list[str] = []

def write(s: str):
  write_buffer.append(s)

def flush():
  print("".join(write_buffer), end="", flush=True)
  write_buffer.clear()
  
def alt():
  write("\x1b[?1049h")

def noalt():
  write("\x1b[?1049l")

def clear():
  write("\x1b[2J\x1b[H")

def sgr(val: str):
  write(f"\x1b[{val}m")

def reset():
  write('\x1b[0m\x1b[?25h')

def moveto(x: int, y: int):
  write(f"\x1b[{y};{x}H")

def cursor():
  write("\x1b[?25h")

def nocursor():
  write("\x1b[?25l")

def savecursor():
  write("\x1b[s")

def loadcursor():
  write("\x1b[u")
