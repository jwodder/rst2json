.. topic:: **Proof:** There exist infinitely many prime numbers.

    Assume that the set :math:`P` of all prime numbers is nonempty and finite.
    As :math:`P` is a finite set of integers, :math:`x = \prod P` and :math:`y
    = x+1` are integers; moreover, as every element of :math:`P` is greater
    than one, :math:`1<p\leq\prod P = x<y` for all :math:`p\in P`.  As
    :math:`y>1`, :math:`y` must be either prime or composite.

    If :math:`y` is prime, then, as it is greater than every element of
    :math:`P`, it cannot be in :math:`P`, and so there exists a prime not in
    :math:`P`.

    Otherwise, if :math:`y` is composite, then it must be divisible by some
    prime :math:`p`.  It cannot be that :math:`p\in P`; for, if possible, let
    it be so: then :math:`p` divides :math:`\prod P = x`, and as :math:`p` also
    divides :math:`y = x+1`, :math:`p` must divide :math:`y-x=1`, which is
    absurd.  Thus, there exists a prime not in :math:`P`.

    Therefore, given a nonempty finite set of primes, there exists a prime
    number not in that set, and as the set of all primes is known to be
    nonempty, it cannot be finite, i.e., it must be infinite.
