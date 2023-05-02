# README

## How to run the code

```
mpirun -np 1 python Main.py Problem{2,3,4}.py test#.txt
```
Do NOT change the number of processes to run it is automatically detected in test.txt file

Important Notes:
- To demonstrate the behavior of future messages in problem 2, comment out line 60, and uncomment 62-68.
- To demonstrate the behavior of a slow process in problem 3, comment out lines 32-33
- To switch between the synchronous or asynchronous behavior, swicth the lines 72-73 comments. 
