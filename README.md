## DyNetiKAT with race condition tracing

This is a fork of [DyNetiKAT_with_race_tracing](https://github.com/EZUTwente/DyNetiKAT_with_race_tracing). The reason for forking is to save the work as it was during initial submition and this is the updated/cleaned version.

`THE REST IS THIS SECTION IS UNCHAGED FROM THE FORK`

This is a fork of [DyNetiKAT](https://github.com/hcantunc/DyNetiKAT) with race condition tracer extension .

This is a network verification tool based on the [DyNetKAT](https://arxiv.org/abs/2102.10035) language which provides a reasoning method on reachability and waypointing properties for dynamic networks. DyNetiKAT utilizes [Maude](https://www.sciencedirect.com/science/article/pii/S0304397501003590) rewriting system and [NetKAT](https://dl.acm.org/doi/10.1145/2578855.2535862) decision procedure in the background.

  
## Requirements
  
A linux enviroment with [Python (>= 3.10.12)](https://www.python.org/downloads/)



## HOW TO INSTALL (DyNetiKAT with Tracer)
  #### Requirements
  - linux (virtual) machine

  #### Steps
  1. Clone this repository if it's not yet on your machine.
  2. Navigate to the root of the project (*`DyNetiKAT_contained/`* folder).
  3. Run the following command: `bash install.sh`
      > Note: this can take a while.
  4. if the result looks something like this (if not skip this step): 

      ```sh
        HTTP request sent, awaiting response... 404 Not Found
        2024-05-31 16:44:42 ERROR 404: Not Found.

        .ZIP.or Maude-3.1-linux.zip Maude-3.1-linux.zip
        rm: cannot remove 'Maude-3.1-linux.zip'$'\r': No such file or directory
        tst.sh: line 22: cd: $'maude-3.1\r': No such file or directory
        chmod: cannot access 'maude.linux64'$ '\r': No such file or directory
      ```

      - please run the following commands:
        - `sudo apt install dos2unix` 
        - `dos2unix install.sh`
        > Note: dos2unix is a tool that changes files from windows encoding to unix encoding (in this case it will change unrecognized `\r` to something that a unix based system can understand).
      - and run the `bash install.sh` again.
  5. to check instalation run `bash run_test.sh`, you should get the following output:
  
      ```sh
        ~/DyNetiKAT_contained$ bash run_test.sh
        Packet: int_to_ext - property: #0: property satisfied.
        Packet: int_to_ext - property: #1: property satisfied.
        Packet: ext_to_int - property: #0: property satisfied.
        Packet: ext_to_int - property: #1: property satisfied.
      ```
      > Note: `run_test.sh` might have similar issue to `install.sh`, fix is also similar - run `dos2unix run_test.sh`



## Usage (Tracer)

    python tracer_runner.py <path_to_maude> <path_to_model_in_maude>

    Options:
      -h, --help            show this help message and exit
      -f LOG_FILENAME, --log_filename=LOG_FILENAME
                            custom text output filename, default:
                            RUN_TRACER_OUT.txt
      -u UNFOLD_DEPTH, --unfold_depth=UNFOLD_DEPTH
                            unfold depth for DNKs 'pi{*depth*}(*program*)',
                            default: 4
      -c, --colorful        print output with color
      -t, --tracing_steps   print tracing steps
      -g GRAPHS, --graph_types=GRAPHS
                            choose types of traces returned 'full' or 'race' if
                            ommited, do both


## HOW TO RUN (Tracer) 
  The repository contains a `run_tracer.sh` file. Simply run the command `bash run_tracer.sh` to execute `tracer_runner.py` with the folowing parameters:
  - `./maude-3.1/maude.linux64` - path to maude instalation (from running `install.sh`) 
  - `./TracerTool/models/dev_model.maude` - path to running model 
  - `-c` - output text with ANSI colors
  - `-t` - show tracing steps

  Outputs (copy of console output and graphs) can be found in the `TracerTool_output/` directory.
  
  > Note that `run_tracer.sh` misgh have issues similar to `install.sh`, refer to the note at the end of `HOW TO INSTALL` section.

## Tracer structure
  TracerTool consists of several layers (from top to bottom):
  
  | Layer | Class name   | Most recent version (filename)  |  Description |
  |:-----:|:------------:|:-------------------------------:|:-------------|
  |    2   | TracerRunner | *tracer_runner_v1.py*           | Prepares and feeds necessary data to the TracerTool to showase an example. |
  |    1   | TracerTool   | *tracer_v2_SEQ.py*              | The tracer tool itself, traces execution branches, detects potential race conditions, and returns traces (can do both full and race traces chosen on class creation). Also returns a visual representation (problematic with large amount of nodes).|
  |    1.1   | Node | *tracer_v2_SEQ.py* | A subclass of TracerTool. Represents the sate of the network in the form of a collection of `Component` classes. Used for keeping track of the network program. (Node in the graph representation) |
  |    1.2   | Step | *tracer_v2_SEQ.py* | A subclass of TracerTool. Represents a recording of component action (packet manipulation or communication between data and control planes). Used for trace reconstruction. (Edge in the graph representation) |
  |    0   | Component | *component_v1.py* | A representation of switcch/controller. Keeps track of personal clock, simulates network rule execution. (Information within the node from in the graph) |

## Folders
  TracerTool contains two folders deprecated and prototype. Deprecated contains old versions of several classes. While the prototype contains attemts at parralelization and object based expressions (instead of current string based).

## Models
  The directory `models` contains 3 models:

  | Filename | Model |
  | :-: | :-|
  | dev_model.maude | Model of running example for DyNetKAT Tracer paper.|
  | dev_model1.maude | Stateful firewall. |
  | dev_model2.maude | Simplified version of the running exmaple. |

## Possible improvements/weakpoints
  - `Performance` - parallelize current algorithm (in my opinion requres changes to the datamodel). It is possible that for better results a faster language like c might be requreid (python should be fine for interfacing).
  - `Datamodel` - current model is a tree structure where nodes relate to each other via storing a node within a node. This poses concurrent challanges as the object can not be shared, and so the resulting tree structure wil be most likely broken. Additionally, more clever/efficient data structures can also impact the performance positively.
  - `Text output (specifically intermediate outputs)` - for better performance intermediate text outputs might be removed. This will, however, increase the debugging difficulty.
  - `Graph representation` - current implementation struggles with large amount of nodes (readability issue).
  - `Make the tool use existing ligraries` - namely `maude_parser` and `util` from the `TracerTool/src` directory.
  - `Consider different model approach` - considering each switch as a separate component is computationaly expensive, so it might be worth to aggregate all switches into a one large switch. Additionaly if more that one switch had taken an action, any communication with the controller by any switch will lead to a race condition (see `TracerTool/Race_traces_running_ex_1c_2sw(54 min)` directory)

# From original DyNetiKAT

## Usage (From original DyNetiKAT)

    python dnk.py <path_to_maude> <path_to_netkat_tool> <input_file>

    Options:
      -h, --help            show this help message and exit
      -t NUM_THREADS, --threads=NUM_THREADS
                            number of threads (Default: the number of available cores in the system)
      -p, --preprocessed    pass this option if the given input file is already preprocessed
      -v NETKAT_VERSION, --netkat-version=NETKAT_VERSION
                            the version of the netkat tool: netkat-idd or netkat-automata (Default: netkat-idd)
      -s --time-stats       reports the timing information.
                      
For `netkat-idd` tool, the path should be as follows: `path_to_netkat_idd_build_dir/install/default/bin/katbv`. <br>
For `netkat-automata` tool, the path should be as follows: `path_to_netkat_automata_build_dir/src/Decide_Repl.native`.

# From this point onward the readme is unchanged from original DyNetiKAT repository

## Encoding

In the following we describe how the operators of NetKAT and DyNetKAT can be represented in in the tool. DyNetKAT operators are encoded as follows:   
 - The dummy policy<img src="https://render.githubusercontent.com/render/math?math=\bot">is encoded as `bot`
 - The sequential composition operator is encoded as `arg1 ; arg2`. Here, `arg1` can either be a NetKAT policy or a communication term and `arg2` is always required to be a DyNetKAT term.
 -  The communication terms sending <img src="https://render.githubusercontent.com/render/math?math=arg1 ! arg2"> and receiving <img src="https://render.githubusercontent.com/render/math?math=arg1 ? arg2"> are encoded as `arg1 ! arg2` and `arg1 ? arg2`. Here, `arg1` is a channel name and `arg2` is a NetKAT policy.
 - The parallel composition of DyNetKAT policies <img src="https://render.githubusercontent.com/render/math?math=arg1 \parallel arg2"> is encoded as `arg1 || arg2`.  
 - Non-deterministic choice of DyNetKAT policies <img src="https://render.githubusercontent.com/render/math?math=arg1 \oplus arg2"> is encoded as `arg1 o+ arg2`
 - The constant <img src="https://render.githubusercontent.com/render/math?math=\mathbf{rcfg}_{arg1, arg2}"> which pinpoints a communication step is encoded as `rcfg(arg1, arg2)`. Here, `arg1` is a channel name and `arg2` is a NetKAT policy.
 - Recursive variables are explicitly defined in the file that is given as input to the tool. 

<br />

The NetKAT operators are encoded as follows:  
 - The predicate <img src="https://render.githubusercontent.com/render/math?math=0"> for dropping a packet is encoded as `zero`
 - The predicate <img src="https://render.githubusercontent.com/render/math?math=1"> which passes on a packet without any modification is encoded as `one` 
 - The predicate <img src="https://render.githubusercontent.com/render/math?math=arg1=arg2"> which checks if the field `arg1` of a packet has the value `arg2` is encoded as `arg1 = arg2`
 - The negation operator<img src="https://render.githubusercontent.com/render/math?math=\neg arg1"> is encoded as `~ arg1`
 - The modification operator <img src="https://render.githubusercontent.com/render/math?math=arg1 \leftarrow arg2"> which assigns the value `arg2` into the field `arg1` in the current packet is encoded as `arg1 <- arg2`
- The union (and disjunction) operator <img src="https://render.githubusercontent.com/render/math?math=arg1"> + <img src="https://render.githubusercontent.com/render/math?math=arg2"> is encoded as `arg1 + arg2`
- The sequential composition (and conjunction) operator <img src="https://render.githubusercontent.com/render/math?math=arg1 \cdot arg2"> is encoded as `arg1 . arg2`
-  The iteration operator <img src="https://render.githubusercontent.com/render/math?math=arg1^*"> is encoded as `arg1 *` 

## Properties

Two types of properties can be checked with DyNetiKAT: reachability and waypointing. Our procedure for checking such properties builds upon the methods introduced in NetKAT for checking reachability and waypointing properties. In NetKAT, these properties are defined with respect to an ingress point <img src="https://render.githubusercontent.com/render/math?math=in">,  an egress point  <img src="https://render.githubusercontent.com/render/math?math=out">, a  switch  policy  <img src="https://render.githubusercontent.com/render/math?math=p"> , a topology  <img src="https://render.githubusercontent.com/render/math?math=t"> and, a waypoint <img src="https://render.githubusercontent.com/render/math?math=w"> for waypointing properties.  The following NetKAT  equivalences characterize reachability and waypointing properties:  

 1. <img src="https://render.githubusercontent.com/render/math?math=in \cdot (p \cdot t)^* \cdot out \nequiv 0"> 
 2. <img src="https://render.githubusercontent.com/render/math?math=in \cdot (p \cdot t)^* \cdot out \equiv 0"> 
 3. <img src="https://render.githubusercontent.com/render/math?math=in \cdot (p \cdot t)^* \cdot out"> + <img src="https://render.githubusercontent.com/render/math?math=in \cdot (\neg out \cdot p \cdot t)^* \cdot w \cdot (\neg in \cdot p \cdot t)^* \cdot out \notag \equiv in \cdot (\neg out \cdot p \cdot t)^* \cdot w \cdot (\neg in \cdot p \cdot t)^* \cdot out"> 

If the equivalence in (1) holds then this implies that the egress point is reachable from the ingress point. Analogously, if the equivalence in (2) holds then this implies that the egress point is not reachable from the ingress point.  If the equivalence in (3) holds then this implies that all the packets from the ingress point to the egress point travel through the waypoint. DyNetKAT provides a mechanism that enables checking such properties in a dynamic setting. This entails utilizing the operators `head(D)` and `tail(D, R)` where `D` is a DyNetKAT term and `R` is a set of terms of shape `rcfg(X, N).` Intuitively, the operator  `head(D)` returns a NetKAT policy which represents the current configuration in the input `D`.  The operator `tail(D, R)` returns  a  DyNetKAT  policy  which is the sum of DyNetKAT policies inside `D` that appear after the synchronization events in  `R`.  Please see [here](https://arxiv.org/abs/2102.10035) for more details on the `head` and `tail` operators. 

For a given DyNetKAT term `D` we first apply our equational reasoning framework to unfold the expression and rewrite it into the normal form. This is achieved by utilizing the projection operator <img src="https://render.githubusercontent.com/render/math?math=\pi_n(-)">. Note that the number of unfoldings (i.e. the value `n` inside the projection operator) is a fixed value specified by the user. We then apply the restriction operator <img src="https://render.githubusercontent.com/render/math?math=\delta_H(-)"> on the resulting expression and eliminate the terms of shape `X!Z` and `X?Z`. That is, we compute the term <img src="https://render.githubusercontent.com/render/math?math=\delta_H(\pi_n(D))"> where H is the set of all terms of shape `X!Z` and `X?Z` that appear in `D`. Then, we extract the desired configurations by using the head and tail operators. After this step, the resulting expression is a purely NetKAT term  and  we  utilize  the  NetKAT  decision  procedure  for  checking  the  desired properties.

In our tool a property is defined as a 4-tuple containing the following elements:

 1. The first element describes the type of property and can be either `r` or `w` where `r` denotes a reachability property and `w` denotes a waypointing property.
 2. The second element is the property itself. The constructs that can be used to define a property are as follows: `head(@Program)`, `tail(@Program, R)`. Here, `@Program` is a special construct that refers to DyNetKAT program that is given as input, and `R` is a set containing elements of shape `rcfg(X,N)`. 
 3.  For reachability properties, the third element can be either `!0` or `=0` where `!0` denotes that the associated egress point should be reachable from the associated ingress point, whereas `=0` denotes that the associated egress should be unreachable from the associated ingress point. For waypointing properties, the third element is a predicate which denotes the waypoint.
 4. The fourth element denotes the maximum number of unfoldings to perform in the projection operator.
 
For an example, `(r, head(@Program), !0, 100)` encodes a reachability property and `(w, head(@Program), sw = 1, 100)` encodes a waypointing property. Furthermore, every property is associated with an ingress point and an egress point. 


## Input format

The input to DyNetiKAT is a .json file which contains the following data:

* in_packets: A dictionary with predicates describing the ingress points, e.g.:

`{"first_packet": "sw = 1 . pt = 1", "second_packet": "sw = 2 . pt = 2"}`

Note that every element in this dictionary must have a corresponding element in *out_packets* with the same key.

* out_packets: A dictionary with predicates describing the egress points, e.g.:

`{"first_packet": "sw = 2 . pt = 2", "second_packet": "sw = 1 . pt = 1"}`

As aforementioned, every element in this dictionary must have a corresponding element in *in_packets* with the same key.

* recursive_variables: Names and definitions of recursive variables that appear in the program, e.g.:

`{"Switch": "\"(pt = 1 . pt <- 2)\" ; Switch o+ (secConReq ? \"one\") ; SwitchPrime"}`

Note that the NetKAT terms inside the definitions must be enclosed with double quotes.

* channels: A list containing the names of the channels that appear in the program.

* program: The program to execute.

* module_name: The name of the program. The output files will be based on this name.

* properties: A dictionary which contains a list of properties. All the properties are associated with an ingress and egress point from the *in_packets* and *out_packets*. For example, consider the following encoding: 
   
   `{ "first_packet": [["r", 
                "head(@Program)", 
                "!0", 
                100], 
            ["w", 
                "head(@Program)", 
                "sw = 1", 
                100]], "second_packet": [[
                "r", 
                "head(@Program)",  
                "!0", 
                100]] 
    }`
    
  The above encoding defines a reachability property and a waypointing property for the `first_packet` and a reachability   property for the`second_packet`.     

Sample input files can be found under the folder `benchmarks`.


## FatTree Benchmarks

The FatTree topologies and the associated properties that are described [here](https://arxiv.org/abs/2102.10035) (Section 5) can be generated using the script `fattree.py` under the folder `benchmarks`. This script requires Python 3 and the package [NetworkX](https://networkx.org/).



## Known Issues

We observed that in certain cases the `netkat-idd` tool raises the following error: `(Invalid_argument "union: not right-associative!")`. You may want to use the `netkat-automata` tool in these cases.
