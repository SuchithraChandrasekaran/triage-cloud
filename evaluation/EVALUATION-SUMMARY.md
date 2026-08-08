# What the results show — Day 35

I ran 12 test messages through the system, covering three things: budget
checks, failure checks, and architecture suggestions.

All 12 ended up correct, but not all on the first try. 10 out of 12 worked
right away. The other 2 failed the first time, and both failures pointed to
real problems I hadn't noticed before:

- One failure showed that my matching logic had a bug - it was checking a
  whole sentence as one block instead of checking each part of it
  separately. Once I fixed that, it worked.
- The other failure was simpler - I had written down a failure type but never 
actually added it to the database the system checks against.
So of course it couldn't find something that wasn't there.
