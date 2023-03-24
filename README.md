# Wikipedia Search Engine

The goal of this project is to build a functional index for a 90GB Wikipedia dump, which will be used to implement an inverted indexing mechanism over this extensive corpus. Additionally, the system is be equipped with a querying mechanism that can efficiently retrieve relevant Wikipedia page titles in response to plain or field queries. The relevancy of the output titles is ranked using a sophisticated ranking mechanism.



### Index Creation
- Index is made up to of 2 types - Primary and Secondary Index

#### Primary Index
- Primary Index is in final folder inside the index directory
- Primary Index consists of all unique words sorted in ascending order and split into multiple files
- After Each words there are batch entries of the format (batch_number: list of 6 values)
- These list of 6 values are file seek pointer for each category like title,infobox,references,etc
- The batch number denotes the file number to look into for each word in main index folder
- There is title primary index which consists of (batch_number: seek_offset token_count) where token count is the total token counts in the page

#### Secondary Index
- There 6 types of files for each category which have multiple batches
- In each file, each line is an unique word the contents of the line are of the format (title_id:frequency)
- These occurrences are seperated by commas and can be used to extract all documents containing the particular word in respective category
- There are title indexes which store the title name for each page/document which can be accessed via primary title index

### Code Base
The code is divided into following parts
1. index.py - creates the whole index structure as specified above by parsing the dump and stores the contents in the index folder
2. preprocessing.py - contains regex and tokenizers to parse the dump and preprocess the string before creating the index
3. dict_to_text.py - it converts the dictionary stored in pickle files to text format for efficient access and usage
4. merge.py - it merges all the primary index files and sort it in the ascending order for efficient access and usage
5. split.py - it splits the single large file obtained from merge.py into multiple smaller chunks and also stored the first word for each chunk for binary search to improve search efficiency
6. search.py - it searched the index and gives results based on the search query inserted as input using primary and secondary index for searching

### Searching Mechanism
- Searching for documents in index is done within few seconds
- It used of TF-IDF scores of query words along with the statistic model to rank the documents
- Wikipedia articles are divided into 6 peices namely Title, Body, Infobox, Category, External Links and Reference 
- Each section has been given some score based on its importance and statistical model these score into account while ranking the documents.


### Instructions to run the code files
- Create a new python virtual env
- Install requirements required to run the code
`pip install -r requirements.txt`
- For index creation run index.py file. Provide following arguments
    1. Data dump absoulute path
    2. Index folder path where index is to be created
    3. Inverted stat file path where is stat file is to be generated
- For quering and retrieveing wikipedia articles based on input queries, run search.py while providing following arguments
    1. queries.txt file path where all the user queries are stored