Programming
===========

Python
------

List Comprehension
^^^^^^^^^^^^^^^^^^

A list comprehension is just a shorthand way of defining a function.

  [do stuff to x    for x in list      if x>0]       ##The if x>0 is optional

Is the same as this:

  def omg(list):
    for x in list:
      if x>0:
        do stuff to x

Eg:
  poweroftwo = [x**2 for x in range(10)]
  ifdivbytwo = [x for x in poweroftwo if x % 2 == 0]

You can perform more than one operation on each item in your list too:
  wordlist = 'The quick brown fox jumps over the lazy dog'.split()
  derp = [[w.upper(), w.lower(), len(w)] for w in wordlist]


What's a lambda?
^^^^^^^^^^^^^^^^

lambda is just an in-place, anonymous function. Eg:
  addTwo = lambda x: x+2
  addTwo(2)  #4

It's the same thing as defining this:
  def addTwo(x):
    return x+2

You can even throw them into dictionaries/hash trees:
  mapTree = {
      'number': lambda x: x**x,
      'string': lambda x: x[1:]
  }
  otype = 'number'
  mapTree[otype](3)  #27
  otype = 'string'
  mapTree[otype]('foo')  #'oo'

It's really just a syntactical thing. It's good if you know that your "function" is only going to be used once, by one thing. Otherwise just create a def(). Note above that ** means to the power of.

One good use for it is with the key= value in your sort() and sorted(). eg:
  pairs = [(1, 'one'), (2, 'two'), (3, 'three'), (4, 'four')]
  pairs.sort(key=lambda english: english[1])
This will sort by the second value of each tuple, giving this:
  [(4, 'four'), (1, 'one'), (3, 'three'), (2, 'two')]

Why __main__?
^^^^^^^^^^^^^
Why do some python files have this? Why should you use it in your python scripts?
  if __name__ == '__main__':
    main()

The python interpreter, when it reads a source (.py) file, will execute everything in it. If, for example, "python myfirstscript.py" is ran, then the interpreter prior to running the source will set the special variable "__name__" to equal "__main__". If, inside of myfirstscript.py, you have "import random_module", then the interpreter will set the __name__ variable for that module to its name, in this case "random_module".

So what's the point? Well, let's say random_module.py could, if you wanted, be ran by itself. myfirstscript.py is just importing it because it has some functions in there that are useful. Well, the interpreter just runs whatever code it opens up. If inside the random_module script you don't have the if __name__ == '__main__': main_function() clause, then the interpreter is just going to run the file. You probably don't want this...you just want the functions out of it, you are running myfirstscript.py not random_module.py. So, if you make sure the if __name__ clause is the only thing that starts the actual work of the script, then you can avoid this.

Doing it this way, you can still run random_module from inside myfirstscript.py if you want. Just do this:
  import random_module
  random_module.main()

Decorators
^^^^^^^^^^
http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/

A decorator is just a callable that takes a function as an argument, and returns a replacement function. Let's create a simple decorator:

  def outer(some_func):
    def inner():
      print "i'm the inner function"
      ret = some_func()
      return ret + 1
    return inner
  def foo():
    return 1
  
  decorated = outer(foo)
  decorated()
  ..i'm the inner function
  ..2

outer() **returns a function**, inner(), which applies some operation on whatever function is passed to outer(). In this example, outer() is our "decorator" and it is "decorating" the foo() function (we passed it foo, and it's adding 1 to whatever foo returned).

In fact, we can completely replace our foo object with its decorated version by re-assigning it:

  foo = outer(foo)

This works since outer(foo) is ran first, uses the original foo() definition, and then assigns the result to the foo object, overwriting the old foo definition. From now on, any calls to foo() won't get the original foo, they'll get our decorated version.

We can use the myfunc = wrapper(myfunc) syntax as mentioned above, but python provides support to do this simply by using @wrapper above some function:

  @wrapper
  def myfunc:
    return blahblahblah

So what's the point? Well, slapping a memory/cpu/other performance profiling wrapper on some function could let you see how many calls it's making, how much memory it is allocating, and whatever else. There also exists situations where you have a class or function in which you cannot change the source code of, but need to extend its functionality. You may also want to write a wrapper that logs all arguments passed to a certain function, or some wrapper that does some bounds checking/filtering on function output, or any use case where you only want to temporarily apply some decorator to some function, where adding a simple @decorator above a function is much easier than changing the function itself.

Quickies
^^^^^^^^
Both list.sort() and sorted() have a **key** parameter which allows you to specify *a function to be called on each list element*. The results of this will determine how elements in a list are sorted.

  students = [ ('john','A','23'), ('jamal','B','32'), ('jerry','C','42') ]
  sorted(students, key=lambda stu: stu[2])  #sort by age, the 3rd element in each tuple

Stacks
------
Stacks are useful (and one of the original) data structures which are well suited to expression evaluation and variable storage (in particular, holding variables outside of a subroutine). 

FIFO  (first in first out) stacks are useful as they naturally work with the structure of code. The deeper you nest into if/for/whatever, each level has variables. As you nest back up to the top, these variables are popped off in order.

Another reason stacks are useful is if a subroutine is called by multiple threads at the same time, or are recursively called. In this instance, a variable could be set to one value by one thread, and then changed to another value by another thread, thereby invalidating the result. To prevent this, a stack can be allocated in memory which essentially gives the subroutine a working memory it can use. Each call of the subroutine pushes and pulls more stuff onto and off the stack.


Registers
---------
A register is a small bit of information that lives in the register file, which resides in a small bit of memory on the CPU.

Usually the EAX register holds a return value. EBP is the stack pointer, pointing to the beginning of your stack. Then you've got the program counter, which points to the current instruction, EIP. The other registers you just use however you want. 

In assembly, these registers are referred to through names like %eax, %esp, %rdi, %edi, etc.


Classes
-------
You can think of a class as a template, it's a struct basically. It holds variables with default values, functions(/methods, described below). 

Let's say you've got a class defined like this:
  class Door:
    scopeExample1 = 'inside the class'
    def open(self, arrrg):
      print 'hello stranger'
      scopeExample2 = 'inside the method inside the class'
      self.scopeExample3 = 'using self. inside the method inside the class'
      if arrrg:
        print arrrg

You can instantiate a class (create a class object) like this (mfi means my_first_instantiation):
  mfi = Door()

Now you have an object that contains all the properties inside the class. Test some stuff:
  mfi.open() ## hello stranger
  mfi.open('blahhh') ## hello stranger \n blahhh
  scopeExample1  ##NameError. Not defined.
  mfi.scopeExample1  ## 'inside the class'
  mfi.scopeExample2  ##Door instance has no attribute scopeExample2
  mfi.scopeExample3  ##Door instance has no attribute scopeExample3
  mfi.self.scopeExample3


  class Door:
    def open(self):
      print 'hello stranger'
  
  def knock_door:
    a_door = Door()
    Door.open(a_door)
  
  knock_door()
