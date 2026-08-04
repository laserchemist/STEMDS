from lessoncards import *


table_intro = Lesson(
    "table_intro",
    "Introduction to Tables",
    "Tables",
    [
        Card(
            Row(
    
                Image(
                    "table_example0.png",
                    width=250
                ),
    
                Column(
                    Heading("What is a Table?"),
                    Text("A table is a way of storing and organizing data, much like lists, arrays, and strings. It consists of a grid, much like those you would find and make in Excel."),
        
                    Note("The tables we will work with in this course are from the **datascience** module, so if the Tables aren't showing, try running the following code."),
        
                    Code("from datascience import *")
                ),

                widths = [1, 1]
                
            )
        ),

        Card(
            Row(
    
                Column(
                    Heading("What are Observations and Descriptors?"),
                    Text("The rows and columns of a Table very often serve specific purposes in organizing data. For example, suppose we are studying apples. We find one apple with the following qualities:"),
                    
                    BulletList("It is a Honeycrisp", "Its color is Red", "It weighs 150 grams", "Its price is $0.90"), 
                    
                    Text("That apple we studied is what scientists call an **observation**, and the qualities we looked at, like its color and price, are its **descriptors**.")
                ),

                Image(
                    "applestock.jpg",
                    width = 300
                ),

                widths = [2, 1]
                
            )
        ),

        Card(
            Row(
    
                Column(
                    Heading("How are Observations and Descriptors arranged in tables?"),
                    
                    Text("In a typical table, each observation is one row. So, in the table to the right, each row is one apple. (The row we studied in the last slide is highlighted in blue.)"),
                    
                    Text("In contrast, each descriptor is one column. You can see that all the colors are in their designated column, and so are the types, weights, and prices."),

                    Text("Each column is topped by a bold text called a **header**. This is treated as separate from the column.")
                ),

                Image(
                    "table_example1.png",
                    width = 300
                ),

                widths = [1, 1]
                
            )
        ),

        Card(
            
            Heading("Why do we use tables?"),
            
            Text("The appeal of tables lies in their ability to keep information organized. All of the information in a single row will stay within that row, but we still have the flexibility to get all sorts of information from it.\n\n"),
            
            Text("Furthermore, the datascience module allows us to read .csv datasets as Tables. Since these datasets typically reach to the hundreds or thousands of rows, we can very easily bring in a whole world of data with just a few lines of code.\n\n"),

            Text("And perhaps best of all, the table functions/methods that you'll learn follow a common pattern that, if you internalize it, will make your life so much easier.")
        )
    ]
)

table_creation = Lesson(
    "table_creation",
    "Making Tables",
    "Tables",
    [
        Card(
            Row(
                Column(
                    Heading("Making Tables Manually"),
        
                    Text("If we have several lists or arrays, we can combine them into a table, where each list/array becomes one column. This is done via the code to the right."),
    
                    Text("`Table().with_columns` creates a new table. By storing it in a variable (such as `newTable`), we can access that table later by calling the variable."),
    
                    Warning("Each list/array that you put in a table **must** have the same number of terms.")
                ),
                Column(

                    Note("The code below will generate a table with **two** columns, one for each array. If you'd like to add more than two, simply continue the pattern of alternating the header and array."),
                    
                    Code(
                        """
                        newTable = Table().with_columns(
                            "header1", array1,
                            "header2", array2
                        )
                        """)
                
                )
            )
        ),

        Card(

            Heading("Loading Tables from a CSV file"),
            Row(
                Column(
        
                    Text("If we want to load a .csv file, we will instead use `Table.read_table`. The argument here is the file name (including the '.csv' at the end) as a string."),
    
                    Note(
                        "The file must be accessible from your Jupyter notebook. "
                        "For beginners, the easiest solution is putting the CSV file "
                        "in the same folder as your Jupyter notebook."
                    )
                ),
                Column(

                    Note("Much like `Table().with_columns`, we can store the loaded dataset in a variable, like `newTable`."),
                    
                    Code(
                        """
                        newTable = Table.read_table(
                            'filename.csv'
                        )
                        """)
                
                ),

                widths = [1, 1]
            )
        ),

        Card(

            Heading("Example using the `apples` table"),

            Row(
                Text("Manually (assuming `types`, `colors`, `weights`, and `prices` are all arrays):"),

                Text("From a CSV file (assuming `apple_data.csv` is the file name):"),
            ),

            Row(
                Code(
                    """
                    apples = Table().with_columns(
                        "Type", types,
                        "Color", colors,
                        "Weight (g)", weights,
                        "Price ($)", prices
                    )
                    """),

                Code(
                    """
                    apples = Table.read_table(
                        'apple_data.csv'
                    )
                    """),

                widths = [1, 1]
            )
        )
    ]
)

table_method = Lesson(
    "table_method",
    "Table Methods",
    "Tables",
    [

        Card(
            Heading("The Basic Structure of Table methods"),

            Text("Beyond creating/loading a new table, all subsequent table methods will be some alteration/transformation to an existing table. So, all of these methods will have the same general structure. This consists of three parts."),

            BulletList("The existing table that you are altering (in green)", "The name of the method (blue)", "Any arguments that it needs (red)"),

            Text("This sample below showsan example of `.column`, which you will be formally introduced to later."),

            Image("example_method.png")
        ),

        Card(
            Heading("Perserving Modifications to Tables"),

            Text("While we often say that these methods *modify* the table, that is not strictly true. Instead, these methods **create a version of the table** with these modifications, but the actual table is not changed."),

            Text("You need to set a variable equal to that code in order to store whatever changes you make."),

            Row(

                Column(
                    Text("This Code creates a modified version of the table `apples`, but since that version is not stored in a variable, you can't use it further."),
                    Code("apples.sort('Color')")
                ),

                Column(
                    Text("This Code creates a modified version of the table `apples`, AND it stores that version in the variable `stored_apples`. We can use `stored_apples` for future code."),

                    Code("stored_apples = apples.sort('Color')")
                ),

                widths = [1, 1]
            )
        ),

        Card(
            Heading("How to refer to Table columns"),

            Text("Most of the methods you'll learn involve a column in some way, like selecting columns, sorting by a column, extracting columns, and so forth. You can use one of two ways to specify which column to use."),

            Row(

                Column(
                    Text("You can refer to the column's header. This requires you to surround that header in quotes."),
                    Code("apples.sort('Color')"),
                    
                    Text("Alternatively, you can refer to its index. This is an integer that describes where on the table the column is. The leftmost column is index 0, and it increases for each column to the right."),

                    Code("apples.sort(1)")
                ),

                Column(
                    Image("table_example0.png")
                ),

                widths = [1, 1]
            )
        )
    ]
)
        
table_column = Lesson(
    "table_column",
    "Extracting Information from Tables",
    "Tables",
    [
        Card(
            Heading("How to Extract a Column as an Array"),

            Text("The main way we extract any sort of information from a table is by extracting the relevant column as an array. It is in this array format (which you learned in lab 2) that you can use all sorts of statistical functions to evaluate the data."),

            Text("A column can be extracted by one of two ways below."),

            Row(
                Code("table.column('header')"),

                Code("table['header']"),

                widths = [1, 1]
            ),

            Text("For clarity, the examples in this card will use the leftmost method, but they can still be achieved with the other.")
        ),

        Card(

            Row(
                Column(

                    Heading("How to get the value of a particular cell"),

                    Text("Once you extract a column as an array, the many tools that you can use with arrays are at your disposal. One of these is, of course, the Index."),
                    Text("Suppose you would like to extract just the `170` in the table to the right. You know that it is located in the fifth row (starting from 0), in the `Weight (g)` column.")
                ),

                Image("table_example0.png"),

                widths = [2, 1]
            ),

            Text("Your first step is always to extract the relevant column as an array."),

            Code("apples.column('Weight (g)')"),

            Code("array([150, 140, 165, 175, 145, 170, 155, 180, 168, 150])"),

            Code("Index:  0    1    2    3    4    5    6    7    8    9   "),

            Text("\nSo, to get the fifth element in this array, we just add to the end the index notation."),

            Code("apples.column('Weight (g)')[5]"),

            Code("170")

        ),

        Card(
            Heading("How to use statistical functions on a table column"),

            Text("As you'll soon realize, being able to find such qualities like the maximum, minimum, and mean values in a certain table column is very useful. However, almost all of these functions will NOT accept tables, but rather arrays."),

            Text("As you will have guessed, we need to extract the relevant column as an array."),

            Code("apples.column('Weight (g)')"),

            Code("array([150, 140, 165, 175, 145, 170, 155, 180, 168, 150])"),

            Text("\nThen, we can use any statistical function we want on this array!"),

            Code("max(apples.column('Weight (g)')"),

            Code("180")
        )
    ]
)

                    


                

                    

table_sort = Lesson(
    "table_sort",
    "Sorting Tables",
    "Tables",
    [
        Card(
            Heading("How to Sort a Table"),

            Text("Remember that almost all methods, including sorting, will **not** alter what is in a table row. So, when we refer to 'sorting a table', it will almost always mean sorting the **rows**."),

            Note("This form sorts from **smallest** to **largest** (or, if the column is made of strings, from **a** to **z**). That means he smallest-valued rows are at the top."),
            
            Code(
                """
                table.sort('header')
                """)
        ),

        Card(
            Column(
                Heading("How to Sort in the Opposite Direction"),
    
                Text("This is remarkably similar to the previous form; all you need to do is add another argument."),

                Code("table.sort('header', descending = True)")
            )
        ),

        Card(
            Heading('Examples using the `apples` table'),

            Row(
                Column(
                    Text('Original Data (`apples`)')
                ),

                Column(
                    Code("apples.sort('Weight (g)')")
                ),

                Column(
                    Code("apples.sort('Weight (g)', descending = True)")
                ),

                widths = [1, 1, 1]
            ),

            Row(

                Image('table_example0.png'),
                
                Image("sorted_table1.png"),

                Image("sorted_table2.png"),

                widths = [1, 1, 1]
            ),

            Row(

                Text("No ordering in the Weights"),

                Text("Smallest Weights first"),

                Text("Largest Weights first"),

                widths = [1, 1, 1]
                
            ),

            Text("Remember, you can use this sorted table as the basis for future methods. For example, this is a superb way to get the `Type` for the lightest or heaviest apple.")
        )
    ]
)