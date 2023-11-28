#! /usr/bin/python3

import sys
from dataclasses import dataclass
from enum import Enum
from random import choice
from time import sleep

class ExitProgram(Exception):
  pass

@dataclass
class Program:
  lines: list[str]
  w: int
  h: int
  
  def __getitem__(self, index: tuple[int, int]):
    x, y = index
    if 0 <= y < self.h:
      if 0 <= x < self.w:
        line = self.lines[y]
        if x < len(line):
          return line[x]
        return ' '
    raise Exception(f'Index out of bounds: {index}')

class Direction(Enum):
  RIGHT = 0
  DOWN = 1
  LEFT = 2
  UP = 3

@dataclass
class State:
  program: Program
  stack: list[int]
  pc: tuple[int, int]
  direction: Direction

  def pop(self):
    if not len(self.stack):
      return 0
    return self.stack.pop()

def load_program(src: str):
  lines = src.splitlines()
  w = max((len(line) for line in lines), default=0)
  h = len(lines)
  return Program(lines=lines, w=w, h=h)

def create_state(program: Program):
  return State(
    program=program, 
    stack=[], 
    pc=(0, 0), 
    direction=Direction.RIGHT
  )

def step_pc(state: State):
  x, y = state.pc
  if state.direction == Direction.RIGHT:
    x += 1
  if state.direction == Direction.DOWN:
    y += 1
  if state.direction == Direction.LEFT:
    x -= 1
  if state.direction == Direction.UP:
    y -= 1
  state.pc = (x % state.program.w, y % state.program.h)

def execute_instruction(state: State, c: str):
  if c == '+':
    a = state.pop() 
    b = state.pop() 
    state.stack.append(a + b)
  elif c == '-':
    a = state.pop() 
    b = state.pop() 
    state.stack.append(b - a)
  elif c == '*':
    a = state.pop() 
    b = state.pop() 
    state.stack.append(a * b)
  elif c == '/':
    a = state.pop()
    b = state.pop()
    if a == 0:
      raise Exception('Computing b/a where a=0; what result do you want?') 
    state.stack.append(b // a)
  elif c == '%':
    a = state.pop()
    b = state.pop()
    if a == 0:
      raise Exception('Computing b%a where a=0; what result do you want?') 
    state.stack.append(b % a)
  elif c == '!':
    a = state.pop()
    if a == 0:
      state.stack.append(1)
    else:
      state.stack.append(0)
  elif c == '`':
    a = state.pop()
    b = state.pop()
    if b > a:
      state.stack.append(1)
    else:
      state.stack.append(0)
  elif c == '>':
    state.direction = Direction.RIGHT
  elif c == 'v':
    state.direction = Direction.DOWN
  elif c == '<':
    state.direction = Direction.LEFT
  elif c == '^':
    state.direction = Direction.UP
  elif c == '?':
    state.direction = choice([d for d in Direction])
  elif c == '_':
    a = state.pop()
    if a == 0:
      state.direction = Direction.RIGHT
    else:
      state.direction = Direction.LEFT
  elif c == '|':
    a = state.pop()
    if a == 0:
      state.direction = Direction.DOWN
    else:
      state.direction = Direction.UP
  elif c == '"':
    raise NotImplementedError()
  elif c == ':':
    state.stack.append(state.stack[-1])
  elif c == '\\':
    a = state.pop()
    b = state.pop()
    state.stack.append(a)
    state.stack.append(b)
  elif c == '$':
    state.pop()
  elif c == '.':
    a = state.pop()
    sys.stderr.write(str(a))
  elif c == ',':
    a = state.pop()
    sys.stderr.write(chr(a))
  elif c == '#':
    step_pc(state)
  elif c == 'g':
    raise NotImplementedError()
  elif c == 'p':
    raise NotImplementedError()
  elif c == '&':
    while True:
      try:
        val = int(read_input(state, "Input integer > "))
        state.stack.append(val)
        break
      except ValueError:
        print("Invalid input")
  elif c == '~':
    while True:
      char = read_input(state, "Input character > ")
      if len(char) == 1:
        state.stack.append(ord(char))
      print("Invalid input")
  elif c == '@':
    raise ExitProgram()
  elif '0' <= c <= '9':
    state.stack.append(int(c))

def step_state(state: State):
  x, y = state.pc
  c = state.program[x, y]
  execute_instruction(state, c)
  step_pc(state)

write_buffer: list[str] = []
def write(s: str):
  write_buffer.append(s)

def flush():
  print("".join(write_buffer), end="", flush=True)
  write_buffer.clear()
  
def term_alt():
  write("\x1b[?1049h")

def term_noalt():
  write("\x1b[?1049l")

def term_clear():
  write("\x1b[2J\x1b[H")

def term_sgr(val: str):
  write(f"\x1b[{val}m")

def term_reset():
  write('\x1b[0m\x1b[?25h')

def term_moveto(x: int, y: int):
  write(f"\x1b[{y};{x}H")

def term_cursor():
  write("\x1b[?25h")

def term_nocursor():
  write("\x1b[?25l")

def term_savecursor():
  write("\x1b[s")

def term_loadcursor():
  write("\x1b[u")

def read_input(state: State, prompt: str):
  term_savecursor()
  term_moveto(0, state.program.h + 2)
  term_cursor()
  term_sgr('33')
  flush()
  
  print(prompt, end="")
  term_sgr('0')
  flush()

  result = input()

  term_loadcursor()
  flush()
  return result

def draw_state(state: State):
  term_clear()
  term_nocursor()
  pc_x, pc_y = state.pc
  for y, line in enumerate(state.program.lines):
    for x, char in enumerate(line.ljust(state.program.w)):
      if x == pc_x and y == pc_y:
        term_sgr('30')
        term_sgr('47')
        write(char)
        term_sgr('0')
      else:
        write(char)
    write('\n')
  flush()

def start_app(state: State):
  try:
    term_alt()
    while True:
      try:
        draw_state(state)
        step_state(state)
        sleep(1/30)
      except ExitProgram:
        break
  except KeyboardInterrupt:
    term_clear()
  finally:
    term_noalt()
    term_reset()
    flush()

def main(path: str):
  with open(path, "r") as f:
    src = f.read()
    program = load_program(src)
    state = create_state(program)
    start_app(state)

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print("Usage: befx.py path")
    exit(-1)
  path = sys.argv[1]
  main(path)
