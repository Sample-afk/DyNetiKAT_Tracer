


[![DOI](https://zenodo.org/badge/338371401.svg)](https://zenodo.org/badge/latestdoi/338371401)



## DyNetiKAT

This is a network verification tool based on the [DyNetKAT](https://arxiv.org/abs/2102.10035) language which provides a reasoning method on reachability and waypointing properties for dynamic networks. DyNetiKAT utilizes [Maude](https://www.sciencedirect.com/science/article/pii/S0304397501003590) rewriting system and [NetKAT](https://dl.acm.org/doi/10.1145/2578855.2535862) decision procedure in the background.

  
## Requirements
  
[Python (>= 3.7)](https://www.python.org/downloads/) including the package [NumPy](https://numpy.org/)

[Maude (>= 3.0)](http://maude.cs.illinois.edu/w/index.php/All_Maude_3_versions)

NetKAT tool ([netkat-idd](https://github.com/netkat-lang/netkat) or [netkat-automata](https://github.com/frenetic-lang/netkat-automata))



## HOW TO INSTALL (DyNetiKAT)
  #### Requirements
  - clean linux (virtual) machine

  #### Steps
  1. Clone this repositoryif it's not yet on your machine.
  2. Navigate to the root of the project (*`DyNetiKAT_contained/`* folder).
  3. Run the following command: `bash install.sh`
      > Note: this can take a while.
  4. if the result looks something like this: 

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
        > Note: dos2unix is a tool that changes files from windows encoding to unix encoding (in this case it will change unrecognized `\r` to something that unix system can understand).
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



## HOW TO INSTALL (Maude)
  If you intend to use only DyNetiKAT this section is irrelevant to you, since DyNEtiKAT has it's own Maude instalation, which is not easily available system-wide.

  However if you need to run MiTool, then Maude is required. There are 2 options how to get Maude working.

  ### Option 1 (Hard way): using DyNetiKAT instalation  

  As any programme, Maude has an entry point, namely `maude.linux64`, so to call Maude we need to call this executable. DyNetiKAT installes Maude in `DyNetiKAT_contained/maude-3.1/maude.linux64`. We need to create an alias for the instalation.

  #### Steps
  1. Go to root directory of the system: run `cd ~`
  2. Open `.bashrc` file with a text editor (here `nano` as example): run `nano ~/.bashrc` or `nano .bashrc`
  3. Add alias to the Maude executable using absolute path: add the following line to the end of `.bashrc` file  
      > Note: DO NOT forget to change path to the appropriate one
      ```sh 
        alias mde='/home/mom/DyNetiKAT_contained/maude-3.1/maude.linux64'
      ```
      where:
      - mde - alias name
      - mom - example user name
      > Note: In the example `DyNetiKAT_contained/` folder is located directly in the default user folder
  4. Save changes and close the file
  If you are using `nano`:
      1. press `Ctrl + o` to save
      2. press `Enter` to confirm saving
      3. press `Ctrl + x` to exit
  5. reload the `~/.bashrc` for the changes to take effect: run `source ~/.bashrc` (otherwise changes will take effect after a restart)

  ### Option 2 (Easier way): install Maude system-wide
  Simply run `sudo apt install maude`. Thats it, maude is installed system-wide.



## HOW TO RUN (MiTool (basicaly 'how to run maude' for now)) 
This tool is self contained, meaning the instalation of DyNetiKAT is not requred.  

The tool is also unfinished, so the instruction are to represent current features and calling procedure (last updated on __`31.05.2024`__).
  #### Requirements
  - clean linux (virtual) machine
  - Maude installed

  #### Steps
  1. Clone this repository if it's not yet on your machine.
  2. Navigate to the *`DyNetiKAT_containde/MiTool/`* directory
  3. Run maude by calling `maude` or your defined alias in the command prompt
      ```sh
        ~/DyNetiKAT_contained/MiTool$ maude
                      \||||||||||||||||||/
                    --- Welcome to Maude ---
                      /||||||||||||||||||\
              Maude 3.1
              Copyright 1997-2020 SRI International
                    Fri May 31 17:35:54 2024
        Maude>
      ```
  4. Load the appropriate `.maude` file (`new_model.maude` in this case)  
      First load
      ```sh
        Maude> load new_model.maude
        Maude>
      ```  
      Reload
      ```sh
        Maude> load new_model.maude
        Advisory: redefining module FIELD.
        Advisory: redefining module COMM.
        Advisory: redefining view Comm.
        Advisory: redefining module DNA.
        Advisory: redefining module RECURSIVE-DNA.
        Advisory: redefining module PROPERTY-CHECKING.
        Advisory: redefining module SIMPLER-MODEL.
        Maude>      
      ```
  5. Run `red pi{*num_of_unfolds*}(*programme/expression*)`
      ```sh
        Maude> red pi{1}(Switch || Controller) .
        reduce in SIMPLER-MODEL : pi{1}(Switch || Controller) .
        rewrites: 1514 in 0ms cpu (0ms real) (~ rewrites/second)
        result DNA: "(flag = b-SSH . 1)" ; bot o+ "(flag = b-TCP . 1)" ; bot o+ "(flag = regular) . (type = SSH) . (pt = 1) . (pt <- 2)" ; bot o+ "(flag = regular) . (type = TCP) . (pt = 1) . (pt <- 2)" ; bot o+ (Up ? "one") ; bot o+ (TCP ? "one") ; bot o+ (SSH ? "one") ; bot
        Maude>      
      ```
  6. To stop Maude press `Ctrl+Z`



## Usage

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
