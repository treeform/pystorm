"""Mersenne Twister random number generator

Usage:
>>> from mtrandom import *
>>> r = MersenneTwister()
>>> for i in range(10): print r.random()

To compare with the original mt19937ar.c:
$ gcc mt19937ar.c && ./a.out > tmp1
$ python mtrandom.py > tmp2
$ diff tmp1 tmp2

See:
http://millerideas.com/?page_id=47
"""
"""
   Converted to Python by Jeff Miller
   2007-02-03
   jwmillerusa (at) gmail (dot) com
   http://millerideas.com

   =======================================================================
   Code from CPython's random module is subject to the following:
   http://www.python.org/psf/license/
   =======================================================================

   =======================================================================
   Mersenne Twister code is subject to the following:
   (Below are the original comments from the authors' C source file.)
   =======================================================================

   A C-program for MT19937, with initialization improved 2002/1/26.
   Coded by Takuji Nishimura and Makoto Matsumoto.

   Before using, initialize the state by using init_genrand(seed)
   or init_by_array(init_key, key_length).

   Copyright (C) 1997 - 2002, Makoto Matsumoto and Takuji Nishimura,
   All rights reserved.

   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions
   are met:

     1. Redistributions of source code must retain the above copyright
        notice, this list of conditions and the following disclaimer.

     2. Redistributions in binary form must reproduce the above copyright
        notice, this list of conditions and the following disclaimer in the
        documentation and/or other materials provided with the distribution.

     3. The names of its contributors may not be used to endorse or promote
        products derived from this software without specific prior written
        permission.

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
   ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
   LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
   CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
   SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
   INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
   ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
   POSSIBILITY OF SUCH DAMAGE.


   Any feedback is very welcome.
   http://www.math.sci.hiroshima-u.ac.jp/~m-mat/MT/emt.html
   email: m-mat @ math.sci.hiroshima-u.ac.jp (remove space)
"""

# Period parameters
N = 624
M = 397
MATRIX_A = 0x9908b0dfL   # constant vector a
UPPER = 0x80000000L  # most significant w-r bits
LOWER = 0x7fffffffL  # least significant r bits

class MersenneTwister:
    def __init__(self, s=None):
        self.mt = [0]*N  # the array for the state vector
        self.mti = N+1   # mti==N+1 means mt is not initialized
        self.gauss_next = 0.0
        self.gauss_switch = 0
        self.seed(s)

    def seed(self, s=None):
        # if not s: s = long(time.time() * 256)
        if not s: s = long(0)
        #self.init_genrand(long(s))
        self.init_by_array([s])

    def random(self):
        return self.genrand_res53()

    def getstate(self):
        """Return internal state; can be passed to setstate() later."""
        return self.mti, self.mt, self.gauss_next, self.gauss_switch

    def setstate(self, state):
        """Restore internal state from object returned by getstate()."""
        self.mti, self.mt, self.gauss_next, self.gauss_switch = state

    def jumpahead(self, n):
        """(Not implemented - Does nothing)
        Provided for basic compatibility with CPython's random modules."""
        pass

## -------------------- pickle support  -------------------

    def __getstate__(self): # for pickle
        return self.getstate()

    def __setstate__(self, state):  # for pickle
        self.setstate(state)

    def __reduce__(self):
        return self.__class__, (), self.getstate()

    """
    =======================================================================
    Mersenne Twister code
    The following methods closely match the original C source code.
    =======================================================================
    """

    # initializes mt with a seed
    def init_genrand(self, s):
        self.mt[0]= s & 0xffffffffL
        for self.mti in range(1,N):
            self.mt[self.mti] = (1812433253L * (self.mt[self.mti-1] ^ \
                    ((self.mt[self.mti-1] >> 30) & 3)) + self.mti)
            # See Knuth TAOCP Vol2. 3rd Ed. P.106 for multiplier.
            # In the previous versions, MSBs of the seed affect
            # only MSBs of the array mt[].
            # 2002/01/09 modified by Makoto Matsumoto

            # JM: Added "& 3" for signed int representation of unsigned int.
            # In the original C code, unsigned ints were used, so
            # right-bitshifting resulted in 0's filling in from the left.
            # However, SS currently only supports signed ints, so we need
            # to imitate unsigned ints. Signed ints normally fill in 1's
            # from the left on right-bitshifts, so we force 0's with the &.
            # (Applied below also for all other right-bitshift operations.)

            self.mt[self.mti] &= 0xffffffffL
            # for >32 bit machines
        self.mti += 1

    # initialize by an array with array-length
    # init_key is the array for initializing keys
    # slight change for C++, 2004/2/26
    def init_by_array(self, init_key, key_length=-1):
        if key_length < 0:
		key_length = len(init_key)
        self.init_genrand(19650218L)
        i,j = 1,0
        k = max(N, key_length)
        for k in range(k,0,-1):
            self.mt[i] = (self.mt[i] ^ ((self.mt[i-1] ^ ((self.mt[i-1]>>30)&3))\
                    * 1664525L)) + init_key[j] + j  # non linear
            self.mt[i] &= 0xffffffffL  # for WORDSIZE > 32 machines
            i+=1; j+=1
            if (i>=N): self.mt[0] = self.mt[N-1]; i=1
            if (j>=key_length): j=0

        for k in range(N-1, 0, -1):
            self.mt[i] = (self.mt[i] ^ ((self.mt[i-1] ^ ((self.mt[i-1]>>30)&3))\
                    * 1566083941L)) - i   # non linear
            self.mt[i] &= 0xffffffffL  # for WORDSIZE > 32 machines
            i+=1
            if (i>=N): self.mt[0] = self.mt[N-1]; i=1

        self.mt[0] = 0x80000000L  # MSB is 1; assuring non-zero initial array


    # generates a random number on [0,0xffffffff]-interval
    def genrand_int32(self):
        mag01 = [0x0L, MATRIX_A]
        # mag01[x] = x * MATRIX_A  for x=0,1

        if (self.mti >= N):  # generate N words at one time

            if (self.mti == N+1):  # if init_genrand() has not been called,
                self.init_genrand(5489L)  # a default initial seed is used

            for kk in range(N-M):
                y = (self.mt[kk] & UPPER) | (self.mt[kk+1] & LOWER)
                self.mt[kk]= self.mt[kk+M] ^ ((y>>1)&LOWER) ^ mag01[y&0x1L]
                    # JM: Added "& LOWER" to (y>>1) for int repr of uint
            
            for kk in range(kk+1, N-1):  # k+1 because range omits last value
                y = (self.mt[kk] & UPPER) | (self.mt[kk+1] & LOWER)
                self.mt[kk] = self.mt[kk+(M-N)] ^ ((y>>1)&LOWER) ^ mag01[y&0x1L]
            
            y = (self.mt[N-1] & UPPER) | (self.mt[0] & LOWER)
            self.mt[N-1] = self.mt[M-1] ^ ((y>>1) & LOWER) ^ mag01[y&0x1L]
            self.mti = 0

        y = self.mt[self.mti]
        self.mti += 1

        # Tempering
        # (JM: Added "& ~(-1 << (32-B))" for signed int repr of unsigned int)
        y ^= (y >> 11) & ~(-1 << (32-11))
        y ^= (y << 7) & 0x9d2c5680L
        y ^= (y << 15) & 0xefc60000L
        y ^= (y >> 18) & ~(-1 << (32-18))

        return y


    # generates a random number on [0,1]-real-interval
    def genrand_real1(self):
        #return self.genrand_int32()*(1.0/4294967295.0)
        # divided by 2^32-1
        r = self.genrand_int32()*(1.0/4294967295.0)
        return r + (r<0)  # (JM: Added so that int or unsigned int can be used)

    # generates a random number on [0,1)-real-interval
    def genrand_real2(self):
        #return self.genrand_int32()*(1.0/4294967296.0)
        # divided by 2^32
        r = self.genrand_int32()*(1.0/4294967296.0)
        return r + (r<0)  # (JM: Added so that int or unsigned int can be used)

    # generates a random number on (0,1)-real-interval
    def genrand_real3(self):
        #return (float(self.genrand_int32()) + 0.5)*(1.0/4294967296.0)
        r = float(self.genrand_int32())
        return (r + (r>0)-0.5)*(1.0/4294967296.0) + (r<0)
        # divided by 2^32

    # generates a random number on [0,1) with 53-bit resolution
    def genrand_res53(self):
        a = (self.genrand_int32()>>5) & ~(-1 << (32-5))
        b = (self.genrand_int32()>>6) & ~(-1 << (32-6))
        return (a*67108864.0+b)*(1.0/9007199254740992.0); 

    # These real versions are due to Isaku Wada, 2002/01/09 added



    """
    =======================================================================
    CPython code
    The following methods are taken from random.py
    =======================================================================
    """


## -------------------- integer methods  -------------------

    def randrange(self, start, stop, step=1):
        """Choose a random item from range(start, stop[, step]).

        This fixes the problem with randint() which includes the
        endpoint; in Python this is usually not what you want.
        Do not supply the 'int', 'default', and 'maxwidth' arguments.
        """
        # Note: In CPython, stop is optional, with a default of None. However,
        # this behavior doesn't seem possible in Shed Skin unless scalar
        # variables can have a None value.

        istart = int(start)
        if istart != start:
            raise ValueError, "non-integer arg 1 for randrange()"

        istop = int(stop)
        if istop != stop:
            raise ValueError, "non-integer stop for randrange()"
        width = istop - istart
        if step == 1 and width > 0:
            return int(istart + int(self.random()*width))
        if step == 1:
            raise ValueError, "empty range for randrange()"

        # Non-unit step argument supplied.
        istep = int(step)
        if istep != step:
            raise ValueError, "non-integer step for randrange()"
        if istep > 0:
            n = (width + istep - 1) / istep
        elif istep < 0:
            n = (width + istep + 1) / istep
        else:
            raise ValueError, "zero step for randrange()"

        if n <= 0:
            raise ValueError, "empty range for randrange()"

        return istart + istep*int(self.random() * n)


    def randint(self, a, b):
        """Return random integer in range [a, b], including both end points.
        """
        return self.randrange(a, b+1)


## -------------------- sequence methods  -------------------

    def choice(self, seq):
        """Choose a random element from a non-empty sequence."""
        return seq[int(self.random() * len(seq))]

    def shuffle(self, x):
        """x, random=random.random -> shuffle list x in place; return None.

        Note that for even rather small len(x), the total number of
        permutations of x is larger than the period of most random number
        generators; this implies that "most" permutations of a long
        sequence can never be generated.
        """
        # Note: CPython supports another optional arg, a function that is
        # called instead of random.

        for i in range(len(x)-1, 0, -1):
            # pick an element in x[:i+1] with which to exchange x[i]
            j = int(self.random() * (i+1))
            x[i], x[j] = x[j], x[i]

    def sample(self, population, k):
        """Chooses k unique random elements from a population sequence.

        Returns a new list containing elements from the population while
        leaving the original population unchanged.  The resulting list is
        in selection order so that all sub-slices will also be valid random
        samples.  This allows raffle winners (the sample) to be partitioned
        into grand prize and second place winners (the subslices).

        Members of the population need not be hashable or unique.  If the
        population contains repeats, then each occurrence is a possible
        selection in the sample.
        """

        # Sampling without replacement entails tracking either potential
        # selections (the pool) in a list or previous selections in a
        # dictionary.

        # When the number of selections is small compared to the population,
        # then tracking selections is efficient, requiring only a small
        # dictionary and an occasional reselection.  For a larger number of
        # selections, the pool tracking method is preferred since the list takes
        # less space than the dictionary and it doesn't suffer from frequent
        # reselections.

        n = len(population)
        if not 0 <= k <= n:
            raise ValueError, "sample larger than population"
        if n==0:
            raise ValueError, "population to sample has no members"
        result = [population[0]] * k
        if n < 6 * k:     # if n len list takes less space than a k len dict
            pool = list(population)
            for i in range(k):         # invariant:  non-selected at [0,n-i)
                j = int(self.random() * (n-i))
                result[i] = pool[j]
                pool[j] = pool[n-i-1]   # move non-selected item into vacancy
        else:
            try:
                n > 0 and (population[0], population[n//2], population[n-1])
            except (TypeError, KeyError):   # handle sets and dictionaries
                population = tuple(population)
            selected = {}
            for i in range(k):
                j = int(self.random() * n)
                while j in selected:
                    j = int(self.random() * n)
                result[i] = selected[j] = population[j]
        return result

## -------------------- real-valued distributions  -------------------

## -------------------- uniform distribution -------------------

    def uniform(self, a, b):
        """Get a random number in the range [a, b)."""
        return a + (b-a) * self.random()

## -------------------- normal distribution --------------------

    def normalvariate(self, mu, sigma):
        """Normal distribution.

        mu is the mean, and sigma is the standard deviation.

        """
        # mu = mean, sigma = standard deviation

        # Uses Kinderman and Monahan method. Reference: Kinderman,
        # A.J. and Monahan, J.F., "Computer generation of random
        # variables using the ratio of uniform deviates", ACM Trans
        # Math Software, 3, (1977), pp257-260.

        #random = self.random
        while True:
            u1 = self.random()
            u2 = 1.0 - self.random()
            z = NV_MAGICCONST*(u1-0.5)/u2
            zz = z*z/4.0
            if zz <= -math.log(u2):
                break
        return mu + z*sigma

## -------------------- lognormal distribution --------------------

    def lognormvariate(self, mu, sigma):
        """Log normal distribution.

        If you take the natural logarithm of this distribution, you'll get a
        normal distribution with mean mu and standard deviation sigma.
        mu can have any value, and sigma must be greater than zero.

        """
        return math.exp(self.normalvariate(mu, sigma))

## -------------------- circular uniform --------------------
    # This function has been deprecated in CPython.
    def cunifvariate(self, mean, arc):
        return math.fmod((mean + arc * (self.random() - 0.5)), math.pi)

## -------------------- exponential distribution --------------------

    def expovariate(self, lambd):
        """Exponential distribution.

        lambd is 1.0 divided by the desired mean.  (The parameter would be
        called "lambda", but that is a reserved word in Python.)  Returned
        values range from 0 to positive infinity.

        """
        # lambd: rate lambd = 1/mean
        # ('lambda' is a Python reserved word)

        #random = self.random
        u = self.random()
        while u <= 1e-7:
            u = self.random()
        return -math.log(u)/lambd

## -------------------- von Mises distribution --------------------

    def vonmisesvariate(self, mu, kappa):
        """Circular data distribution.

        mu is the mean angle, expressed in radians between 0 and 2*pi, and
        kappa is the concentration parameter, which must be greater than or
        equal to zero.  If kappa is equal to zero, this distribution reduces
        to a uniform random angle over the range 0 to 2*pi.

        """
        # mu:    mean angle (in radians between 0 and 2*pi)
        # kappa: concentration parameter kappa (>= 0)
        # if kappa = 0 generate uniform random angle

        # Based upon an algorithm published in: Fisher, N.I.,
        # "Statistical Analysis of Circular Data", Cambridge
        # University Press, 1993.

        # Thanks to Magnus Kessler for a correction to the
        # implementation of step 4.

        #random = self.random
        if kappa <= 1e-6:
            return 2*math.pi * self.random()

        a = 1.0 + math.sqrt(1.0 + 4.0 * kappa * kappa)
        b = (a - math.sqrt(2.0 * a))/(2.0 * kappa)
        r = (1.0 + b * b)/(2.0 * b)

        while True:
            u1 = self.random()

            z = math.cos(math.pi * u1)
            f = (1.0 + r * z)/(r + z)
            c = kappa * (r - f)

            u2 = self.random()

            if not (u2 >= c * (2.0 - c) and u2 > c * math.exp(1.0 - c)):
                break

        u3 = self.random()
        if u3 > 0.5:
            #theta = (mu % TWOPI) + math.acos(f)
            theta = math.fmod(mu, 2*math.pi) + math.acos(f)
        else:
            #theta = (mu % TWOPI) - math.acos(f)
            theta = math.fmod(mu, 2*math.pi) - math.acos(f)

        return theta

## -------------------- gamma distribution --------------------

    def gammavariate(self, alpha, beta):
        """Gamma distribution.  Not the gamma function!

        Conditions on the parameters are alpha > 0 and beta > 0.

        """

        # alpha > 0, beta > 0, mean is alpha*beta, variance is alpha*beta**2

        # Warning: a few older sources define the gamma distribution in terms
        # of alpha > -1.0
        if alpha <= 0.0 or beta <= 0.0:
            raise ValueError, 'gammavariate: alpha and beta must be > 0.0'

        #random = self.random
        if alpha > 1.0:

            # Uses R.C.H. Cheng, "The generation of Gamma
            # variables with non-integral shape parameters",
            # Applied Statistics, (1977), 26, No. 1, p71-74

            ainv = math.sqrt(2.0 * alpha - 1.0)
            bbb = alpha - LOG4
            ccc = alpha + ainv

            while True:
                u1 = self.random()
                if not 1e-7 < u1 < .9999999:
                    continue
                u2 = 1.0 - self.random()
                v = math.log(u1/(1.0-u1))/ainv
                x = alpha*math.exp(v)
                z = u1*u1*u2
                r = bbb+ccc*v-x
                if r + SG_MAGICCONST - 4.5*z >= 0.0 or r >= math.log(z):
                    return x * beta

        elif alpha == 1.0:
            # expovariate(1)
            u = self.random()
            while u <= 1e-7:
                u = self.random()
            return -math.log(u) * beta

        else:   # alpha is between 0 and 1 (exclusive)

            # Uses ALGORITHM GS of Statistical Computing - Kennedy & Gentle

            while True:
                u = self.random()
                b = (math.e + alpha)/math.e
                p = b*u
                if p <= 1.0:
                    x = pow(p, 1.0/alpha)
                else:
                    # p > 1
                    x = -math.log((b-p)/alpha)
                u1 = self.random()
                if not (((p <= 1.0) and (u1 > math.exp(-x))) or
                          ((p > 1)  and  (u1 > pow(x, alpha - 1.0)))):
                    break
            return x * beta


    # Deprecated in CPython
    def stdgamma(self, alpha, ainv, bbb, ccc):
        return self.gammavariate(alpha, 1.0)



## -------------------- Gauss (faster alternative) --------------------

    def gauss(self, mu, sigma):
        """Gaussian distribution.

        mu is the mean, and sigma is the standard deviation.  This is
        slightly faster than the normalvariate() function.

        Not thread-safe without a lock around calls.

        """
        # When x and y are two variables from [0, 1), uniformly
        # distributed, then
        #
        #    cos(2*pi*x)*sqrt(-2*log(1-y))
        #    sin(2*pi*x)*sqrt(-2*log(1-y))
        #
        # are two *independent* variables with normal distribution
        # (mu = 0, sigma = 1).
        # (Lambert Meertens)
        # (corrected version; bug discovered by Mike Miller, fixed by LM)

        # (Shed Skin note: Does this apply for SS?)
        # Multithreading note: When two threads call this function
        # simultaneously, it is possible that they will receive the
        # same return value.  The window is very small though.  To
        # avoid this, you have to use a lock around all calls.  (I
        # didn't want to slow this down in the serial case by using a
        # lock here.)

        if self.gauss_switch == 1:
            z = self.gauss_next
            self.gauss_switch = 0
        else:
            x2pi = self.random() * 2*math.pi
            g2rad = math.sqrt(-2.0 * math.log(1.0 - self.random()))
            z = math.cos(x2pi) * g2rad
            self.gauss_next = math.sin(x2pi) * g2rad
            self.gauss_switch = 1

        return mu + z*sigma

## -------------------- beta --------------------

    def betavariate(self, alpha, beta):
        """Beta distribution.

        Conditions on the parameters are alpha > -1 and beta} > -1.
        Returned values range between 0 and 1.

        """
        # This version due to Janne Sinkkonen, and matches all the std
        # texts (e.g., Knuth Vol 2 Ed 3 pg 134 "the beta distribution").
        y = self.gammavariate(alpha, 1.)
        if y == 0:
            return 0.0
        else:
            return y / (y + self.gammavariate(beta, 1.))

## -------------------- Pareto --------------------

    def paretovariate(self, alpha):
        """Pareto distribution.  alpha is the shape parameter."""
        # Jain, pg. 495

        u = 1.0 - self.random()
        return 1.0 / pow(u, 1.0/alpha)

## -------------------- Weibull --------------------

    def weibullvariate(self, alpha, beta):
        """Weibull distribution.

        alpha is the scale parameter and beta is the shape parameter.

        """
        # Jain, pg. 499; bug fix courtesy Bill Arms

        u = 1.0 - self.random()
        return alpha * pow(-math.log(u), 1.0/beta)


# This method was added for compatibility with Python's random classes
## -------------------- bitwise methods  -------------------

    def getrandbits(self, k):
        """getrandbits(k) -> x.  Generates an int with k random bits."""
        if k <= 0:
            raise "number of bits must be greater than zero for getrandbits(k)"
        return (self.genrand_int32() >> (32-k)) & ~(-1 << k)


if __name__=='__main__':
    init = [0x123, 0x234, 0x345, 0x456]
    r = MersenneTwister()
    r.init_by_array(init)
    for i in range(10):
        print r.genrand_res53()

