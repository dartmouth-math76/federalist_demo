
# A list of the disputed papers (1-based indexing)
disputed_papers =  [49,50,51,52,53,54,55,56,57,58,62,63]


def LoadPapers():
    """ 
        This function loads the federalist paper texts from a text file downloaded
        from Project Gutenberg and then seperates the text into the individual
        federalist papers.  The papers are then cleaned and the title, author, and text are
        extracted.  These are stored in a dictionary with keys 'Title', 'Author', and 'Text'
        
        RETURNS:
            list(dict): A list of dictionary objects.  The list contains one entry for
                        each paper and the dictionary has entries ['Title','Author','Text','Length']
                        containing the corresponding information. 
    """
    
    with open('FederalistPapers.txt', 'r') as fin:
        all_text = fin.read()
        
    papers = all_text.split('To the People of the State of New York:')
    all_data = []
    
    for i in range(1,len(papers)):
        #title = prev_parts
        if i in disputed_papers:
            author = 'DISPUTED'
        else:
            author = papers[i-1].strip().split('\n')[-1].strip()
        
        parts = papers[i-1].split('FEDERALIST')[-1].replace('\n\n','\n').split('\n')
        parts = list(filter(lambda a: a != '\r', parts))
       
        if('Same Subject Continued' in parts[1]):
            title = parts[2].strip()
        else:
            title = parts[1].strip()
            
        text = papers[i].split('PUBLIUS')[0].strip().replace('\n',' ').replace('\r','')
        num_words = len(text.split())
        all_data.append({'Title': title, 'Author': author, 'Text':text, 'Length':num_words, 'ID':i})
        
    return all_data


def ExtractSegments(combined_text):
    """
    Generates equal length segments of the combined text for a single author.
    """
    
    # Number of words in a segment
    seg_length = 200
    
    # Will hold a list of all segments
    all_segs = []
    
    # Split up the text to find all the words
    all_words = combined_text.split(' ')
    num_words = len(all_words)
    
    # Extract the segments
    i = 0
    while(i+seg_length<num_words):
        all_segs.append( ' '.join(all_words[i:i+seg_length]) )
        
        i += seg_length
        
    return all_segs
        
def GenerateSegmentData(all_papers, words_of_interest):
    
    # First, combine all the jay papers, all the madison papers, and all the hamilton papers
    jays = ''
    hamiltons = ''
    madisons = ''
    
    for paper in all_papers:
        if(paper['Author']=='JAY'):
            jays += ' ' + paper['Text']
        elif(paper['Author']=='MADISON'):
            madisons += ' ' + paper['Text']
        elif(paper['Author']=='HAMILTON'):
            hamiltons += ' ' + paper['Text']
       
    # Split each text into segments of 200 words
    jay_segs = ExtractSegments(jays)
    mad_segs = ExtractSegments(madisons)
    ham_segs = ExtractSegments(hamiltons)
    
    # Count the words in each segments
    jay_counts = dict()
    mad_counts = dict()
    ham_counts = dict()
    for word in words_of_interest:
        jay_counts[word] = [seg.count(word) for seg in jay_segs]
        mad_counts[word] = [seg.count(word) for seg in mad_segs]
        ham_counts[word] = [seg.count(word) for seg in ham_segs]
        
    return jay_counts, mad_counts, ham_counts

    
def CountWords(all_papers, words_of_interest):
    """ Given the list of information for each federalist paper returned by
        the LoadPapers function, this function counts the number of occurences
        of each word in in the words_of_interest argument.  The counts are added
        to the dictionaries in all_papers.
    """
    
    for paper_dict in all_papers:
        for word in words_of_interest:
            paper_dict[word + '_count'] = paper_dict['Text'].count(word)
    
    return all_papers

def WriteSegmentCSV(counts, filename):
    """
    Writes the output of the GenerateSegmentData for a single author to a CSV file.
    """
    keys = counts.keys()
    num_segments = len(counts[keys[0]])
    
    # Open the file
    with open(filename, 'w') as fout:
    
        # Write the header 
        fout.write(keys[0])
        for key in keys[1:]:
            fout.write(','+key)
        fout.write('\n')
        
        # Write the counts
        for i in range(num_segments):
            fout.write(str(counts[keys[0]][i]))
            for key in keys[1:]:
                fout.write(',' + str(counts[key][i]))
            fout.write('\n')
            
    
def WriteCSV(all_papers, filename):
    """
    Writes the list of 
    """
    
    keys = list(all_papers[0].keys())
    keys.remove('Text')
    keys.remove('Title')
    
    with open(filename,'w') as fout:
        
        # Write the header line
        fout.write(','.join(keys) + '\n')
        
        for i in range(len(all_papers)):
            fout.write( all_papers[i][keys[0]] ) 
            for key in keys[1:]:
                fout.write( ','+str(all_papers[i][key]))
            fout.write('\n')
            
        
    
# Load the Federalist papers from the Gutenberg project text.
papers = LoadPapers()

# Count the occurrence of certain words in the papers
words = ['by','from','to','upon']
papers = CountWords(papers, words)

# Extract 200 word segments from each author and count the words
jay_cnts, mad_cnts, ham_cnts = GenerateSegmentData(papers, words)
WriteSegmentCSV(jay_cnts, 'JayWordCounts.csv')
WriteSegmentCSV(mad_cnts, 'MadisonWordCounts.csv')
WriteSegmentCSV(ham_cnts, 'HamiltonWordCounts.csv')

# Write the results (not including the text) to a CSV file
filename = 'PaperWordCounts.csv'
WriteCSV(papers, filename)    
    
    