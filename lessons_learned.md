# Lessons learned


|What went well?|How could it be improved?|
|-|-|
|HDF5 worked quite well as a data format for measurement data. </br> Although the parsing process created an overhead which was time-consuming|Maybe use a relational database mapping lib like SQLAlchemy. And then search an already existing tool (or create one if necessary) to parse data from SQLite (or similar) to hdf5. The database is easy to parse and the hdf5 file remains easy to read by a human|
|The usage of tmux sessions was very helpful while starting and constructing experiment scripts. Although was bugs occurred because the wasn't very familiar tmux|More experience. Knowledge gained through this project will help to not certain bugs in the future|

|What went wrong?|How could it be improved or avoided next time?|
|-|-|
|The creation of diagrams with python scripts was very slow. This was due to the fact that statistics were recomputed from anew each time the diagram was rendered|The creation of stats and diagrams should be separated in the software architecture. This may create some code overhead. But it will be more efficient in terms of computing time.|
|Missing tests. This was due to time pressure but also because bash scripts are not as easy to test as python scripts|Bash scripts should be broken down into smaller bash scripts. These are then easier to test|
|Time problems and planning difficulties. This was probably mostly due to a lack of experience.|More experience but also milestones and intermediate deadlines and milestones. Although the latter can only be set correctly with enough experience.|