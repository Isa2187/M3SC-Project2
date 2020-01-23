# M3SC-Project2
Second project of Scientific Computation (M3SC) module taken in 3rd year. (Grade = 100%)

All  code was done in Python, and further details of the task can be found in the folder Project_Files.

The basis of this project was to organise a prouction line, whereby a set of jobs needed completing. Some jobs were dependent on others e.g. job 4 could only be done after job 1 was completed, so I had to first find the shortest amount of time that would be required to complete all jobs whilst respecting the job dependencies. This was done using a variation of the Bellman-Ford algorithm, which was applied to a network representing each job's completion times as well as any dependencies.

Having minimised the total time taken, I then had to identify how best to organise the jobs between parallel production lines. I visually produced a production line in the form of a Gantt chart, which showed how to minimise the number of production lines so that jobs could be completed simultaneously whilst still respecting job dependencies.
