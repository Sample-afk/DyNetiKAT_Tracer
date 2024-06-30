## Graph explanation
- `green` - start node
- `yellow` - reconfiguretion (send, receive pair)
- `red` - race condition
- `blue` - regular node

## Graph naming
Number at the end of the name means unfold level.
- `FULL` - contains full execution tree
- `ONLY_RACES` - contain ony execution paths that lead to race conditions
- `PRUNED` - are similar to full, however the branch stops execution when a race condtition occurs

.png and .svg files with the matching name contain the same graphs.