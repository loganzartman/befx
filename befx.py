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
    a = state.stack.pop() 
    b = state.stack.pop() 
    state.stack.append(a + b)
  elif c == '-':
    a = state.stack.pop() 
    b = state.stack.pop() 
    state.stack.append(b - a)
  elif c == '*':
    a = state.stack.pop() 
    b = state.stack.pop() 
    state.stack.append(a * b)
  elif c == '/':
    a = state.stack.pop()
    b = state.stack.pop()
    if a == 0:
      raise Exception('Computing b/a where a=0; what result do you want?') 
    state.stack.append(b // a)
  elif c == '%':
    a = state.stack.pop()
    b = state.stack.pop()
    if a == 0:
      raise Exception('Computing b%a where a=0; what result do you want?') 
    state.stack.append(b % a)
  elif c == '!':
    a = state.stack.pop()
    if a == 0:
      state.stack.append(1)
    else:
      state.stack.append(0)
  elif c == '`':
    a = state.stack.pop()
    b = state.stack.pop()
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
    a = state.stack.pop()
    if a == 0:
      state.direction = Direction.RIGHT
    else:
      state.direction = Direction.LEFT
  elif c == '|':
    a = state.stack.pop()
    if a == 0:
      state.direction = Direction.DOWN
    else:
      state.direction = Direction.UP
  elif c == '"':
    raise NotImplementedError()
  elif c == ':':
    state.stack.append(state.stack[-1])
  elif c == '\\':
    a = state.stack.pop()
    b = state.stack.pop()
    state.stack.append(a)
    state.stack.append(b)
  elif c == '$':
    state.stack.pop()
  elif c == '.':
    a = state.stack.pop()
    sys.stderr.write(str(a))
  elif c == ',':
    a = state.stack.pop()
    sys.stderr.write(chr(a))
  elif c == '#':
    step_pc(state)
  elif c == 'g':
    raise NotImplementedError()
  elif c == 'p':
    raise NotImplementedError()
  elif c == '&':
    raise NotImplementedError()
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

def term_clear():
  write("\x1b[2J\x1b[H")

def term_sgr(val: str):
  write(f"\x1b[{val}m")

def term_reset():
  write('\x1b[0m\x1b[?25h')

def term_moveto(x: int, y: int):
  write("\x1b[{y};{x}H")

def draw_state(state: State):
  term_clear()
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
    while True:
      try:
        step_state(state)
        draw_state(state)
        sleep(1/30)
      except ExitProgram:
        break
  except KeyboardInterrupt:
    term_clear()
  finally:
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
