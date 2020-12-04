# NetCracker

![](static/netcracker_logo.png)

NetCracker is an FPGA architecture analysis tool for facilitating the
investigation of connectivity patterns within as well as in between switchboxes.
NetCracker has been used to generate the information which served as the basis
for the conclusions drawn in [insert reference to NetCracker paper]. We
therefore recommend familiarizing oneself with this work before exploring NetCracker.

NetCracker relies on switchboxes being described in a `.json`-based file format.
The format describes a directed graph with interconnect points as vertices and
their forward and backward connections as edges, alongside information about the
location of interconnect points in the device. This format is vendor-independent
and thus any interconnect structure adhering to the format may be analysed
through NetCracker.

NetCracker organizes its analysis as a set of passes which execute on one or
more switchboxes. Each pass may produce a set of artifacts (plots, statistics,
etc.) to facilitate further qualitative analysis by the user, or to enable the
execution of other passes. Having each pass being able to produce and consume
the results of other passes allows passes to be organized in a dependency graph.
Given an analysis request, specified by the user through a command-line
interface, NetCracker schedules the required set of passes to fulfill the
requested analysis. The intent of the architecture is to facilitate quick
implementations of new analysis passes as well as allowing each pass to be as
atomic as possible.

- [NetCracker](#netcracker)
  - [Requirements](#requirements)
  - [Usage](#usage)
    - [Example architecture](#example-architecture)
    - [Example 1: Adjacency analysis (internal)](#example-1-adjacency-analysis-internal)
    - [Example 2: Switchbox diversity](#example-2-switchbox-diversity)
  - [File format](#file-format)
  - [Adding a new analysis pass](#adding-a-new-analysis-pass)
    - [Step 1: Define the pass interface](#step-1-define-the-pass-interface)
    - [Step 2: Define the pass execution function](#step-2-define-the-pass-execution-function)
    - [Step 3: Register the pass](#step-3-register-the-pass)

## Requirements

NetCracker should be executed with `python3` and depends on the packages specified in `requirements.txt`.  
Run
> \> pip3 install -r requirements.txt

to ensure that all requirements are met.

## Usage

To execute NetCracker, simply call `python3 netcracker.py [args...]`.
Given the number of different passes provided with NetCracker, refer to
`python3 netcracker.py -h` for an overview over the provided passes.

To enable vendor-specific analysis passes, the vendor name must be added to the
command line. As of now, only `x7s` is a valid vendor to provide. If no
vendor, provide the string `none` instead.

All logs as well as pass artifacts for a given execution of NetCracker will be
placed in the `output/${time of execution}` folder.

### Example architecture

| <img src="https://raw.githubusercontent.com/mortbopet/NetCracker/main/static/exarch_names.svg"/>|<img src="https://raw.githubusercontent.com/mortbopet/NetCracker/main/static/exarch_long.svg"/> | <img src="https://raw.githubusercontent.com/mortbopet/NetCracker/main/static/exarch_short.svg"/> |
|:-:|:-:|:-:|  
| PIP junction names | Internal connections (long ins) | Internal connections (short ins) |

In `examples/sb_example.json` we provide an example NetCracker file which
describes a small, made-up switchbox architecture. This example is illustrated in the figures above.

### Example 1: Adjacency analysis (internal)

To run an adjacency analysis investigating the feedback connections of a CLB,
run:

```sh
> python3 netcracker.py -f examples/sb_example.json -x7sALLoc x7s
```

This will produce a file `adjacency_analysis_x7sALLoc.txt` in the output directory
of the `SB_X10Y10` switchbox.
directory. This file contains a matrix detailing the connections between ins-
and outputs towards a CLB. This file may be further manipulated or plotted - we
recommend using the online tool
[Morpheus](https://software.broadinstitute.org/morpheus/) which facilitates easy
matrix exploration, clustering etc..

To view which PIP junctions are included under each clustering group of an
adjacency analysis result, refer to the `Group contents` sections within the
`log.txt` file contained in the output directory of a given analysis run.

### Example 2: Switchbox diversity

If a NetCracker file is provided which contains multiple switchboxes spread out
over a given area (specified by each switchbox' `x` and `y` coordinates), NetCracker
may analyse the distribution of unique switchboxes across the device.

```sh
> python3 netcracker.py -f ${netcracker file} -x7sGNL -sbdiversity x7s
```

1. `-f ${netcracker file}` specifies the netcracker file
   which we wish to analyse.
2. `-x7sGNL` specifies the adjacency analysis to run. The switchbox comparison is
   dependent on the results of an adjacency analysis pass. Many different
   adjacency analyses are available (see `vendor/Xilinx/S7/`).
3. `-sbdiversity` enables the switchbox comparison pass.
4. `x7s` allows the execution of Xilinx 7-series specific passes.

Upon finished execution, a plot is shown of the device with switchboxes
represented as pixels. Each unique pixel color represents a unique switchbox
type, based on the switchbox' adjacency analysis result.

## File format

NetCracker files are `json` key-value files which realize a directed graph with vertices being PIP junctions and edges being PIPs. For each PIP junction, a list of connected (forward or backward) PIP junctions shall be specified. It is then these connections which are interpreted as the PIPs of the switchbox.

The `options` field is an arbitrary field which allows for embedding additional information into a NetCracker file, allowing additional vendor-specific analysis.

A PIP Junction may have an empty `forward_pjs` list. A PIP Junction may not have an empty `backward_pjs` list - in other words, a PIP Junction must be driven.

Following is a (simplified) grammar for the NetCracker file format. Whitespace, newline etc. have been left out for brevity due to being a `json` based file format.

```txt
<NetCracker file> ::= "{" <switchboxes> "}"
<switchboxes>     ::= <switchbox> | {"," <switchbox>}
<switchbox>       ::= <switchbox name> ": {" <switchbox_internals> "}"
<switchbox_internals> ::=
   ""x" :" <integer> ","
   ""y" :" <integer> ","
   ""pip_junctions" : "[" <pip_junctions> "]" | "," <options>

<pip_junctions> ::= <pip_junction> {"," <pip_junction>}

<pip_junction> ::=
   "{"
      ""forward_pjs": ["  <pip_junction_references> "],"
      ""backward_pjs": [" <pip_junction_references> "]"
   "}"

<pip_junction_references>  ::= <pip_junction_reference> {"," <pip_junction_reference>}
<pip_junction_reference>   ::=
   "{"
      ""name" :"  <switchbox name> ","
      ""x" :"     <integer> ","
      ""y" :"     <integer>
   "}"

<switchbox name> ::= <string>
<options>        ::= (any JSON key-value structure contained within {} brackets)
```

As an example file, please refer to `examples/sb_example.json`.

## Adding a new analysis pass

As a reference analysis pass, see see `src/analysis/fanIOAnalysis.py`.

### Step 1: Define the pass interface

Referencing the FanIOAnalysis class, we have the following:

```python
class FanIOAnalysis(AnalysisPass):
    def __init__(self):
        super().__init__(
            description="Determine Fan-in/Fan-out for the PIP junctions of a switchbox",
            key="fanio",
            depends=[INOUT_ANALYSIS_RES],
            produces=[]
        )
   ...
```

`FanIOAnalysis` inherits `AnalysisPass` which is the base class for all analysis
passes. Constructor arguments are as follows:
- `name`: Name of the pass, mainly shown in debug output.
- `key`: The key which triggers the pass in the command-line interface. Hence, running NetCracker with `-F` will enable the pass.
- `depends`: A list of strings which are identifiers for results produced by other passes. If an analysis pass depends on a result which is produced by another pass but this pass is not enabled, the given producing pass will be implicitly enabled. If an analysis pass has a dependency which cannot be resolved (ie. there is no registerred pass which produces the given result), execution will fail.
- `produces`: Similarly to `depends`, produces is a list of strings which are identifiers for results produced by this pass.


### Step 2: Define the pass execution function

Next, a pass must define a `run` function. The function will be executed whenever all dependencies of the pass have been resolved.
Depending on whether `executesOnAllSBs` was set during construction, the pass will be called with either a single or multiple switchboxes as an argument.

Within the pass, one may retrieve results from other depending passes as follows:

```python
inout_res = sb.getAnalysisResult(INOUT_ANALYSIS_RES)
```

And from there use the depending pass results alongside values generally available in the Switchbox class, to perform the desired analysis.

The given pass produces no values. However, if this was the case, the pass could be extended as follows, to register a produced value:

```python
FAN_IO_RES = "Fan IO analysis result"

# in constructor
produces=[FAN_IO_RES]

# in run(self, sb)
sb.results[FAN_IO_RES] = ...
```

### Step 3: Register the pass

Finally, the pass must be registered within NetCracker. If the pass is not vendor-specific, navigate to the bottom of `passmanager.py` and construct the pass, similarly to the remainder of passes present in the file:

```python
from analysis.fanIOAnalysis import *
FanIOAnalysis() # Registers pass through construction
```

If the pass is vendor specific, navigate to the given vendor, and register the pass in the vendor objects constructor (see `Xilinx7SeriesVendor::__init__` in `src/vendor/Xilinx/S7/x7.py`).
