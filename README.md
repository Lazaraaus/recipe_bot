# Assignment 3: Conversational Interface

## How to run Rasa Conversation Engine
- In a terminal window run `rasa run actions` inside your virtual env
- In a separate window run `rasa train` inside your virtual env. Then run `rasa shell` to converse w/ the bot. 

### A Note About Python and Rasa
Rasa only works for Python 3.7 and 3.8. If you don't have one of those versions of Python installed on your machine, you will need to install them. Once you install a correct version of Python, you should set up a virtual environtment using that version. To do so, simply navigate to the recipe_bot project folder and type `virtualenv -p=<path/to/python3.7|python3.8> <path/to/new/venv>`. Finally, in both terminal windows that you will be using (one for the server and one for the shell), activate the virtual environment by typing `source [name-of-venv]/bin/activate`. Only once you're running a virtual environment with the correct version of Python in at least one of the terminals should you install the requirements by typing `pip install -r requirements.txt` or `pip3 install -r requirements.txt`.



# Assignment 2: Recipe Parser & Interactive Cookbook
#### Written by: Aaron Cooper, Macey Goldstein, & Yjaden Wood

## How to Run This Project
In order to run the project, you need to download and navigate to the project directory. From there, optionally activate a virtual environment and then install the necessary libraries by running `pip install -r requirements.txt` or `pip3 install -r requirements.txt`.

## Project Parameters
To run the project in the project directory, run the `python3 parser.py [transformation] [output] [url]` command. Below are more details about each of the parameters.
- `transformation`: Describes what transformation to perform on the input recipe. The options for this parameter are:
    - `none`: Outputs the parsed recipe with no transformations.
    - `vegetarian`: Outputs a vegetarian version of the recipe.
    - `italian`: Outputs an Italian-cuisine version of the recipe.
    - `halved`: Outputs a version of the recipe that yields half the amount.
    - `doubled`: Outputs a version of the recipe that yields twice the amount.
    - `unvegetarian`: Outputs a non-vegetarian version of the recipe
    - `unhealthy`: Outputs an unhealthier version of the recipe
    - `healthy`: Outputs a healthier version of the recipe

- `output`: Lists the path to an output file to which the human-readable recipe will be written. If you would like a look at the internal representation of the parsed recipe (before transformations) instead, you may use `cmd` as the value for this parameter and it will print that internal representation to the command line.
- `url`: The URL of the input recipe from www.allrecipes.com.