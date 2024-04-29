# Aozaki

Really simple interepreted dynamically typed language, with pattern matching!
I've used [peco](https://github.com/true-grue/peco) by @true-grue for the parser implementation, thank you, @true-grue!

# Learn X in Y minutes, where X = aozaki

```haskell
-- Comments can appear only on start of line
  -- even like that

-- numbers
10

-- strings
"hello world"

-- arithmetic
2 + 2
2 * 2
2 + 2 * 2
2 + 2 * 2^3^4

-- let-in binding
let x = something; in x
let x = 10; y = 20; in x + y

-- let-in is pattern matching
let 10 = 10; in 10

-- functions
x: x + 10

-- functions are curried
x: y: x + y

-- function application
(x: x + 10) 10 -- 20

-- function application operator
(x: x + 10) $ 10 -- 20

-- pattern matching
case (10) of {
  10 -> 20,
  30 -> 40,
} -- 20, brackets and braces are necessary

-- function arguments are pattern matched, actually
(10: 20) 10 -- 20
(10: 20) 20 -- exception!

-- in aozaki, all your custom types tied to single `struct` (aka product) type
{ x, y }
-- this defines type that is composed of two fields: x and y

{ x, y } 10 20 -- by applying values to type you can get instance of it
{} -- this is value of type {}

-- structs can be pattern matched
case ({ x, y } 10 20) of {
  { z: z } -> "this can't happen",
  { x: x, y: y } -> x + y,

  -- Patterns are checked from top to bottom, so interpreter will pick pattern that matched first
  { x: x } -> "this will happen",
  {} -> "this will happen",
} -- 30

-- Putting it all together
let some = { some };
    none = {};
    unwrap_or = or: maybe:
      case (maybe) of {
        { some: x } -> x,
        _ -> or
      };
    map = f: maybe:
      case (maybe) of {
        { some: x } -> some $ f x,
        n -> n,
      };
in map (x: x + 10) $ some $ unwrap_or 10 (some 20)
-- some 30
```

# Examples

For examples, see [examples](examples/) folder.

