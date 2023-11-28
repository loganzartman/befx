#! /usr/bin/python3

import argparse
from dataclasses import dataclass
from enum import Enum
from random import choice
from time import sleep

import term

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
    raise IndexError(f'Index out of bounds: {index}')

  def __setitem__(self, index: tuple[int, int], val: str):
    assert len(val) == 1
    x, y = index
    if 0 <= y < self.h:
      if 0 <= x < self.w:
        line = self.lines[y]
        if x > len(line):
          line = line.ljust(self.w)
        self.lines[y] = f'{line[:x]}{val}{line[x+1:]}'
        return
    raise IndexError(f'Index out of bounds: {index}')

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
  stringmode: bool
  output: list[str]

  def push(self, val: int):
    self.stack.append(val)

  def pop(self):
    if not len(self.stack):
      return 0
    return self.stack.pop()
  
  def get_output(self):
    return "".join(self.output)

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
    direction=Direction.RIGHT,
    stringmode=False,
    output=[]
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
  if state.stringmode and c != '"':
    state.push(ord(c))
    return

  if c == ' ':
    pass
  elif c == '+':
    a = state.pop() 
    b = state.pop() 
    state.push(a + b)
  elif c == '-':
    a = state.pop() 
    b = state.pop() 
    state.push(b - a)
  elif c == '*':
    a = state.pop() 
    b = state.pop() 
    state.push(a * b)
  elif c == '/':
    a = state.pop()
    b = state.pop()
    if a == 0:
      raise Exception('Computing b/a where a=0; what result do you want?') 
    state.push(b // a)
  elif c == '%':
    a = state.pop()
    b = state.pop()
    if a == 0:
      raise Exception('Computing b%a where a=0; what result do you want?') 
    state.push(b % a)
  elif c == '!':
    a = state.pop()
    if a == 0:
      state.push(1)
    else:
      state.push(0)
  elif c == '`':
    a = state.pop()
    b = state.pop()
    if b > a:
      state.push(1)
    else:
      state.push(0)
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
    state.stringmode = not state.stringmode
  elif c == ':':
    a = state.pop()
    state.push(a)
    state.push(a)
  elif c == '\\':
    a = state.pop()
    b = state.pop()
    state.push(a)
    state.push(b)
  elif c == '$':
    state.pop()
  elif c == '.':
    a = state.pop()
    state.output.append(str(a))
  elif c == ',':
    a = state.pop()
    state.output.append(chr(a))
  elif c == '#':
    step_pc(state)
  elif c == 'g':
    y = state.pop()
    x = state.pop()
    try:
      code = ord(state.program[x, y])
    except IndexError:
      code = 0
    state.push(code)
  elif c == 'p':
    y = state.pop()
    x = state.pop()
    v = state.pop()
    state.program[x, y] = chr(v)
  elif c == '&':
    while True:
      try:
        val = int(read_input(state, "Input integer > "))
        state.push(val)
        break
      except ValueError:
        print("Invalid input")
  elif c == '~':
    while True:
      char = read_input(state, "Input character > ")
      if len(char) == 1:
        state.push(ord(char))
        break
      print("Invalid input")
  elif c == '@':
    raise ExitProgram()
  elif '0' <= c <= '9':
    state.push(int(c))
  else:
    raise NotImplementedError(f'Unsupported command "{c}"')

def step_state(state: State):
  x, y = state.pc
  c = state.program[x, y]
  execute_instruction(state, c)
  step_pc(state)

def read_input(state: State, prompt: str):
  term.write('\n')
  term.cursor()
  term.sgr('33')
  term.flush()
  
  print(prompt, end="")
  term.sgr('0')
  term.flush()

  result = input()

  term.flush()
  return result

def draw_program(state: State):
  pc_x, pc_y = state.pc
  for y, line in enumerate(state.program.lines):
    for x, char in enumerate(line.ljust(state.program.w)):
      if x == pc_x and y == pc_y:
        term.sgr('30')
        term.sgr('47')
        term.write(char)
        term.sgr('0')
      else:
        term.write(char)
    term.write('\n')

def draw_stack(state: State):
  term.sgr('34')
  items_int = ", ".join(str(x) for x in state.stack)
  items_str = ", ".join(chr(x) for x in state.stack)
  term.write(f"Stack (int): {items_int}\n")
  term.write(f"Stack (str): {items_str}\n")
  term.sgr('0')
  
def draw_output(state: State):
  term.sgr('32')
  term.write("Output:\n")
  term.sgr('0')
  term.write(state.get_output())
  term.sgr('0')

def draw_state(state: State):
  term.loadcursor()
  term.savecursor()
  term.clear_down()
  term.nocursor()
  draw_program(state)
  term.write("\n")
  draw_stack(state)
  draw_output(state)
  term.flush()

def start_app(state: State, framerate: int):
  try:
    term.savecursor()
    while True:
      try:
        draw_state(state)
        step_state(state)
        sleep(1/framerate)
      except ExitProgram:
        break
  except KeyboardInterrupt:
    pass
  finally:
    term.reset()
    term.flush()

def run_to_exit(state: State):
  try:
    while True:
      try:
        step_state(state)
        print(state.get_output(), end="")
        state.output.clear()
      except ExitProgram:
        break
  except KeyboardInterrupt:
    pass
  print()

def main(path: str, framerate: int, headless: bool):
  with open(path, "r") as f:
    src = f.read()
    program = load_program(src)
    state = create_state(program)
    if headless:
      run_to_exit(state)
    else:
      start_app(state, framerate)

def parse_args():
  parser = argparse.ArgumentParser(description="Animation script arguments")
  parser.add_argument('path', type=str,
                      help='Path to the script to execute')
  parser.add_argument('-f', '--framerate', type=int, default=30,
                      help='Set the animation framerate (in frames per second)')
  parser.add_argument('-H', '--headless', action='store_true',
                      help='Enable headless mode; only output the results')
  return parser.parse_args()

if __name__ == '__main__':
  args = parse_args()
  main(args.path, args.framerate, args.headless)
