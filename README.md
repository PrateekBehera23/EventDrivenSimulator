# Team
  _Prateek Behera (UFID:16723280) and Anjali Baheti (UFID: 21538534)_

# Install requirements
Python 3.8.3 is required
pip install matplotlib==3.3.4
pip install pandas==1.2.4
pip install scipy==1.6.1
pip install numpy==1.20.1

# How to modify input parameters:
Modify the value of input in the input file. An input file containing the following values has been used to change the constants.
  ## -----Sample Input------
Cache_Replacement_Policy = LRU
Number_Of_Files = 10000
Total_No_Of_Requests = 30000
File_Request_Rate = 10.0
Network_Bandwidth = 100
Access_Link_Bandwidth = 15
Pareto_Alpha = 2
Cache_Capacity = 200
Max_Time = 600
Cache_Check_Time = 0.4

# How to Run code:
  ## Format for executing simulation:
  python main.py input seed

  ## positional arguments:
    input       Input text file containing parameters to simulate from
    seed        Seed to carry out simulation

  ## optional arguments:
    -h, --help  for displaying help message

  ## Example command:
  python main.py input 2

# How to read outputs:
Outputs will be printed out and Scatter plots will be saved.