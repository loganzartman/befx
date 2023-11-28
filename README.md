# befx

Execute [Befunge][befunge] code. "beef-ex".

![demo image](demo.gif)

## what

This is a mostly complete Befunge-93 interpreter! Befunge is an esoteric language that executes in two dimensions!

## usage

Run with visualization:

```
python befx.py examples/helloworld.befunge
```

Run faster:

```
python befx.py -f 100 examples/helloworld.befunge
```

Headless mode; no visualization:

```
python befx.py -H examples/helloworld.befunge
```

[befunge]: https://esolangs.org/wiki/Befunge
