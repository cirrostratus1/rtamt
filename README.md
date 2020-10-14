<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-generate-toc again -->
**Table of Contents**

- [About](#about)
- [Installation](#installation)
- [Theory](#theory)
- [Usage](#usage)
- [References](#references)

<!-- markdown-toc end -->

# About

RTAMT is a Python (2- and 3-compatible) library for online monitoring of bounded-future 
Signal Temporal Logic (STL). The library has an optional C++ back-end. 

# Installation

## Install prerequisites for RTAMT installation

```bash
sudo apt install libboost-all-dev
sudo apt install python-dev
sudo apt install python-pip
```

If your want to extend the specification language, you may need the ANTLR4 parser generator.

```bash
sudo apt install antlr4
```

You will also need CMake version 3.12 or higher if you need to build the CPP backend.

```bash
sudo apt install cmake
```

You can check manual intallation of cmake.  
https://anglehit.com/how-to-install-the-latest-version-of-cmake-via-command-line/

## Build the tool

### Clone the repository

```bash
git clone https://github.com/nickovic/rtamt
```

#### Build CPP libraries for Python 2 
This step is needed only if you want to use the CPP backend and
can be skipped if you want to use pure Python monitors.

```bash
cd rtamt/rtamt
mkdir build
cd build
cmake -DPythonVersion=2 ../
make
```

#### Install RTAMT for Python 2

```bash
cd rtamt/
sudo pip2 install .
```

#### build CPP libraries for Python 3 
This step is needed only if you want to use the CPP backend and
can be skipped if you want to use pure Python monitors.

```bash
cd rtamt/rtamt
mkdir build
cd build
cmake -DPythonVersion=3 ../
make
```

#### install RTAMT for Python 3

```bash
cd rtamt/
sudo pip3 install .
```

#### uninstall RTAMT (Python 2)

```bash
sudo pip2 uninstall rtamt
```

#### uninstall RTAMT (Python 3)

```bash
sudo pip3 uninstall rtamt
```

# Theory

RTAMT is a Python library for online monitoring of bounded-future 
Signal Temporal Logic (STL). The library is inspired by several theoretical and practical 
works:
- The bounded-future fragment of STL is inspired by [2]
- The interface-aware interpretation of STL quantitative semantics is inspired by [3]
- The periodic-sampling interpretation of specifications (even in presence of timestamps that are not prefectly periodic) is inpired by [4]
- The translation of bounded-future STL to "equirobust" past STL prior to the monitoring phase is inpired by [2] 

## Specification Language

RTAMT uses the bounded-future fragment of Signal Temporal Logic (STL) and interface-aware STL (IA-STL).

The library supports a variant of STL with past and future temporal operators as well as basic arithmetic and absolute value operators. 
Semantics of STL is defined in terms of a robustess degree `rho(phi,w,t)`, a function defined over reals extended with `+inf` and `-inf` that takes as input an STL specification `phi`, an input signal 
`w` and time index `t`, and computes how far is the signal `w` at time `t` from satisfying/violating `phi`. The robustness degree function is defined inductively as follows
(`c` is a real constant, `x` is a variable, `w_x(t)` denotes the value of `w` projected to `x` at time `t`, `a,b` are rational constants such that `0 <= a <= b` and `|w|` is the length of `w`):
```
% Constant
rho(c,w,t) = c

% Variable
rho(x,w,t) = w_x(t)

% Absolute value
rho(abs(phi),w,t) = |rho(phi,w,t)|

% Arithmetic operators
rho(phi + psi,w,t) = rho(phi,w,t) + rho(psi,w,t)
rho(phi - psi,w,t) = rho(phi,w,t) - rho(psi,w,t)
rho(phi * psi,w,t) = rho(phi,w,t) * rho(psi,w,t)
rho(phi / psi,w,t) = rho(phi,w,t) / rho(psi,w,t)

% Numeric predicates
rho(phi <= psi,w,t) = rho(psi,w,t) - rho(phi,w,t) 
rho(phi < psi,w,t) = rho(psi,w,t) - rho(phi,w,t)
rho(phi >= psi,w,t) = rho(phi,w,t) - rho(psi,w,t)
rho(phi >= psi,w,t) = rho(phi,w,t) - rho(psi,w,t)
rho(phi == psi,w,t) = -|rho(phi,w,t) - rho(psi,w,t)|
rho(phi !== psi,w,t) = |rho(phi,w,t) - rho(psi,w,t)|

% Boolean operators
rho(not(phi),w,t) = -rho(phi,w,t)
rho(phi or psi,w,t) = max(rho(phi,w,t),rho(psi,w,t))
rho(phi and psi,w,t) = min(rho(phi,w,t),rho(psi,w,t))
rho(phi -> psi,w,t) = max(-rho(phi,w,t),rho(psi,w,t))
rho(phi <-> psi,w,t) = -|rho(phi,w,t) - rho(psi,w,t)|
rho(phi xor psi,w,t) = |rho(phi,w,t) - rho(psi,w,t)|

% Events
rho(rise(phi),w,t) = rho(phi,w,t)                     if t=0
                     min(-rho(phi,w,t-1),rho(phi,w,t) otherwise
rho(fall(phi),w,t) = -rho(phi,w,t)                    if t=0
                     min(rho(phi,w,t-1),-rho(phi,w,t) otherwise

% Past untimed temporal operators
rho(once phi,w,t) = max_{t' in [0,t]} rho(phi,w,t')
rho(historically phi,w,t) = min_{t' in [0,t]} rho(phi,w,t')
rho(phi since psi,w,t) = max_{t' in [0,t]}(min(rho(psi,w,t'), min_{t'' in (t',t]}rho(psi,w,t') rho(phi,w,t'')))

% Past untimed temporal operators
rho(once[a,b] phi,w,t) = -inf                                                            if t-a < 0
                         max_{t' in ([0,t] intersect [t-a,t-b])} rho(phi,w,t')           otherwise
rho(historically[a,b] phi,w,t) = inf                                                     if t-a < 0
                                 min_{t' in ([0,t] intersect [t-a,t-b])} rho(phi,w,t')   otherwise
rho(phi since[a,b] psi,w,t) = -inf                                                       if t-a < 0 
                              max_{t' in ([0,t] intersect [t-a,t-b]} (min(rho(psi,w,t'), 
                              min_{t'' in (t',t]}rho(psi,w,t') rho(phi,w,t'')))          otherwise

% Future untimed temporal operators
rho(eventually phi,w,t) = max_{t' in [0,t]} rho(phi,w,t')
rho(always phi,w,t) = min_{t' in [0,t]} rho(phi,w,t')

% Future timed temporal operators
rho(eventually[a,b] phi,w,t) = -inf                                                     if t+a >= |w|
                               max_{t' in ([0,t] intersect [t+a,t+b])} rho(phi,w,t')    otherwise
rho(always[a,b] phi,w,t) = inf                                                          if t+a >= |w|
                           min_{t' in ([0,t] intersect [t+a,t+b])} rho(phi,w,t')        otherwise
rho(phi until[a,b] psi,w,t) = -inf                                                      if t+a >= |w|
                              max_{t' in ([0,t] intersect [t+a,t+b]}(min(rho(psi,w,t'), 
                              min_{t'' in [t,t')}rho(psi,w,t') rho(phi,w,t'')))         otherwise   
```

We define the robustness degree `rho(phi,w)` as `rho(phi,w,0)`.

There are several important points to note about the above syntax and semantics:
- The library allows only bounded-future STL specifications, meaning that _unbounded_ future operators `always` and `eventually` can appear only at the top level of the specification. For example, `always(x<=2)` is a bounded-future STL specification, while `always(eventually(x<=2))` is not.
- The library does not allow _unbounded_ `until` operator.
- The library uses _non-standard_ semantics for unbounded `always` and `eventually` operators. For instance, standard TL semantics says that `always phi` holds at time `t` iff `phi` holds at all future times `t'>=t`. This interpretation cannot be monitored in online fashion. We define semantics that says that `always phi` holds at time `t` iff `phi` has been continuously holding so far. Note that this interpretation of `always` is equivalent to the `historically`operator. The situation is symmetric for the non-standard semantics of  `eventually` and `once`.

We can see from the semantics of bounded-future STL that the direct evaluation of a formula `phi` at time `t` may depend on inputs at `t'>t` that have not arrived yet.
The library monitors bounded-future STL formulas with a fixed _delay_. In order to compute `rho(phi,w,t)`, the monitor waits for all inputs required to evaluate `phi` to become available before computing the robustness degree. This delay is fixed and depends on the specification. For instance, the specification `always((req >= 3) -> eventually[0:2]always[0:3](gnt >= 3)`is evaluated with delay `5` - the time needed to capture all inputs required for evaluating bounded `eventually` and `always` operators. We refer the reader to [2] for algorithmic details regarding monitoring with delay.

# Usage

## Working with time units and timing assumptions

The default unit in RTAMT is seconds, and the default expected period between 
two consecutive input samples is `1s` with `10%` tolerance. 
The following program uses these default values to implicitely set up the monitor. 
The specification intuitively states that whenever the `req` is above `3`, 
eventually within `5s` `gnt` also goes above `3`. 
The user feeds the monitor with values timestamped _exactly_ `1s` apart 
from each other. It follows that the periodic sampling assumption holds.

RTAMT counts how many times the periodic sampling assumption has been violated 
up to the moment of being invoked via the `sampling_violation_counter` member. 
In this example, this violation obviously occurs `0` times.

```
import sys
import rtamt

def monitor():
    spec = rtamt.STLSpecification()
    spec.name = 'Bounded-response Request-Grant'

    spec.declare_var('req', 'float')
    spec.declare_var('gnt', 'float')
    spec.declare_var('out', 'float')

    spec.spec = 'out = always((req>=3) implies (eventually[0:5](gnt>=3)))'

    try:
        spec.parse()
        spec.update(0, [('req', 0.1), ('gnt', 0.3)])
        spec.update(1, [('req', 0.45), ('gnt', 0.12)])
        spec.update(2, [('req', 0.78), ('gnt', 0.18)])
        nb_violations = spec.sampling_violation_counter // nb_violations = 0
    except rtamt.STLParseException as err:
        print('STL Parse Exception: {}'.format(err))
        sys.exit()

if __name__ == '__main__':
    # Process arguments
    monitor()
}
```
The same program, but with slightly different timestamps still reports `0` number of periodic sampling assumption violations. This is because the difference between all consecuting sampling timestamps remains within the (implicitely) specified `10%` tolerance.


```
    ...
    out = spec.update(0, {In("req", 0.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(1.01, {In("req", 0.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(1.98, {In("req", 0.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(3.03, {In("req", 6.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(4.01, {In("req", 6.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(4.99, {In("req", 0.0), In("gnt", 0.0)}); // out = 3
    out = spec.update(6.01, {In("req", 0.0), In("gnt", 0.0)}); // out = 3
    
    double nb_violations = spec.sampling_violation_counter(); // nb_violations = 0
```
On the other hand, the following sequence of inputs results in `1` reported violation of periodic sampling assumption. This is because the second input is `1.11s` away from the first sample, which is `11%` above the assumed `1s` period. 

```
    ...
    out = spec.update(0, {In("req", 0.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(1.11, {In("req", 0.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(2.08, {In("req", 0.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(3.03, {In("req", 6.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(4.01, {In("req", 6.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(4.99, {In("req", 0.0), In("gnt", 0.0)}); // out = 3
    out = spec.update(6.01, {In("req", 0.0), In("gnt", 0.0)}); // out = 3
    
    double nb_violations = spec.sampling_violation_counter(); // nb_violations = 1
```
This same sequence of inputs results in `0` reported violation of periodic sampling assumption if we explicitely set the sampling period tolerance value to `20%`. 

```
    ...
    spec.sampling_period(1, Unit::S, 0.2);
    ...
    out = spec.update(0, {In("req", 0.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(1.11, {In("req", 0.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(2.08, {In("req", 0.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(3.03, {In("req", 6.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(4.01, {In("req", 6.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(4.99, {In("req", 0.0), In("gnt", 0.0)}); // out = 3
    out = spec.update(6.01, {In("req", 0.0), In("gnt", 0.0)}); // out = 3
    
    double nb_violations = spec.sampling_violation_counter(); // nb_violations = 1
```

The user can also explicitely set the default unit, as well as the expected period and tolerance. In that case, the user must ensure that the timing bounds declared in the specification are divisible by the sampling period. The following specification is correct, since the sampling period is set to `500ms`, the default unit is set to seconds, and the specification implicitely defines the bound from `0.5s = 500ms` and `1.5s = 1500ms`, i.e. between `1` amd `3` sampling periods. 

```
#include <rtamt/stl_specification.hpp>
#include <rtamt/stl_exception.hpp>

using namespace std;
using namespace rtamt;
using In = Input;

int main(int argc, char **argv) {
    StlSpecification spec;

    spec.name("Bounded-response Request-Grant");
    
    spec.declare_var("req", Type::FLOAT);
    spec.declare_var("gnt", Type::FLOAT);
    spec.declare_var("out", Type::FLOAT);
    
    spec.var_io_type("req", StlIOType::IN);
    spec.var_io_type("gnt", StlIOType::OUT);
    
    spec.default_unit(Unit::S);
    spec.sampling_period(500, Unit::MS, 0.1);
    
    spec.semantics(StlSemantics::STANDARD);
    
    spec.spec("out = (req >= 3) -> (eventually[0.5:1.5](gnt >= 3))");
    
    spec.parse();
    
    double out;
    
    out = spec.update(0, {In("req", 0.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(0.5, {In("req", 0.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(1, {In("req", 0.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(1.5, {In("req", 6.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(2, {In("req", 6.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(2.5, {In("req", 0.0), In("gnt", 0.0)}); // out = 3
    out = spec.update(3, {In("req", 0.0), In("gnt", 0.0)}); // out = 3

    double nb_violations = spec.sampling_violation_counter(); // nb_violations = 0
}
```
The following defines the same program, but now with `ms` as the default unit. 

```
    ...
    spec.default_unit(Unit::MS);
    spec.sampling_period(500, Unit::MS, 0.1);
    ...
    spec.spec("out = (req >= 3) -> (eventually[500:1500](gnt >= 3))");
    
    spec.parse();
    
    double out;
    
    out = spec.update(0, {In("req", 0.0), In("gnt", 0.0)}); // out = inf
    out = spec.update(500, {In("req", 0.0), In("gnt", 0.0)}); // out = inf

    double nb_violations = spec.sampling_violation_counter(); // nb_violations = 0
}
```

The following program throws an exception - the temporal bound is defined between `500ms` and `1500ms`, while the sampling period equals to `1s = 1000ms`. 

```
    ...
    spec.default_unit(Unit::MS);
    spec.sampling_period(1, Unit::S, 0.1);
    ...
    spec.spec("out = (req >= 3) -> (eventually[500:1500](gnt >= 3))");
    ...
    spec.parse();
    ...
    
}
```

Finally, the following program is correct, because the temporal bound is explicitely defined between `500s` and `1500s`, while the sampling period equals to `1s`. 

```
    ...
    spec.default_unit(Unit::MS);
    spec.sampling_period(1, Unit::S, 0.1);
    ...
    spec.spec("out = (req >= 3) -> (eventually[500s:1500s](gnt >= 3))");
    ...
    spec.parse();
    ...
    
}
```



## Run examples

### online-STL example

```bash
cd rtamt/examples/basic
$ python monitor_basic.py
time=0 rob=122.0
time=1 rob=3.0
time=2 rob=-10.0
```

### offline-STL example

```bash
cd rtamt/examples/basic
$ python monitor_offline.py
Robustness: -98.0
```

### Io-STL example

```bash
cd rtamt/examples/offline_monitors
$ python offline_monitor_dt.py
Example (a) - standard robustness: 3.0
Example (a) - output robustness: 3.0
Example (a) - input vacuity: 0
Example (b) - standard robustness: 1.0
Example (b) - output robustness: inf
Example (b) - input vacuity: 1.0
Example (c) - standard robustness: -2.0
Example (c) - output robustness: -2.0
Example (c) - input vacuity: 0
Example (d) - standard robustness: -1.0
Example (d) - output robustness: -2.0
Example (d) - input vacuity: 0
```

# References

- [1] Dejan Nickovic, Tomoya Yamaguchi: RTAMT: Online Robustness Monitors from STL. CoRR abs/2005.11827 (2020)
- [2] Stefan Jaksic, Ezio Bartocci, Radu Grosu, Reinhard Kloibhofer, Thang Nguyen, Dejan Nickovic: From signal temporal logic to FPGA monitors. MEMOCODE 2015: 218-227
- [3] Thomas Ferrère, Dejan Nickovic, Alexandre Donzé, Hisahiro Ito, James Kapinski: Interface-aware signal temporal logic. HSCC 2019: 57-66
- [4] Thomas A. Henzinger, Zohar Manna, Amir Pnueli: What Good Are Digital Clocks? ICALP 1992: 545-558